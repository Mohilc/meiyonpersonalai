"""Unit Tests for EmailAI Verification RAG Module."""
import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import verification_rag
from app.services.verification_rag import (
    drive_sync,
    vector_index,
    verifier,
    langchain_tool
)


@pytest.fixture
def client():
    return TestClient(app)


def test_drive_sync_and_parsing():
    """Validates that document fetching and parsing produces categorized reference docs."""
    docs = drive_sync.fetch_documents_from_google_drive()
    assert len(docs) > 0

    categories = [d["category"] for d in docs]
    assert "ALLOWLIST" in categories
    assert "RECRUITER_DIRECTORY" in categories
    assert "SCAM_PATTERN" in categories

    for d in docs:
        assert "doc_id" in d
        assert "file_name" in d
        assert "doc_hash" in d
        assert len(d["content"]) > 10


def test_vector_index_idempotent_upsert():
    """Validates idempotent upsert into the vector index."""
    docs = drive_sync.fetch_documents_from_google_drive()
    
    # 1. First upsert
    res1 = vector_index.upsert_documents_to_index(docs)
    assert res1["status"] == "SUCCESS"
    assert res1["total_documents"] == len(docs)

    # 2. Second upsert with unchanged documents should be skipped (idempotent)
    res2 = vector_index.upsert_documents_to_index(docs)
    assert res2["status"] == "SUCCESS"
    assert res2["skipped"] == len(docs)


def test_vector_query():
    """Validates semantic and category-filtered vector query."""
    docs = drive_sync.fetch_documents_from_google_drive()
    vector_index.upsert_documents_to_index(docs)

    results = vector_index.query_verification_index("greenhouse ATS recruiting", category="ALLOWLIST", top_k=2)
    assert len(results) > 0
    assert "greenhouse" in results[0]["text"].lower()


def test_verifier_allowlist_domain():
    """Validates that verified ATS enterprise domains receive high confidence and trust signals."""
    docs = drive_sync.fetch_documents_from_google_drive()
    vector_index.upsert_documents_to_index(docs)

    result = verifier.verify_sender_context(
        sender_email="recruiting@greenhouse.io",
        domain="greenhouse.io",
        message_text="Invitation to interview for Senior AI Engineer"
    )

    assert isinstance(result, dict)
    assert "matched_entities" in result
    assert "domain_trust_signals" in result
    assert "risk_flags" in result
    assert "confidence_score" in result
    assert result["confidence_score"] >= 0.90
    assert any("greenhouse.io" in s for s in result["domain_trust_signals"])
    assert len(result["risk_flags"]) == 0


def test_verifier_scam_detection():
    """Validates that phishing and equipment cashier check patterns are flagged with low confidence."""
    docs = drive_sync.fetch_documents_from_google_drive()
    vector_index.upsert_documents_to_index(docs)

    result = verifier.verify_sender_context(
        sender_email="hr-google@gmail.com",
        domain="gmail.com",
        message_text="Congratulations! We will mail you a cashier's check to buy your office equipment. Join Telegram @recruiter."
    )

    assert result["confidence_score"] < 0.40
    assert len(result["risk_flags"]) > 0
    assert any("cashier's check" in f.lower() for f in result["risk_flags"])
    assert any("telegram" in f.lower() for f in result["risk_flags"])
    assert any("free webmail" in f.lower() for f in result["risk_flags"])


def test_langchain_tool_wrapper():
    """Validates the LangChain tool wrapper returns strict JSON with required schema."""
    tool_func = langchain_tool.verify_sender_security_context
    raw_json = tool_func.invoke({
        "sender_email": "recruiting@deepautonomy.ai",
        "domain": "deepautonomy.ai",
        "message_text": "We would like to discuss the Autonomous Systems Engineer position."
    })

    parsed = json.loads(raw_json)
    assert "matched_entities" in parsed
    assert "domain_trust_signals" in parsed
    assert "risk_flags" in parsed
    assert "confidence_score" in parsed
    assert parsed["confidence_score"] >= 0.70


def test_api_verification_routes(client):
    """Validates FastAPI endpoints for verification RAG."""
    # 1. Status
    res_status = client.get("/api/verification/status")
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert status_data["status"] == "ONLINE"
    assert "telemetry" in status_data

    # 2. Live verification test endpoint
    res_verify = client.post("/api/verification/verify", json={
        "sender_email": "sarah@deepautonomy.ai",
        "domain": "deepautonomy.ai",
        "message_text": "Interview confirmation for Robotics AI role",
        "source_platform": "Email"
    })
    assert res_verify.status_code == 200
    verify_data = res_verify.json()
    assert verify_data["confidence_score"] >= 0.70
    assert "matched_entities" in verify_data

    # 3. Sync Drive endpoint (with valid secret)
    from app.config import settings
    res_sync = client.post(
        "/api/verification/sync-drive",
        headers={"x-sync-secret": settings.VERIFICATION_SYNC_SECRET}
    )
    assert res_sync.status_code == 200
    sync_data = res_sync.json()
    assert sync_data["success"] is True
    assert "details" in sync_data
