"""Service for scheduling, triggering, snoozing, and tracking reminder deliveries."""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from app.database import get_db_connection
from app.models.task import ReminderCreate, ReminderResponse, ReminderStatusEnum

def create_reminder(data: ReminderCreate) -> ReminderResponse:
    """Creates a new reminder for a task."""
    remind_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO reminders (
                id, task_id, remind_at, status, channel, delivery_message, snooze_count, created_at
            ) VALUES (?, ?, ?, 'SCHEDULED', ?, ?, 0, ?);
            """, (
                remind_id,
                data.task_id,
                data.remind_at,
                data.channel,
                data.delivery_message or "Task deadline reminder",
                now_iso
            ))
        return get_reminder(remind_id)
    finally:
        conn.close()

def get_reminder(remind_id: str) -> Optional[ReminderResponse]:
    """Retrieves a single reminder."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM reminders WHERE id = ?;", (remind_id,))
        row = cur.fetchone()
        if not row:
            return None
        return ReminderResponse(
            id=row["id"],
            task_id=row["task_id"],
            remind_at=row["remind_at"],
            status=ReminderStatusEnum(row["status"]),
            channel=row["channel"],
            delivery_message=row["delivery_message"],
            delivery_timestamp=row["delivery_timestamp"],
            snooze_count=row["snooze_count"],
            created_at=row["created_at"]
        )
    finally:
        conn.close()

def process_due_reminders() -> List[ReminderResponse]:
    """
    Scans for scheduled reminders that have reached or passed their trigger time.
    Executes simulated/dashboard delivery, updates delivery timestamp and status to DELIVERED.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    conn = get_db_connection()
    delivered_reminders = []
    
    try:
        cur = conn.execute("""
            SELECT r.*, t.title as task_title 
            FROM reminders r 
            JOIN tasks t ON r.task_id = t.id 
            WHERE r.status = 'SCHEDULED' AND r.remind_at <= ?;
        """, (now_iso,))
        due_rows = cur.fetchall()
        
        with conn:
            for row in due_rows:
                r_id = row["id"]
                task_title = row["task_title"]
                delivery_msg = f"[ALERT] Task '{task_title}' is due or starting now!"
                
                conn.execute("""
                UPDATE reminders 
                SET status = 'DELIVERED', 
                    delivery_timestamp = ?, 
                    delivery_message = ?
                WHERE id = ?;
                """, (now_iso, delivery_msg, r_id))
                
                delivered_reminders.append(get_reminder(r_id))
                
        return [r for r in delivered_reminders if r is not None]
    finally:
        conn.close()

def snooze_reminder(remind_id: str, minutes: int = 15) -> Optional[ReminderResponse]:
    """Snoozes a reminder by pushing its scheduled time forward."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM reminders WHERE id = ?;", (remind_id,))
        row = cur.fetchone()
        if not row:
            return None
            
        new_remind_dt = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        new_remind_iso = new_remind_dt.isoformat()
        new_count = row["snooze_count"] + 1
        
        with conn:
            conn.execute("""
            UPDATE reminders 
            SET status = 'SCHEDULED',
                remind_at = ?,
                snooze_count = ?,
                delivery_timestamp = NULL
            WHERE id = ?;
            """, (new_remind_iso, new_count, remind_id))
            
        return get_reminder(remind_id)
    finally:
        conn.close()

def dismiss_reminder(remind_id: str) -> Optional[ReminderResponse]:
    """Dismisses a reminder."""
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("UPDATE reminders SET status = 'DISMISSED' WHERE id = ?;", (remind_id,))
        return get_reminder(remind_id)
    finally:
        conn.close()

def list_reminders(status: Optional[str] = None) -> List[ReminderResponse]:
    """Lists reminders filtered by status."""
    conn = get_db_connection()
    try:
        if status:
            cur = conn.execute("SELECT * FROM reminders WHERE status = ? ORDER BY remind_at ASC;", (status,))
        else:
            cur = conn.execute("SELECT * FROM reminders ORDER BY remind_at ASC;")
        rows = cur.fetchall()
        return [
            ReminderResponse(
                id=r["id"],
                task_id=r["task_id"],
                remind_at=r["remind_at"],
                status=ReminderStatusEnum(r["status"]),
                channel=r["channel"],
                delivery_message=r["delivery_message"],
                delivery_timestamp=r["delivery_timestamp"],
                snooze_count=r["snooze_count"],
                created_at=r["created_at"]
            ) for r in rows
        ]
    finally:
        conn.close()
