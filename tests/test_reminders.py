"""Tests for Reminder delivery tracking, triggering, and snoozing."""
from datetime import datetime, timezone, timedelta
from app.database import init_db
from app.services import task_service, reminder_service
from app.models.task import (
    TaskCreate, ReminderCreate, ReminderStatusEnum, PriorityEnum, CategoryEnum
)

def test_reminder_trigger_and_delivery_status():
    init_db()
    
    # 1. Create a task
    task = task_service.create_task(TaskCreate(
        title="B.Tech AI Assignment Submission",
        priority=PriorityEnum.P1_URGENT,
        category=CategoryEnum.STUDY
    ))
    
    # 2. Schedule a reminder that is due NOW (in the past by 1 minute)
    past_due = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
    reminder = reminder_service.create_reminder(ReminderCreate(
        task_id=task.id,
        remind_at=past_due,
        delivery_message="Assignment is due now!"
    ))
    assert reminder.status == ReminderStatusEnum.SCHEDULED
    assert reminder.delivery_timestamp is None
    
    # 3. Process due reminders
    delivered = reminder_service.process_due_reminders()
    delivered_ids = [r.id for r in delivered]
    assert reminder.id in delivered_ids
    
    # 4. Check reminder status after trigger
    checked = reminder_service.get_reminder(reminder.id)
    assert checked.status == ReminderStatusEnum.DELIVERED
    assert checked.delivery_timestamp is not None
    assert "[ALERT]" in checked.delivery_message
    
    # 5. Test Snooze (reschedules and resets delivery timestamp)
    snoozed = reminder_service.snooze_reminder(reminder.id, minutes=15)
    assert snoozed.status == ReminderStatusEnum.SCHEDULED
    assert snoozed.snooze_count == 1
    assert snoozed.delivery_timestamp is None
    
    # 6. Test Dismiss
    dismissed = reminder_service.dismiss_reminder(reminder.id)
    assert dismissed.status == ReminderStatusEnum.DISMISSED
    
    # Clean up
    task_service.delete_task(task.id)
