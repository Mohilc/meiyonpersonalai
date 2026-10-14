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
