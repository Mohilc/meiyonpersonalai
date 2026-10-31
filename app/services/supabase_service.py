"""Supabase Cloud Storage & Database Persistence Service.

Provides secure, resilient integration with Supabase for:
1. Cloud File Storage (PDF attendance reports, marksheets, resumes, media).
2. Cloud Database Snapshots & Persistence (automated cloud backups of SQLite state).
3. Cloud Recovery on stateless deployments (e.g., Render free-tier restarts).
4. Direct REST & Storage APIs with automatic fallback.
"""
import os
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Union

import httpx
from app.config import settings, DATA_DIR
from app.database import backup_database, restore_database

logger = logging.getLogger(__name__)

# Cached Supabase client
_supabase_client = None


def is_configured() -> bool:
    """Checks whether Supabase URL and API Key are configured."""
    return bool(settings.SUPABASE_URL and settings.SUPABASE_KEY)


def get_client():
    """Initializes and returns the official Supabase Client if configured."""
    global _supabase_client
    if not is_configured():
        return None

    if _supabase_client is not None:
        return _supabase_client

    try:
        from supabase import create_client
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        return _supabase_client
    except Exception as e:
        logger.error("Failed to initialize Supabase client: %s", str(e))
        return None


def get_headers() -> Dict[str, str]:
    """Returns authorization headers for direct Supabase HTTP REST/Storage calls."""
    key = settings.SUPABASE_KEY or ""
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }


def ensure_bucket(bucket_name: Optional[str] = None, is_public: bool = True) -> bool:
    """
    Verifies that the target storage bucket exists in Supabase.
    If it doesn't exist, attempts to create it.
    """
    if not is_configured():
        logger.warning("Supabase is not configured; skipping ensure_bucket.")
        return False

    target_bucket = bucket_name or settings.SUPABASE_STORAGE_BUCKET
    client = get_client()

    if client:
        try:
            buckets = client.storage.list_buckets()
            existing_names = [b.name for b in buckets] if hasattr(buckets[0] if buckets else None, 'name') else [b.get('name') for b in buckets]
            if target_bucket in existing_names:
                return True

            # Attempt creation
            client.storage.create_bucket(target_bucket, options={"public": is_public})
            logger.info("Created Supabase storage bucket '%s' (public=%s)", target_bucket, is_public)
            return True
        except Exception as e:
            logger.warning("Supabase SDK create_bucket notice: %s. Checking via HTTP...", str(e))

    # HTTP Fallback
    try:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/bucket"
        with httpx.Client(timeout=10.0) as http_client:
            resp = http_client.get(url, headers=get_headers())
            if resp.status_code == 200:
                buckets_data = resp.json()
                if any(b.get("name") == target_bucket or b.get("id") == target_bucket for b in buckets_data):
                    return True

            # Try POST to create bucket
            create_resp = http_client.post(
                url,
                headers={**get_headers(), "Content-Type": "application/json"},
                json={"id": target_bucket, "name": target_bucket, "public": is_public}
            )
            return create_resp.status_code in (200, 201)
    except Exception as err:
        logger.error("Failed to verify/create Supabase bucket: %s", str(err))
        return False


