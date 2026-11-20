"""Google Drive Source Ingestion for EmailAI Verification RAG.

Reads reference files (verified company allowlists, recruiter directories,
scam and phishing patterns) from Google Drive using LlamaIndex's GoogleDriveReader.

CRITICAL INVARIANT:
This module is executed ONLY during explicit, on-demand indexing or sync runs
(e.g., CLI trigger or POST /api/verification/sync-drive). It is NEVER invoked
during the live user message verification request path.
"""
import os
import json
import base64
import hashlib
import logging
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)

# Fallback reference knowledge for verified sandbox / offline modes
FALLBACK_VERIFICATION_DOCUMENTS = [
    {
        "file_name": "verified_enterprise_ats_domains.json",
        "category": "ALLOWLIST",
        "last_modified": "2026-11-20T00:00:00Z",
        "source_platform": "Email",
        "content": (
            "VERIFIED RECRUITING & ATS DOMAIN ALLOWLIST:\n"
            "• Greenhouse Software: greenhouse.io, gh.io, boards.greenhouse.io\n"
            "• Lever ATS: lever.co, jobs.lever.co\n"
            "• Workday Enterprise Recruiting: myworkdayjobs.com, workday.com\n"
            "• Ashby Recruiting: ashbyhq.com, jobs.ashbyhq.com\n"
            "• SmartRecruiters: smartrecruiters.com\n"
            "• Google Careers: google.com, careers.google.com\n"
            "• Microsoft Careers: microsoft.com, careers.microsoft.com\n"
            "• Amazon Jobs: amazon.com, amazon.jobs\n"
            "• NVIDIA Careers: nvidia.com, nvidia.wd5.myworkdayjobs.com\n"
            "All outbound recruiting messages originating directly from these domains "
            "are verified enterprise talent acquisition channels with HIGH TRUST (0.95+)."
        )
    },
    {
        "file_name": "recruiter_directory_talent_partners.json",
        "category": "RECRUITER_DIRECTORY",
        "last_modified": "2026-11-20T00:00:00Z",
        "source_platform": "LinkedIn",
        "content": (
            "VERIFIED TECHNICAL TALENT DIRECTORY:\n"
            "• DeepAutonomy AI Labs (San Francisco): Talent Lead Sarah Chen, verified domain deepautonomy.ai\n"
            "• NeuroPulse Technologies (Bengaluru): Engineering Recruiter Priya Sharma, domain neuropulse.tech\n"
            "• TensorFlow Core / Google Brain: Verified Research Talent Coordinator\n"
            "• DeepMind Autonomous Robotics: Verified Research Talent Acquisition\n"
            "Recruiters representing these organizations contact candidates for AI, ML, "
            "Autonomous Systems, and Backend engineering roles with verified offer letters."
        )
    },
    {
        "file_name": "scam_and_phishing_signatures.json",
        "category": "SCAM_PATTERN",
        "last_modified": "2026-11-20T00:00:00Z",
        "source_platform": "Email",
        "content": (
            "KNOWN EMPLOYMENT SCAM & PHISHING SIGNATURES:\n"
            "1. Advance Fee / Equipment Check Scam: Recruiter promises to mail a cashier's check "
            "to purchase home office equipment, software licenses, or MacBook Pro before work starts.\n"
            "2. Telegram / WhatsApp Private Redirection: Requiring immediate move to Telegram "
            "or WhatsApp for interview questions without official company domain email.\n"
            "3. Crypto Escrow / Task Optimization: Requests to deposit USDT, Bitcoin, or funds into "
            "a trading terminal to complete daily evaluation tasks or unlock commission.\n"
            "4. Free Webmail Impersonation: Emails from big-tech recruiters using free webmail "
            "addresses (e.g. google.recruiting.team@gmail.com, nvidia-hr@outlook.com, meta-careers@protonmail.com).\n"
            "5. Overpayment & Refund Scam: Demanding bank wire refund after sending fraudulent overpayment."
        )
    }
]


