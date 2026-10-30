"""Academic models for College Attendance, Absence Tracking, and Assignments."""
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class AttendanceStatusEnum(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"

class AssignmentStatusEnum(str, Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"

class AttendanceRecordCreate(BaseModel):
    subject: str = Field(..., min_length=1, max_length=100)
    status: AttendanceStatusEnum = AttendanceStatusEnum.PRESENT
    date: Optional[str] = None  # YYYY-MM-DD
    period: int = 1
    notes: Optional[str] = None

class AttendanceRecord(BaseModel):
    id: str
    subject: str
    status: AttendanceStatusEnum
    date: str
    period: int
    notes: Optional[str] = None
    created_at: str

class SubjectAttendanceSummary(BaseModel):
    subject: str
    total_classes: int
    attended: int
    absent: int
    percentage: float
    is_safe: bool  # True if percentage >= 75.0
    classes_needed_for_75: int

class OverallAttendanceSummary(BaseModel):
    total_classes: int
    total_attended: int
    total_absent: int
    overall_percentage: float
    is_safe: bool
    subjects: List[SubjectAttendanceSummary]
    recent_absences: List[AttendanceRecord]

class AssignmentCreate(BaseModel):
    subject: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: str = Field(..., description="Due date in YYYY-MM-DD format")
    max_marks: float = 100.0

class AssignmentUpdate(BaseModel):
    status: Optional[AssignmentStatusEnum] = None
    marks_obtained: Optional[float] = None
    description: Optional[str] = None

class Assignment(BaseModel):
    id: str
    subject: str
    title: str
    description: Optional[str] = None
    due_date: str
    status: AssignmentStatusEnum
    marks_obtained: Optional[float] = None
    max_marks: float
    submitted_at: Optional[str] = None
    created_at: str

