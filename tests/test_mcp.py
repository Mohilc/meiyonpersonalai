"""Tests for Gmail and LinkedIn Model Context Protocol (MCP) Servers and Services."""
import json
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db, get_db_connection
from app.services import mcp_service, audit_service
from app.models.approval import RiskLevelEnum, ApprovalDecision, ApprovalStatusEnum
from mcp_servers import gmail_server, linkedin_server

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    init_db()
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("DELETE FROM email_messages WHERE external_id IS NOT NULL;")
            conn.execute("DELETE FROM linkedin_interactions;")
    finally:
        conn.close()


def test_gmail_mcp_server_tools():
    """Validates core Gmail MCP server tools directly."""
    # 1. Status
    status_raw = gmail_server.get_mailbox_status()
    status = json.loads(status_raw)
    assert status["connected"] is True
    assert "mode" in status
    assert "configured_address" in status

    # 2. List unread emails
    list_raw = gmail_server.list_unread_emails(max_results=3)
    list_res = json.loads(list_raw)
    assert list_res["status"] in ("SUCCESS", "FALLBACK_SANDBOX")
    assert len(list_res["emails"]) > 0
    first_email = list_res["emails"][0]
    assert "subject" in first_email
    assert "sender" in first_email
    assert "body" in first_email

    # 3. Read specific email
    msg_id = first_email["id"]
    read_raw = gmail_server.read_email(msg_id)
    read_res = json.loads(read_raw)
    assert read_res["status"] == "SUCCESS"
    assert read_res["email"]["id"] == msg_id

    # 4. Draft reply
    draft_raw = gmail_server.draft_email_reply(
        thread_id="thread_001",
        to="recruiter@example.com",
        subject="Interview follow up",
        reply_body="I look forward to discussing the role."
    )
    draft_res = json.loads(draft_raw)
    assert draft_res["status"] == "SUCCESS"
    assert "draft_id" in draft_res

    # 5. Safety guardrail: Sending without approval must halt
    send_unapproved_raw = gmail_server.send_email(
        to="recruiter@example.com",
        subject="Re: Job",
        body="Yes",
        approved=False
    )
    send_unapproved = json.loads(send_unapproved_raw)
    assert send_unapproved["status"] == "HALTED_FOR_APPROVAL"

def test_linkedin_mcp_server_tools():
    """Validates core LinkedIn MCP server tools directly."""
    # 1. Status
    status_raw = linkedin_server.get_linkedin_status()
    status = json.loads(status_raw)
    assert status["connected"] is True
    assert status["user_name"] == "Mohil"

    # 2. Candidate Profile
    prof_raw = linkedin_server.get_linkedin_profile()
    prof = json.loads(prof_raw)
    assert prof["status"] in ("SUCCESS", "FALLBACK_SANDBOX")
    assert prof["profile"]["full_name"] == "Mohil"
    assert "Mar Baselios" in prof["profile"]["education"]

    # 3. Connection requests & messages
    conn_raw = linkedin_server.list_connection_requests(limit=2)
    conn = json.loads(conn_raw)
    assert conn["status"] == "SUCCESS"
    assert len(conn["connections"]) > 0

    msg_raw = linkedin_server.list_recent_messages(limit=2)
    msg = json.loads(msg_raw)
    assert msg["status"] == "SUCCESS"
    assert len(msg["messages"]) > 0

    # 4. 300 character limit enforcement for connection notes
    over_limit_note = "A" * 305
    invalid_res = json.loads(linkedin_server.send_connection_invite("https://linkedin.com/in/test", over_limit_note))
    assert invalid_res["status"] == "VALIDATION_ERROR"
    assert "300" in invalid_res["error"]

    # 5. Safety guardrail: Publishing post without approval must halt
    unapproved_post = json.loads(linkedin_server.publish_post("Excited to share my drone project!", approved=False))
    assert unapproved_post["status"] == "HALTED_FOR_APPROVAL"

