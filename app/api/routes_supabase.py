"""REST API endpoints for Supabase Cloud Storage & Database Persistence."""
from typing import Optional, List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.services import supabase_service

router = APIRouter(prefix="/api/supabase", tags=["Supabase Cloud Persistence"])


class CloudBackupResponse(BaseModel):
    status: str
    archive_path: Optional[str] = None
    latest_path: Optional[str] = None
    timestamp: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@router.get("/status")
def get_supabase_status():
    """Returns the operational status, configuration check, and storage buckets in Supabase."""
    return supabase_service.get_status()


@router.post("/backup", response_model=Dict[str, Any])
def trigger_cloud_backup():
    """Takes a verified snapshot of SQLite database and uploads it to Supabase Cloud Storage."""
    result = supabase_service.backup_database_to_cloud()
    if not result:
        raise HTTPException(status_code=500, detail="Failed to complete cloud backup to Supabase.")
    return result


@router.post("/restore")
def trigger_cloud_restore(remote_path: str = "backups/latest.db"):
    """Restores local database from a Supabase cloud snapshot with path traversal defense."""
    safe_remote = Path(remote_path).as_posix().lstrip("/")
    if ".." in safe_remote or not safe_remote.endswith(".db"):
        raise HTTPException(status_code=400, detail="Invalid cloud backup path.")
    success = supabase_service.restore_database_from_cloud(remote_path=safe_remote)
    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restore database from Supabase cloud path '{safe_remote}'"
        )
    return {"message": f"Database successfully restored from Supabase snapshot '{safe_remote}'"}


@router.get("/files")
def list_cloud_files(folder: str = ""):
    """Lists files in the target Supabase storage bucket."""
    return supabase_service.list_files(folder=folder)


@router.post("/upload")
async def upload_file_to_supabase(
    file: UploadFile = File(...),
    folder: str = Form("uploads")
):
    """Uploads any file (PDF, report, image) directly to Supabase Cloud Storage."""
    import tempfile
    from pathlib import Path

    safe_filename = Path(file.filename or "upload.bin").name
    clean_folder = folder.strip("/").strip().replace("..", "").replace("\\", "/")
    clean_folder = "/".join(part for part in clean_folder.split("/") if part and part != ".")
    dest_path = f"{clean_folder}/{safe_filename}" if clean_folder else safe_filename

    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{safe_filename}") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = Path(tmp.name)

    try:
        res = supabase_service.upload_file(
            file_path=tmp_path,
            destination_path=dest_path,
            content_type=file.content_type
        )
        if not res:
            raise HTTPException(status_code=500, detail="Failed to upload file to Supabase")
        return res
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass

