"""Tests for Academic Attendance, Absence Tracking, Assignments, and PDF generation."""
import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db
from app.services import academic_service, messaging_bot_service

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_attendance_and_absence_logging():
    # Mark classes
    p1 = academic_service.mark_attendance("Operating Systems", "PRESENT", notes="Lab")
    assert p1.subject == "Operating Systems"
    assert p1.status.value == "PRESENT"

    a1 = academic_service.mark_attendance("Operating Systems", "ABSENT", notes="Sick leave")
    assert a1.status.value == "ABSENT"

    # Verify summary
    summary = academic_service.get_attendance_summary()
    assert summary.total_classes >= 2
    os_sub = next(s for s in summary.subjects if s.subject == "Operating Systems")
    assert os_sub.total_classes >= 2

def test_assignments_workflow():
    # Create assignment
    ass = academic_service.add_assignment(
        subject="Compiler Design",
        title="Lexical Analyzer in C",
        due_date="2026-11-20",
        max_marks=50.0
    )
    assert ass.title == "Lexical Analyzer in C"
    assert ass.status.value == "PENDING"

    # Update assignment to submitted
    up = academic_service.update_assignment_status(ass.id, "SUBMITTED")
    assert up is not None
    assert up.status.value == "SUBMITTED"

    # Grade assignment
    graded = academic_service.update_assignment_status(ass.id, "GRADED", marks_obtained=48.0)
    assert graded.marks_obtained == 48.0
    assert graded.status.value == "GRADED"

def test_academic_pdf_report_generation():
    pdf_path = academic_service.generate_academic_pdf_report()
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000

def test_academic_bot_commands():
    # Test /attendance
    att_resp = messaging_bot_service.handle_incoming_text("test_user", "telegram", "/attendance")
    assert "ATTENDANCE" in att_resp

    # Test /absent
    ab_resp = messaging_bot_service.handle_incoming_text("test_user", "telegram", "/absent Compiler Design")
    assert "Absence Noted" in ab_resp
    assert "Compiler Design" in ab_resp

    # Test /assignments
    ass_resp = messaging_bot_service.handle_incoming_text("test_user", "telegram", "/assignments")
    assert "ASSIGNMENTS" in ass_resp

def test_academic_api_endpoints():
    # GET summary
    res1 = client.get("/api/academic/attendance/summary")
    assert res1.status_code == 200
    assert "overall_percentage" in res1.json()

    # GET PDF report
    res2 = client.get("/api/academic/report/pdf")
    assert res2.status_code == 200
    assert res2.headers["content-type"] == "application/pdf"

