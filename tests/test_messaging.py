"""Tests for Telegram and WhatsApp Mobile Messaging Integrations."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db
from app.config import settings
from app.services import messaging_bot_service, task_service
from app.models.task import TaskCreate, PriorityEnum, CategoryEnum

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()
    from app.database import get_db_connection
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("DELETE FROM tasks WHERE title LIKE 'Task before backup%';")
    finally:
        conn.close()

def test_messaging_status_endpoint():
    """Verifies the messaging webhook status endpoint."""
    resp = client.get("/api/webhooks/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "telegram" in data
    assert "whatsapp" in data

def test_telegram_security_authorization_gate():
    """Verifies that an unauthorized chat ID is rejected when chat ID whitelist is active."""
    original_id = settings.TELEGRAM_ALLOWED_CHAT_ID
    try:
        settings.TELEGRAM_ALLOWED_CHAT_ID = "12345678"
        # From attacker
        resp_blocked = messaging_bot_service.handle_incoming_text(sender_id="99999999", platform="telegram", text="/briefing")
        assert "Unauthorized" in resp_blocked

        # From authorized user
        resp_allowed = messaging_bot_service.handle_incoming_text(sender_id="12345678", platform="telegram", text="/start")
        assert "Welcome" in resp_allowed
    finally:
        settings.TELEGRAM_ALLOWED_CHAT_ID = original_id

def test_messaging_commands():
    """Verifies core executive messaging commands."""
    # 1. /start
    res_start = messaging_bot_service.handle_incoming_text(sender_id="any", platform="telegram", text="/start")
    assert "Welcome" in res_start
    assert "/briefing" in res_start

    # 2. /briefing
    res_briefing = messaging_bot_service.handle_incoming_text(sender_id="any", platform="telegram", text="/briefing")
    assert "DAILY EXECUTIVE BRIEFING" in res_briefing

    # 3. /tasks
    t = task_service.create_task(TaskCreate(title="Test Telegram Task", priority=PriorityEnum.P1_URGENT, category=CategoryEnum.STUDY))
    try:
        res_tasks = messaging_bot_service.handle_incoming_text(sender_id="any", platform="telegram", text="/tasks")
        assert "Active Commitments" in res_tasks
        assert "Test Telegram Task" in res_tasks
    finally:
        task_service.delete_task(t.id)

    # 4. /approvals
    res_appr = messaging_bot_service.handle_incoming_text(sender_id="any", platform="telegram", text="/approvals")
    assert "Security Gate" in res_appr or "Pending" in res_appr

def test_whatsapp_twilio_webhook_endpoint():
    """Tests incoming Twilio WhatsApp webhook and TwiML XML formatting."""
    sender_number = settings.WHATSAPP_ALLOWED_NUMBER or "+919876543210"
    clean_sender = sender_number if sender_number.startswith("whatsapp:") else f"whatsapp:{sender_number}"
    resp = client.post(
        "/api/webhooks/whatsapp",
        data={"From": clean_sender, "Body": "/start"}
    )
    assert resp.status_code == 200
    assert "text/xml" in resp.headers["content-type"]
    assert "<Response>" in resp.text
    assert "<Message>" in resp.text
    assert "Welcome" in resp.text

def test_linkedin_link_variations_and_agentic_flow():
    """Verifies that all LinkedIn profile URL variations trigger the HITL permission gate and can be approved."""
    # 1. Standard URL
    res1 = messaging_bot_service.handle_incoming_text("any", "telegram", "https://www.linkedin.com/in/mohil-c")
    assert "SECURITY GATE" in res1
    assert "LINKEDIN_INVITE" in res1
    assert "Mohil C" in res1

    # 2. Regional URL (in.linkedin.com)
    res2 = messaging_bot_service.handle_incoming_text("any", "telegram", "https://in.linkedin.com/in/sarah-jenkins")
    assert "SECURITY GATE" in res2
    assert "Sarah Jenkins" in res2

    # 3. Missing scheme and with tracking params
    wa_sender = settings.WHATSAPP_ALLOWED_NUMBER or "+918590144798"
    res3 = messaging_bot_service.handle_incoming_text(wa_sender, "whatsapp", "linkedin.com/in/dr-rajesh-kumar?utm_source=share")
    assert "SECURITY GATE" in res3
    assert "Dr Rajesh Kumar" in res3

    # 4. Conversational wrapping ("check this linkedin link: ...")
    res4 = messaging_bot_service.handle_incoming_text("any", "telegram", "check this linkedin link: https://www.linkedin.com/in/ananya-sharma")
    assert "SECURITY GATE" in res4
    assert "Ananya Sharma" in res4

    # 5. Custom note extraction
    res5 = messaging_bot_service.handle_incoming_text(
        "any", "telegram",
        "connect linkedin.com/in/vikram-menon note: Interested in your ML internship cohort"
    )
    assert "SECURITY GATE" in res5
    assert "Interested in your ML internship cohort" in res5

    # 6. Approving staged invite via chatbot command
    # Extract approval ID from res5
    import re
    appr_match = re.search(r"/approve ([a-f0-9]{8})", res5)
    assert appr_match is not None
    short_id = appr_match.group(1)
    res_approve = messaging_bot_service.handle_incoming_text("any", "telegram", f"/approve {short_id}")
    assert "ACTION EXECUTED SUCCESSFULLY" in res_approve

def test_linkedin_diagnostics_and_features():
    """Verifies LinkedIn diagnostics, post detection, and profile inspection."""
    # 1. Diagnostics trigger when user asks why LinkedIn link is not working
    res_diag = messaging_bot_service.handle_incoming_text("any", "telegram", "why is linkedin link not working?")
    assert "MCP SYSTEM DIAGNOSTICS" in res_diag
    assert "LinkedIn MCP" in res_diag

    # 2. LinkedIn Post link detection
    res_post = messaging_bot_service.handle_incoming_text(
        "any", "telegram",
        "https://www.linkedin.com/posts/mohil-c_autonomous-drones-telemetry-activity-712345"
    )
    assert "LinkedIn Post Link Detected" in res_post

    # 3. View Profile inspection
    res_view = messaging_bot_service.handle_incoming_text(
        "any", "telegram",
        "view profile https://www.linkedin.com/in/mohil-c"
    )
    assert "LinkedIn Profile Summary" in res_view


def test_linkedin_post_like_and_comment_chat_flows():
    """Verifies that liking and commenting on a LinkedIn post creates HITL approvals and can be executed."""
    import re
    post_url = "https://www.linkedin.com/posts/mohil-ai-research-lab-update"

    # 1. Like LinkedIn Post
    res_like = messaging_bot_service.handle_incoming_text(
        "any", "telegram",
        f"like {post_url}"
    )
    assert "SECURITY GATE" in res_like
    assert "LINKEDIN_LIKE" in res_like
    assert post_url in res_like

    like_match = re.search(r"/approve ([a-f0-9]{8})", res_like)
    assert like_match is not None
    like_id = like_match.group(1)
    res_approve_like = messaging_bot_service.handle_incoming_text("any", "telegram", f"/approve {like_id}")
    assert "ACTION EXECUTED SUCCESSFULLY" in res_approve_like

    # 2. Comment on LinkedIn Post
    res_comm = messaging_bot_service.handle_incoming_text(
        "any", "telegram",
        f"comment on {post_url}: Outstanding telemetry breakthroughs!"
    )
    assert "SECURITY GATE" in res_comm
    assert "LINKEDIN_COMMENT" in res_comm
    assert "Outstanding telemetry breakthroughs!" in res_comm

    comm_match = re.search(r"/approve ([a-f0-9]{8})", res_comm)
    assert comm_match is not None
    comm_id = comm_match.group(1)
    res_approve_comm = messaging_bot_service.handle_incoming_text("any", "telegram", f"/approve {comm_id}")
    assert "ACTION EXECUTED SUCCESSFULLY" in res_approve_comm


def test_whatsapp_simulation_endpoint():
    """Verifies that the /api/webhooks/whatsapp/simulate endpoint returns instant WhatsApp responses."""
    resp = client.post(
        "/api/webhooks/whatsapp/simulate",
        json={"from_number": "+918590144798", "message": "/briefing"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "DAILY EXECUTIVE BRIEFING" in data["reply"]
    assert data["sender"] == "+918590144798"


