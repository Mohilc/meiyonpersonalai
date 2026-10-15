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
    resp = client.post(
        "/api/webhooks/whatsapp",
        data={"From": "whatsapp:+919876543210", "Body": "/start"}
    )
    assert resp.status_code == 200
    assert "text/xml" in resp.headers["content-type"]
    assert "<Response>" in resp.text
    assert "<Message>" in resp.text
    assert "Welcome" in resp.text
