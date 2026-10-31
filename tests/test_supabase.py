"""Unit tests for Supabase Cloud Storage & Database Persistence."""
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.config import settings, DATA_DIR
from app.database import init_db
from app.services import supabase_service, messaging_bot_service

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_supabase_status_unconfigured():
    """Verify status response when Supabase is not configured."""
    with patch.object(settings, "SUPABASE_URL", ""), patch.object(settings, "SUPABASE_KEY", ""):
        status = supabase_service.get_status()
        assert status["configured"] is False
        assert "Not Set" in status["supabase_url"]
        assert status["storage_bucket"] == settings.SUPABASE_STORAGE_BUCKET

def test_supabase_status_endpoint():
    """Verify REST endpoint GET /api/supabase/status."""
    resp = client.get("/api/supabase/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "configured" in data
    assert "storage_bucket" in data

def test_supabase_upload_file_simulation():
    """Verify upload_file gracefully simulates local URL when not connected to cloud."""
    test_file = DATA_DIR / "test_sample.txt"
    test_file.write_text("Hello Supabase", encoding="utf-8")

    try:
        with patch.object(settings, "SUPABASE_URL", ""), patch.object(settings, "SUPABASE_KEY", ""):
            res = supabase_service.upload_file(test_file)
            assert res is not None
            assert res["simulated"] is True
            assert res["path"] == "test_sample.txt"
            assert "public_url" in res
    finally:
        if test_file.exists():
            test_file.unlink()

def test_supabase_cloud_backup_workflow():
    """Verify backup_database_to_cloud successfully snapshots the DB and triggers cloud upload."""
    res = supabase_service.backup_database_to_cloud()
    assert res is not None
    assert res["status"] == "success"
    assert "backups/manager_backup_" in res["archive_path"]
    assert res["latest_path"] == "backups/latest.db"

def test_supabase_api_backup_endpoint():
    """Verify POST /api/supabase/backup."""
    resp = client.post("/api/supabase/backup")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "archive_path" in data

def test_messaging_bot_supabase_command():
    """Verify Telegram /supabase command output."""
    msg = messaging_bot_service.handle_incoming_text(
        sender_id="test_user_telegram",
        platform="telegram",
        text="/supabase"
    )
    assert "Supabase Cloud Storage" in msg

    msg_backup = messaging_bot_service.handle_incoming_text(
        sender_id="test_user_telegram",
        platform="telegram",
        text="/supabase backup"
    )
    assert "Supabase Cloud Backup" in msg_backup
    assert "backups/latest.db" in msg_backup
