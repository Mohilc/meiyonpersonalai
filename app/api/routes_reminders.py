"""API Routes for Reminders."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.task import ReminderCreate, ReminderResponse, ReminderSnooze
from app.services import reminder_service, audit_service

router = APIRouter(prefix="/api/reminders", tags=["Reminders"])

@router.get("", response_model=List[ReminderResponse])
def list_reminders(status: Optional[str] = Query(None)):
    return reminder_service.list_reminders(status=status)

@router.post("", response_model=ReminderResponse, status_code=201)
def create_reminder(payload: ReminderCreate):
    created = reminder_service.create_reminder(payload)
    return created

@router.post("/process-due", response_model=List[ReminderResponse])
def process_due_reminders():
    """Triggers delivery check for any reminders scheduled on or before current time."""
    delivered = reminder_service.process_due_reminders()
    if delivered:
        audit_service.log_audit(
            action_type="REMINDERS_DELIVERED",
            target_entity="reminders",
            details={"delivered_count": len(delivered), "ids": [r.id for r in delivered]},
            status="SUCCESS"
        )
    return delivered

@router.post("/{remind_id}/snooze", response_model=ReminderResponse)
def snooze_reminder(remind_id: str, payload: ReminderSnooze):
    snoozed = reminder_service.snooze_reminder(remind_id, minutes=payload.snooze_minutes)
    if not snoozed:
        raise HTTPException(status_code=404, detail="Reminder not found")
    audit_service.log_audit(
        action_type="REMINDER_SNOOZED",
        target_entity="reminder",
        details={"remind_id": remind_id, "snooze_minutes": payload.snooze_minutes},
        status="SUCCESS"
    )
    return snoozed

@router.post("/{remind_id}/dismiss", response_model=ReminderResponse)
def dismiss_reminder(remind_id: str):
    dismissed = reminder_service.dismiss_reminder(remind_id)
    if not dismissed:
        raise HTTPException(status_code=404, detail="Reminder not found")
    audit_service.log_audit(
        action_type="REMINDER_DISMISSED",
        target_entity="reminder",
        details={"remind_id": remind_id},
        status="SUCCESS"
    )
    return dismissed
