"""EmailAI Verification RAG Package.

Combines Google Drive source document ingestion (LlamaIndex GoogleDriveReader)
with Supabase pgvector indexing for sub-millisecond sender and recruiter security verification.
"""
from typing import Optional, Dict, Any, List

from app.services.verification_rag.drive_sync import fetch_documents_from_google_drive
from app.services.verification_rag.vector_index import (
    upsert_documents_to_index,
    query_verification_index,
    get_index_stats
)
from app.services.verification_rag.verifier import verify_sender_context
from app.services.verification_rag.langchain_tool import verify_sender_security_context


def sync_drive_documents(folder_id: Optional[str] = None) -> Dict[str, Any]:
    """
    On-demand sync coordinator:
    1. Fetches reference allowlists, recruiter directories, and scam patterns from Google Drive.
    2. Incrementally upserts vectors to the Supabase pgvector table `emailai_verification_vectors`.
    
    CRITICAL:
    Only executed via explicit manual trigger or CLI script. Never on live message requests.
    """
    docs = fetch_documents_from_google_drive(folder_id=folder_id)
    result = upsert_documents_to_index(docs)
    return {
        "status": result["status"],
        "fetched_from_drive": len(docs),
        "inserted": result.get("inserted", 0),
        "updated": result.get("updated", 0),
        "skipped": result.get("skipped", 0),
        "active_index_size": result.get("active_index_size", 0)
    }


__all__ = [
    "fetch_documents_from_google_drive",
    "upsert_documents_to_index",
    "query_verification_index",
    "verify_sender_context",
    "verify_sender_security_context",
    "get_index_stats",
    "sync_drive_documents"
]
