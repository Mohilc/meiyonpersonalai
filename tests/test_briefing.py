"""Tests for Daily Executive Briefing generation and priority ranking."""
from datetime import datetime, timezone, timedelta
from app.database import init_db
from app.services import task_service, briefing_service
from app.models.task import TaskCreate, PriorityEnum, CategoryEnum

def test_daily_briefing_generation():
    init_db()
    
    # Create tasks with various priorities and dates
    now = datetime.now(timezone.utc)
    t1 = task_service.create_task(TaskCreate(
        title="P1 Urgent Study Milestone",
        due_date=(now + timedelta(hours=2)).isoformat(),
        priority=PriorityEnum.P1_URGENT,
        category=CategoryEnum.STUDY
    ))
    t2 = task_service.create_task(TaskCreate(
        title="P2 High Job Application",
        due_date=(now + timedelta(hours=4)).isoformat(),
        priority=PriorityEnum.P2_HIGH,
        category=CategoryEnum.JOB_SEARCH
    ))
    t3 = task_service.create_task(TaskCreate(
        title="Overdue Personal Chore",
        due_date=(now - timedelta(days=1)).isoformat(),
        priority=PriorityEnum.P3_MEDIUM,
        category=CategoryEnum.PERSONAL
    ))
    
    briefing = briefing_service.generate_daily_briefing()
    assert briefing is not None
    assert briefing.timezone == "Asia/Kolkata"
    assert len(briefing.top_three_priorities) <= 3
    assert len(briefing.recommendations) > 0
    assert len(briefing.overdue_commitments) >= 1
    assert any(t.id == t3.id for t in briefing.overdue_commitments)
    
    # Cleanup
    task_service.delete_task(t1.id)
    task_service.delete_task(t2.id)
    task_service.delete_task(t3.id)