def upload_file(
    file_path: Union[str, Path],
    destination_path: Optional[str] = None,
    bucket_name: Optional[str] = None,
    content_type: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Uploads a local file to Supabase Cloud Storage.
    Returns metadata including public URL, cloud path, and upload timestamp.
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        logger.error("Cannot upload to Supabase: file not found at %s", str(path_obj))
        return None

    if not is_configured():
        logger.info("Supabase credentials not configured. Simulating local storage for %s", path_obj.name)
        return {
            "bucket": bucket_name or settings.SUPABASE_STORAGE_BUCKET,
            "path": destination_path or path_obj.name,
            "public_url": f"/static/reports/{path_obj.name}",
            "size_bytes": path_obj.stat().st_size,
            "simulated": True,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }

    target_bucket = bucket_name or settings.SUPABASE_STORAGE_BUCKET
    dest_path = (destination_path or path_obj.name).lstrip("/")
    mime = content_type or _detect_content_type(path_obj.name)

    client = get_client()
    try:
        file_bytes = path_obj.read_bytes()

        if client:
            try:
                # Use storage upload with upsert=True
                client.storage.from_(target_bucket).upload(
                    path=dest_path,
                    file=file_bytes,
                    file_options={"content-type": mime, "upsert": "true"}
                )
                public_url = client.storage.from_(target_bucket).get_public_url(dest_path)
                return {
                    "bucket": target_bucket,
                    "path": dest_path,
                    "public_url": public_url,
                    "size_bytes": len(file_bytes),
                    "simulated": False,
                    "uploaded_at": datetime.now(timezone.utc).isoformat()
                }
            except Exception as sdk_err:
                logger.warning("Supabase SDK upload failed (%s), attempting HTTP upload...", str(sdk_err))

        # Direct HTTP upload fallback
        upload_url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/{target_bucket}/{dest_path}"
        headers = {
            **get_headers(),
            "Content-Type": mime,
            "x-upsert": "true"
        }
        with httpx.Client(timeout=30.0) as http_client:
            resp = http_client.post(upload_url, headers=headers, content=file_bytes)
            if resp.status_code in (200, 201):
                public_url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/public/{target_bucket}/{dest_path}"
                return {
                    "bucket": target_bucket,
                    "path": dest_path,
                    "public_url": public_url,
                    "size_bytes": len(file_bytes),
                    "simulated": False,
                    "uploaded_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                logger.error("Supabase HTTP upload failed with status %d: %s", resp.status_code, resp.text)
                return None
    except Exception as e:
        logger.error("Exception uploading file to Supabase: %s", str(e))
        return None


def download_file(
    remote_path: str,
    local_destination: Union[str, Path],
    bucket_name: Optional[str] = None
) -> bool:
    """Downloads a file from Supabase Storage to the local disk."""
    if not is_configured():
        logger.warning("Supabase not configured, cannot download %s", remote_path)
        return False

    target_bucket = bucket_name or settings.SUPABASE_STORAGE_BUCKET
    dest_path = Path(local_destination)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    clean_remote = remote_path.lstrip("/")

    client = get_client()
    try:
        if client:
            try:
                res_bytes = client.storage.from_(target_bucket).download(clean_remote)
                dest_path.write_bytes(res_bytes)
                logger.info("Downloaded %s from Supabase to %s", clean_remote, str(dest_path))
                return True
            except Exception as sdk_err:
                logger.warning("SDK download failed (%s), falling back to HTTP...", str(sdk_err))

        # Direct HTTP download
        download_url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/{target_bucket}/{clean_remote}"
        with httpx.Client(timeout=30.0) as http_client:
            resp = http_client.get(download_url, headers=get_headers())
            if resp.status_code == 200:
                dest_path.write_bytes(resp.content)
                logger.info("HTTP downloaded %s from Supabase to %s", clean_remote, str(dest_path))
                return True
            else:
                logger.error("HTTP download failed: %d %s", resp.status_code, resp.text)
                return False
    except Exception as e:
        logger.error("Exception downloading file from Supabase: %s", str(e))
        return False


def list_files(folder: str = "", bucket_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lists objects in the target Supabase Storage bucket."""
    if not is_configured():
        return []

    target_bucket = bucket_name or settings.SUPABASE_STORAGE_BUCKET
    client = get_client()
    try:
        if client:
            try:
                items = client.storage.from_(target_bucket).list(folder)
                return [i if isinstance(i, dict) else i.__dict__ for i in items]
            except Exception as sdk_err:
                logger.warning("SDK list failed (%s), falling back to HTTP...", str(sdk_err))

        url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/list/{target_bucket}"
        headers = {**get_headers(), "Content-Type": "application/json"}
        with httpx.Client(timeout=15.0) as http_client:
            resp = http_client.post(url, headers=headers, json={"prefix": folder, "limit": 100})
            if resp.status_code == 200:
                return resp.json()
            return []
    except Exception as e:
        logger.error("Failed to list Supabase files: %s", str(e))
        return []


def backup_database_to_cloud(bucket_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Creates a consistent SQLite snapshot and uploads it to Supabase Storage:
    1. Timestamped archive: `backups/manager_backup_YYYYMMDD_HHMMSS.db`
    2. Pointer snapshot: `backups/latest.db` (for automatic cloud restoration)
    """
    try:
        # Step 1: Create local verified snapshot
        local_backup = backup_database()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_bucket = bucket_name or settings.SUPABASE_STORAGE_BUCKET

        # Step 2: Upload timestamped backup
        archive_path = f"backups/manager_backup_{timestamp}.db"
        archive_res = upload_file(
            file_path=local_backup,
            destination_path=archive_path,
            bucket_name=target_bucket,
            content_type="application/x-sqlite3"
        )

        # Step 3: Upload latest snapshot pointer
        latest_res = upload_file(
            file_path=local_backup,
            destination_path="backups/latest.db",
            bucket_name=target_bucket,
            content_type="application/x-sqlite3"
        )

        logger.info("Successfully backed up SQLite database to Supabase: %s", archive_path)
        return {
            "status": "success",
            "archive_path": archive_path,
            "latest_path": "backups/latest.db",
            "archive_upload": archive_res,
            "latest_upload": latest_res,
            "timestamp": timestamp
        }
    except Exception as e:
        logger.error("Failed to backup database to Supabase: %s", str(e))
        return None


def restore_database_from_cloud(
    bucket_name: Optional[str] = None,
    remote_path: str = "backups/latest.db"
) -> bool:
    """
    Restores the database from a cloud snapshot stored in Supabase.
    Useful for initializing state on new deployment containers or stateless restarts.
    """
    if not is_configured():
        logger.warning("Supabase not configured, cannot restore cloud database.")
        return False

    temp_path = DATA_DIR / "temp_cloud_restore.db"
    try:
        # Download from cloud
        downloaded = download_file(
            remote_path=remote_path,
            local_destination=temp_path,
            bucket_name=bucket_name
        )
        if not downloaded or not temp_path.exists():
            logger.error("Could not download cloud database snapshot from %s", remote_path)
            return False

        # Restore into active SQLite database
        success = restore_database(temp_path)
        if success:
            logger.info("Successfully restored active database from Supabase snapshot: %s", remote_path)
        return success
    except Exception as e:
        logger.error("Exception during Supabase cloud restore: %s", str(e))
        return False
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass


def upload_academic_pdf(pdf_path: str) -> Optional[Dict[str, Any]]:
    """Convenience helper to upload an academic attendance/marksheet PDF to Supabase."""
    p = Path(pdf_path)
    if not p.exists():
        return None
    dest = f"reports/academic/{p.name}"
    return upload_file(file_path=p, destination_path=dest, content_type="application/pdf")


def get_status() -> Dict[str, Any]:
    """Returns diagnostics and connection status for Supabase."""
    configured = is_configured()
    status_info: Dict[str, Any] = {
        "configured": configured,
        "supabase_url": settings.SUPABASE_URL if configured else "Not Set",
        "storage_bucket": settings.SUPABASE_STORAGE_BUCKET,
        "connected": False,
        "buckets": [],
        "error": None
    }

    if not configured:
        status_info["message"] = (
            "Supabase is not yet configured. Please set SUPABASE_URL and SUPABASE_KEY in your environment or .env file."
        )
        return status_info

    try:
        url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/bucket"
        with httpx.Client(timeout=6.0) as http_client:
            resp = http_client.get(url, headers=get_headers())
            if resp.status_code == 200:
                buckets = resp.json()
                status_info["connected"] = True
                status_info["buckets"] = [b.get("name") or b.get("id") for b in buckets]
                status_info["target_bucket_exists"] = settings.SUPABASE_STORAGE_BUCKET in status_info["buckets"]
            else:
                status_info["error"] = f"HTTP {resp.status_code}: {resp.text[:100]}"
    except Exception as e:
        status_info["error"] = str(e)

    return status_info


def _detect_content_type(filename: str) -> str:
    """Simple mime-type detection based on file extension."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "application/pdf"
    if lower.endswith(".db") or lower.endswith(".sqlite"):
        return "application/x-sqlite3"
    if lower.endswith(".json"):
        return "application/json"
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".jpg") or lower.endswith(".jpeg"):
        return "image/jpeg"
    if lower.endswith(".txt") or lower.endswith(".log"):
        return "text/plain"
    return "application/octet-stream"
