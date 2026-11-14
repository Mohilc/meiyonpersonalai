"""Tests for Task CRUD, status lifecycle, and persistence."""
from datetime import datetime, timezone, timedelta
from app.database import init_db
from app.services import task_service
from app.models.task import (
    TaskCreate, TaskUpdate, TaskStatusEnum, PriorityEnum, CategoryEnum
)

def test_task_lifecycle_crud():
    init_db()
    
    # 1. Add Task
    due_dt = datetime.now(timezone.utc) + timedelta(days=2)
    new_task = task_service.create_task(TaskCreate(
        title="Prepare Resume for ML Internships",
        description="Highlight Python, PyTorch, and Drone project",
        due_date=due_dt.isoformat(),
        priority=PriorityEnum.P1_URGENT,
        category=CategoryEnum.JOB_SEARCH,
        is_confirmed=True,
        reminder_minutes_before=60
    ))
    assert new_task.id is not None
    assert new_task.status == TaskStatusEnum.PENDING
    assert new_task.is_confirmed is True
    assert len(new_task.reminders) == 1
    
    # 2. Retrieve Task
    retrieved = task_service.get_task(new_task.id)
    assert retrieved is not None
    assert retrieved.title == "Prepare Resume for ML Internships"
    
    # 3. Edit Task
    updated = task_service.update_task(new_task.id, TaskUpdate(
        priority=PriorityEnum.P2_HIGH,
        description="Updated notes: include Git repositories"
    ))
    assert updated.priority == PriorityEnum.P2_HIGH
    assert "Updated notes" in updated.description
    
    # 4. Complete Task (verify honesty - status is COMPLETED and completed_at is recorded)
    completed = task_service.complete_task(new_task.id)
    assert completed.status == TaskStatusEnum.COMPLETED
    assert completed.completed_at is not None
    
    # 5. Delete Task
    deleted = task_service.delete_task(new_task.id)
    assert deleted is True
    assert task_service.get_task(new_task.id) is None

def test_inferred_vs_confirmed_tasks():
    init_db()
    # Create inferred task (e.g. from an email that suggested a meeting date)
    task = task_service.create_task(TaskCreate(
        title="Inferred Recruiter Follow-up",
        is_confirmed=False
    ))
    assert task.is_confirmed is False
    
    # Confirm it after verification
    confirmed_task = task_service.update_task(task.id, TaskUpdate(is_confirmed=True))
    assert confirmed_task.is_confirmed is True
    
    # Clean up
    task_service.delete_task(task.id)

def test_task_server_tools_and_commands():
    """Validates FastMCP task_server tools and dual-mode execution."""
    import json
    from mcp_servers import task_server
    from app.services import messaging_bot_service

    init_db()

    # 1. Server status
    status_raw = task_server.get_task_server_status()
    status_data = json.loads(status_raw)
    assert status_data["connected"] is True
    assert "mode" in status_data

    # 2. Create task tool
    create_raw = task_server.create_task(
        title="Test Sensor Calibration",
        description="Calibrate IMU and barometer",
        priority="P2_HIGH",
        due_date="2026-11-25"
    )
    create_data = json.loads(create_raw)
    assert create_data["status"] == "SUCCESS"
    assert "task_id" in create_data
    task_id = create_data["task_id"]

    # 3. List active tasks
    list_raw = task_server.list_active_tasks(limit=10)
    list_data = json.loads(list_raw)
    assert list_data["status"] == "SUCCESS"
    assert any(t["id"] == task_id[:8] for t in list_data["tasks"])

    # 4. Complete task tool
    comp_raw = task_server.complete_task(task_id[:8])
    comp_data = json.loads(comp_raw)
    assert comp_data["status"] == "SUCCESS"
    assert comp_data["task_status"] == "COMPLETED"

    # 5. Mark important data tool
    imp_raw = task_server.mark_important_data(
        title="Battery Min Voltage",
        content="Never drop below 14.4V"
    )
    imp_data = json.loads(imp_raw)
    assert imp_data["status"] == "SUCCESS"
    assert "memory_id" in imp_data
    assert "task_id" in imp_data

    # 6. Messaging bot commands: /task add, /done, /important
    res_add = messaging_bot_service.handle_incoming_text("tester", "telegram", "/task add Test Bot Task | 2026-11-28")
    assert "Task Created!" in res_add
    assert "Test Bot Task" in res_add

    res_tasks = messaging_bot_service.handle_incoming_text("tester", "telegram", "/tasks")
    assert "Active Commitments & Tasks" in res_tasks
    assert "Test Bot Task" in res_tasks

    # Clean up created task
    task_service.delete_task(task_id)
    task_service.delete_task(imp_data["task_id"])

