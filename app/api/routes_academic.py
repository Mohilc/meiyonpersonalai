"""Academic API routes for Attendance, Absences, Assignments, and PDF generation."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse
from pathlib import Path

from app.models.academic import (
    AttendanceRecord,
    AttendanceRecordCreate,
    OverallAttendanceSummary,
    Assignment,
    AssignmentCreate,
    AssignmentUpdate
)
from app.services import academic_service

router = APIRouter(prefix="/api/academic", tags=["Academic & Attendance"])


@router.post("/attendance", response_model=AttendanceRecord)
def record_attendance(payload: AttendanceRecordCreate):
    """Marks attendance (PRESENT or ABSENT) for a subject and date."""
    return academic_service.mark_attendance(
        subject=payload.subject,
        status=payload.status.value,
        date=payload.date,
        period=payload.period,
        notes=payload.notes
    )


@router.get("/attendance/summary", response_model=OverallAttendanceSummary)
def get_attendance_summary():
    """Returns overall and subject-wise attendance percentages, safe status, and absence logs."""
    return academic_service.get_attendance_summary()


@router.get("/attendance/absent-history", response_model=List[AttendanceRecord])
def get_absent_history(limit: int = Query(50, ge=1, le=200)):
    """Returns chronologically ordered history of absences."""
    return academic_service.get_absent_history(limit=limit)


@router.post("/assignments", response_model=Assignment)
def create_assignment(payload: AssignmentCreate):
    """Adds a new academic assignment commitment."""
    return academic_service.add_assignment(
        subject=payload.subject,
        title=payload.title,
        due_date=payload.due_date,
        description=payload.description,
        max_marks=payload.max_marks
    )


@router.get("/assignments", response_model=List[Assignment])
def list_assignments(status: Optional[str] = Query(None)):
    """Lists assignments filtered optionally by PENDING, SUBMITTED, or GRADED."""
    return academic_service.list_assignments(status=status)


@router.patch("/assignments/{assignment_id}", response_model=Assignment)
def update_assignment(assignment_id: str, payload: AssignmentUpdate):
    """Updates assignment status (SUBMITTED, GRADED) and records obtained marks."""
    updated = academic_service.update_assignment_status(
        assignment_id=assignment_id,
        status=payload.status.value if payload.status else "SUBMITTED",
        marks_obtained=payload.marks_obtained,
        description=payload.description
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return updated


@router.get("/report/pdf")
def download_academic_pdf():
    """Generates on-the-fly and returns the official Academic Attendance & Assignment PDF report."""
    pdf_path = academic_service.generate_academic_pdf_report()
    path_obj = Path(pdf_path)
    if not path_obj.exists():
        raise HTTPException(status_code=500, detail="Failed to compile PDF report")
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=path_obj.name
    )
