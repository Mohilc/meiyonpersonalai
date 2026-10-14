"""Tests for SQLite database initialization, WAL mode, persistence, and backup/restore."""
import pytest
from pathlib import Path
from app.config import settings
from app.database import init_db, get_db_connection, backup_database, restore_database
from app.services import profile_service, task_service
from app.models.task import TaskCreate, PriorityEnum, CategoryEnum

def test_database_initialization_and_wal():
    init_db()
    conn = get_db_connection()
    cur = conn.execute("PRAGMA journal_mode;")
    mode = cur.fetchone()[0]
    conn.close()
    assert mode.lower() == "wal"

def test_profile_seeded():
    init_db()
    prof = profile_service.get_profile()
    assert "B.Tech Computer Science with Artificial Intelligence" in prof.education
    assert "Mar Baselios Christian College" in prof.college
    assert prof.expected_graduation == "2027"
    assert prof.timezone == "Asia/Kolkata"

def test_backup_and_restore_cycle():
    init_db()
    # 1. Create a baseline task
    task = task_service.create_task(TaskCreate(
        title="Task before backup",
        priority=PriorityEnum.P1_URGENT,
        category=CategoryEnum.STUDY
    ))
    
    # 2. Take a backup
    backup_file = backup_database()
    assert backup_file.exists()
    assert backup_file.stat().st_size > 0
    
    # 3. Create a task AFTER backup
    task_after = task_service.create_task(TaskCreate(
        title="Task after backup",
        priority=PriorityEnum.P2_HIGH,
        category=CategoryEnum.PROJECT
    ))
    assert task_service.get_task(task_after.id) is not None
    
    # 4. Restore the backup
    success = restore_database(backup_file)
    assert success is True
    
    # 5. Verify the restored state: task before backup exists, task after backup does not exist in restored state
    assert task_service.get_task(task.id) is not None
    assert task_service.get_task(task_after.id) is None