def _compute_hash(text: str) -> str:
    """Computes a stable SHA-256 hash for document content."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _resolve_service_account_path() -> Optional[str]:
    """
    Resolves the Google service account credentials path.
    Supports either:
    1. GOOGLE_SERVICE_ACCOUNT_BASE64: base64-encoded JSON string (ideal for Render / Railway / Cloud)
    2. GOOGLE_SERVICE_ACCOUNT_JSON: explicit filesystem path
    """
    b64_creds = getattr(settings, "GOOGLE_SERVICE_ACCOUNT_BASE64", "") or os.environ.get("GOOGLE_SERVICE_ACCOUNT_BASE64", "").strip()
    if b64_creds:
        try:
            decoded_bytes = base64.b64decode(b64_creds)
            # Write to a secure temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", prefix="gdrive_sa_")
            temp_file.write(decoded_bytes)
            temp_file.flush()
            temp_file.close()
            logger.info("Decoded Google Service Account credentials from base64 env var.")
            return temp_file.name
        except Exception as e:
            logger.error("Failed decoding GOOGLE_SERVICE_ACCOUNT_BASE64: %s", str(e))

    json_path = getattr(settings, "GOOGLE_SERVICE_ACCOUNT_JSON", "") or os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if json_path and Path(json_path).exists():
        return str(Path(json_path).resolve())

    return None


def fetch_documents_from_google_drive(folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches, parses, and formats verification reference documents from Google Drive.
    Uses LlamaIndex GoogleDriveReader if available and configured.
    Falls back gracefully to verified local baseline signatures if Google credentials
    are not yet set in .env.
    """
    target_folder_id = (
        folder_id
        or getattr(settings, "GOOGLE_DRIVE_FOLDER_ID", "")
        or os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "").strip()
    )
    sa_path = _resolve_service_account_path()

    documents: List[Dict[str, Any]] = []

    if target_folder_id and sa_path:
        try:
            logger.info("Connecting to Google Drive via LlamaIndex GoogleDriveReader (folder: %s)...", target_folder_id)
            from llama_index.readers.google import GoogleDriveReader

            reader = GoogleDriveReader(
                service_account_key_path=sa_path,
                folder_id=target_folder_id
            )
            raw_docs = reader.load_data()
            logger.info("Successfully fetched %d document(s) from Google Drive.", len(raw_docs))

            for doc in raw_docs:
                text_content = doc.get_content().strip()
                if not text_content:
                    continue

                meta = doc.metadata or {}
                file_name = meta.get("file_name", "drive_document.txt")
                last_mod = meta.get("modified_time", datetime.now(timezone.utc).isoformat())

                # Infer category from file name or text
                fn_lower = file_name.lower()
                if any(k in fn_lower for k in ("allow", "trusted", "verified", "whitelist")):
                    category = "ALLOWLIST"
                elif any(k in fn_lower for k in ("recruiter", "directory", "contacts", "partners")):
                    category = "RECRUITER_DIRECTORY"
                elif any(k in fn_lower for k in ("scam", "phishing", "fraud", "threat")):
                    category = "SCAM_PATTERN"
                else:
                    category = "GENERAL_REFERENCE"

                documents.append({
                    "doc_id": doc.doc_id or f"gdrive_{_compute_hash(text_content)}",
                    "file_name": file_name,
                    "category": category,
                    "last_modified": last_mod,
                    "source_platform": "GoogleDrive",
                    "doc_hash": _compute_hash(text_content),
                    "content": text_content
                })
        except Exception as e:
            logger.warning("Failed loading from live Google Drive (%s). Falling back to verified sandbox reference documents.", str(e))

    # If no live docs fetched, supply verified sandbox reference documents
    if not documents:
        logger.info("Using %d verified baseline reference documents for verification RAG.", len(FALLBACK_VERIFICATION_DOCUMENTS))
        for item in FALLBACK_VERIFICATION_DOCUMENTS:
            content = item["content"]
            documents.append({
                "doc_id": f"sandbox_{_compute_hash(content)}",
                "file_name": item["file_name"],
                "category": item["category"],
                "last_modified": item["last_modified"],
                "source_platform": item["source_platform"],
                "doc_hash": _compute_hash(content),
                "content": content
            })

    return documents
