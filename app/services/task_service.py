"""Service for persistent Task operations."""
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from app.database import get_db_connection
from app.models.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskStatusEnum, PriorityEnum,
    CategoryEnum, TaskSourceEnum, ReminderResponse, ReminderStatusEnum
)

def _row_to_task(row, reminders: List[ReminderResponse] = None) -> TaskResponse:
    return TaskResponse(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        due_date=row["due_date"],
        priority=PriorityEnum(row["priority"]),
        status=TaskStatusEnum(row["status"]),
        category=CategoryEnum(row["category"]),
        source=TaskSourceEnum(row["source"]),
        related_entity_type=row["related_entity_type"],
        related_entity_id=row["related_entity_id"],
        recurrence=row["recurrence"],
        is_confirmed=bool(row["is_confirmed"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        completed_at=row["completed_at"],
        reminders=reminders or []
    )

def _get_reminders_for_task(conn, task_id: str) -> List[ReminderResponse]:
    cur = conn.execute("SELECT * FROM reminders WHERE task_id = ? ORDER BY remind_at ASC;", (task_id,))
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

def create_task(data: TaskCreate) -> TaskResponse:
    """Creates a new task and optionally schedules an initial reminder."""
    task_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO tasks (
                id, title, description, due_date, priority, status, category,
                source, related_entity_type, related_entity_id, recurrence,
                is_confirmed, created_at, updated_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL);
            """, (
                task_id,
                data.title,
                data.description,
                data.due_date,
                data.priority.value,
                TaskStatusEnum.PENDING.value,
                data.category.value,
                data.source.value,
                data.related_entity_type,
                data.related_entity_id,
                data.recurrence,
                1 if data.is_confirmed else 0,
                now_iso,
                now_iso
            ))
            
            # Auto-schedule reminder if requested and due_date exists
            if data.reminder_minutes_before and data.due_date:
                try:
                    # Parse due date
                    dt = datetime.fromisoformat(data.due_date.replace("Z", "+00:00"))
                    remind_dt = dt - timedelta(minutes=data.reminder_minutes_before)
                    remind_iso = remind_dt.isoformat()
                    
                    remind_id = str(uuid.uuid4())
                    conn.execute("""
                    INSERT INTO reminders (
                        id, task_id, remind_at, status, channel, delivery_message, created_at
                    ) VALUES (?, ?, ?, 'SCHEDULED', 'DASHBOARD', ?, ?);
                    """, (
                        remind_id,
                        task_id,
                        remind_iso,
                        f"Reminder: {data.title} is due soon!",
                        now_iso
                    ))
                except Exception:
                    # If date parsing fails, record task anyway without breaking
                    pass
        
        return get_task(task_id)
    finally:
        conn.close()

def get_task(task_id: str) -> Optional[TaskResponse]:
    """Retrieves a single task with its reminders."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM tasks WHERE id = ?;", (task_id,))
        row = cur.fetchone()
        if not row:
            return None
        reminders = _get_reminders_for_task(conn, task_id)
        return _row_to_task(row, reminders)
    finally:
        conn.close()

def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None
) -> List[TaskResponse]:
    """Lists tasks with optional filtering."""
    conn = get_db_connection()
    try:
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        if category:
            query += " AND category = ?"
            params.append(category)
            
        query += " ORDER BY CASE priority WHEN 'P1_URGENT' THEN 1 WHEN 'P2_HIGH' THEN 2 WHEN 'P3_MEDIUM' THEN 3 ELSE 4 END, due_date ASC;"
        cur = conn.execute(query, params)
        rows = cur.fetchall()
        
        results = []
        for row in rows:
            reminders = _get_reminders_for_task(conn, row["id"])
            results.append(_row_to_task(row, reminders))
        return results
    finally:
        conn.close()

def update_task(task_id: str, update: TaskUpdate) -> Optional[TaskResponse]:
    """Updates an existing task."""
    current = get_task(task_id)
    if not current:
        return None
        
    now_iso = datetime.now(timezone.utc).isoformat()
    title = update.title if update.title is not None else current.title
    description = update.description if update.description is not None else current.description
    due_date = update.due_date if update.due_date is not None else current.due_date
    priority = update.priority.value if update.priority is not None else current.priority.value
    status = update.status.value if update.status is not None else current.status.value
    category = update.category.value if update.category is not None else current.category.value
    recurrence = update.recurrence if update.recurrence is not None else current.recurrence
    is_confirmed = (1 if update.is_confirmed else 0) if update.is_confirmed is not None else (1 if current.is_confirmed else 0)
    
    completed_at = now_iso if status == TaskStatusEnum.COMPLETED.value and current.status != TaskStatusEnum.COMPLETED else (
        None if status != TaskStatusEnum.COMPLETED.value else current.completed_at
    )

    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            UPDATE tasks SET
                title = ?,
                description = ?,
                due_date = ?,
                priority = ?,
                status = ?,
                category = ?,
                recurrence = ?,
                is_confirmed = ?,
                updated_at = ?,
                completed_at = ?
            WHERE id = ?;
            """, (
                title, description, due_date, priority, status, category,
                recurrence, is_confirmed, now_iso, completed_at, task_id
            ))
        return get_task(task_id)
    finally:
        conn.close()

def complete_task(task_id: str) -> Optional[TaskResponse]:
    """Marks task as completed and records completion timestamp honestly."""
    return update_task(task_id, TaskUpdate(status=TaskStatusEnum.COMPLETED))

def delete_task(task_id: str) -> bool:
    """Deletes task and its cascades."""
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.execute("DELETE FROM tasks WHERE id = ?;", (task_id,))
            return cur.rowcount > 0
    finally:
        conn.close()
