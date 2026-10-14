"""Task and Reminder data models."""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class PriorityEnum(str, Enum):
    P1_URGENT = "P1_URGENT"
    P2_HIGH = "P2_HIGH"
    P3_MEDIUM = "P3_MEDIUM"
    P4_LOW = "P4_LOW"

class TaskStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    BLOCKED = "BLOCKED"

class CategoryEnum(str, Enum):
    STUDY = "STUDY"
    JOB_SEARCH = "JOB_SEARCH"
    PROJECT = "PROJECT"
    COMMUNICATION = "COMMUNICATION"
    PERSONAL = "PERSONAL"
    EXAM = "EXAM"
    ADMIN = "ADMIN"

class TaskSourceEnum(str, Enum):
    MANUAL = "MANUAL"
    EMAIL_INFERRED = "EMAIL_INFERRED"
    AGENT_PLANNED = "AGENT_PLANNED"
    JOB_DEADLINE = "JOB_DEADLINE"

class ReminderStatusEnum(str, Enum):
    SCHEDULED = "SCHEDULED"
    DELIVERED = "DELIVERED"
    SNOOZED = "SNOOZED"
    DISMISSED = "DISMISSED"
    FAILED = "FAILED"

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[str] = None  # ISO format: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD
    priority: PriorityEnum = PriorityEnum.P3_MEDIUM
    category: CategoryEnum = CategoryEnum.PERSONAL
    source: TaskSourceEnum = TaskSourceEnum.MANUAL
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    recurrence: Optional[str] = None
    is_confirmed: bool = True
    reminder_minutes_before: Optional[int] = None  # Auto-schedule a reminder N minutes before due_date

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[TaskStatusEnum] = None
    category: Optional[CategoryEnum] = None
    recurrence: Optional[str] = None
    is_confirmed: Optional[bool] = None

class ReminderCreate(BaseModel):
    task_id: str
    remind_at: str
    channel: str = "DASHBOARD"
    delivery_message: Optional[str] = None

class ReminderResponse(BaseModel):
    id: str
    task_id: str
    remind_at: str
    status: ReminderStatusEnum
    channel: str
    delivery_message: Optional[str] = None
    delivery_timestamp: Optional[str] = None
    snooze_count: int
    created_at: str

class ReminderSnooze(BaseModel):
    snooze_minutes: int = 15

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: PriorityEnum
    status: TaskStatusEnum
    category: CategoryEnum
    source: TaskSourceEnum
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    recurrence: Optional[str] = None
    is_confirmed: bool
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    reminders: List[ReminderResponse] = []
