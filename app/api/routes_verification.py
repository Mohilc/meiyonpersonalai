"""FastAPI Routes for EmailAI Verification RAG.

Endpoints:
- POST /api/verification/sync-drive : Manual trigger to pull docs from Google Drive & update Supabase pgvector.
- POST /api/verification/verify     : Fast live message verification test endpoint.
- GET  /api/verification/status     : Health, stats, and vector count.
"""
import os
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Header, Query, status
from pydantic import BaseModel, Field

from app.config import settings
from app.services import verification_rag

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/verification", tags=["Verification RAG"])


class SyncDriveRequest(BaseModel):
    folder_id: Optional[str] = Field(None, description="Optional override for Google Drive folder ID")


class VerificationRequest(BaseModel):
    sender_email: str = Field(..., description="Email address of the sender")
    domain: Optional[str] = Field(None, description="Optional domain extracted from sender or link")
    message_text: Optional[str] = Field(None, description="Message body or snippet to inspect for phishing")
    source_platform: str = Field("Email", description="Originating channel: 'Email' or 'LinkedIn'")


class VerificationResponse(BaseModel):
    matched_entities: List[str] = Field(default_factory=list)
    domain_trust_signals: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)
    confidence_score: float = Field(0.0)
    source_platform: str = "Email"
    elapsed_ms: float = 0.0


def _check_sync_authorization(x_sync_secret: Optional[str] = Header(None), secret: Optional[str] = Query(None)):
    """Verifies that the caller has provided the correct sync secret if configured."""
    expected_secret = getattr(settings, "VERIFICATION_SYNC_SECRET", "") or os.environ.get("VERIFICATION_SYNC_SECRET", "").strip()
    if expected_secret:
        provided = x_sync_secret or secret
        if provided != expected_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: Invalid or missing verification sync secret."
            )


@router.post("/sync-drive", summary="Trigger Google Drive Document Sync & pgvector Upsert")
def sync_drive(
    req: Optional[SyncDriveRequest] = None,
    x_sync_secret: Optional[str] = Header(None),
    secret: Optional[str] = Query(None)
):
    """
    On-demand indexing trigger.
    Reads verified allowlists, recruiter directories, and scam patterns from Google Drive
    and incrementally upserts them into the Supabase pgvector store.
    
    Protected via VERIFICATION_SYNC_SECRET.
    """
    _check_sync_authorization(x_sync_secret, secret)
    folder_id = req.folder_id if req else None

    logger.info("Initiating manual verification sync from Google Drive...")
    try:
        res = verification_rag.sync_drive_documents(folder_id=folder_id)
        return {
            "success": True,
            "message": "Google Drive verification documents indexed successfully.",
            "details": res
        }
    except Exception as e:
        logger.error("Error during verification sync: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.post("/verify", response_model=VerificationResponse, summary="Fast Live Message Verification")
def verify_message(req: VerificationRequest):
    """
    Fast live sender verification tool.
    Queries ONLY the Supabase pgvector index (never Google Drive live).
    Evaluates enterprise ATS allowlists, recruiter directories, and known scam patterns.
    """
    result = verification_rag.verify_sender_context(
        sender_email=req.sender_email,
        domain=req.domain,
        message_text=req.message_text,
        source_platform=req.source_platform
    )
    return VerificationResponse(**result)


@router.get("/status", summary="Verification Index Telemetry & Status")
def verification_status():
    """Returns current vector count, Supabase pgvector connection state, and cache statistics."""
    stats = verification_rag.get_index_stats()
    return {
        "service": "EmailAI Verification RAG",
        "status": "ONLINE",
        "telemetry": stats
    }