def test_mcp_service_email_sync_and_triage():
    """Validates that syncing emails via MCP runs security triage and deduplicates."""
    res = mcp_service.sync_unread_emails_via_mcp(limit=5)
    assert res.status == "SUCCESS"
    assert res.synced_count > 0
    
    # Check that triaged emails are in database
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM email_messages WHERE external_id IS NOT NULL;")
        rows = cur.fetchall()
        assert len(rows) >= res.synced_count
        
        # Verify prompt injection was sanitized for msg_004
        cur_inj = conn.execute("SELECT * FROM email_messages WHERE external_id = 'gmail_msg_004';")
        inj_row = cur_inj.fetchone()
        if inj_row:
            assert "[BLOCKED_INJECTION_ATTEMPT]" in inj_row["body"]
            assert "Prompt injection" in inj_row["phishing_flags"]
    finally:
        conn.close()

    # Second sync should not duplicate
    res_second = mcp_service.sync_unread_emails_via_mcp(limit=5)
    assert res_second.synced_count == 0

def test_mcp_service_linkedin_sync():
    """Validates syncing LinkedIn messages and connection requests into SQLite."""
    res = mcp_service.sync_linkedin_activity_via_mcp(limit=5)
    assert res.status == "SUCCESS"
    assert res.synced_messages_count > 0
    assert res.pending_connections_count > 0

    interactions = mcp_service.list_linkedin_interactions()
    assert len(interactions) >= (res.synced_messages_count + res.pending_connections_count)

def test_mcp_rest_api_endpoints():
    """Tests the FastAPI REST endpoints for MCP operations."""
    # 1. MCP Status
    r_status = client.get("/api/communication/mcp/status")
    assert r_status.status_code == 200
    data = r_status.json()
    assert data["is_ready"] is True
    assert "gmail" in data
    assert "linkedin" in data

    # 2. Trigger Email Sync
    r_sync_email = client.post("/api/communication/mcp/sync-emails", json={"limit": 5})
    assert r_sync_email.status_code == 200
    assert "synced_count" in r_sync_email.json()

    # 3. Trigger LinkedIn Sync
    r_sync_li = client.post("/api/communication/mcp/sync-linkedin", json={"limit": 5})
    assert r_sync_li.status_code == 200
    assert "synced_messages_count" in r_sync_li.json()

    # 4. List LinkedIn interactions
    r_li_list = client.get("/api/communication/linkedin/interactions")
    assert r_li_list.status_code == 200
    assert isinstance(r_li_list.json(), list)

def test_mcp_execute_approved_action_gate():
    """Verifies that approved MCP actions execute only when human authorization is granted."""
    # 1. Create approval request for sending email reply
    appr = audit_service.create_approval_request(
        title="Send MCP Email Reply to Recruiter",
        description="Authorization required to transmit reply",
        action_payload={
            "action_type": "EMAIL_REPLY",
            "recipient": "recruiting@deepautonomy.ai",
            "subject": "Re: Interview Invitation",
            "reply_body": "I confirm my availability for Tuesday 2 PM IST."
        },
        risk_level=RiskLevelEnum.HIGH
    )

    # 2. Attempt execution while still PENDING - must fail
    res_pending = client.post(f"/api/communication/mcp/execute-approved/{appr.id}")
    assert res_pending.status_code == 400
    assert "cannot be executed" in res_pending.json()["detail"]

    # 3. Approve via security gate
    audit_service.decide_approval(appr.id, ApprovalDecision(decision=ApprovalStatusEnum.APPROVED, reason="Authorized by Mohil"))


    # 4. Execute approved action - must succeed
    res_approved = client.post(f"/api/communication/mcp/execute-approved/{appr.id}")
    assert res_approved.status_code == 200
    exec_data = res_approved.json()
    assert exec_data["status"] == "EXECUTED"
    assert exec_data["mcp_result"]["status"] in ("SENT", "SENT_SIMULATED")
