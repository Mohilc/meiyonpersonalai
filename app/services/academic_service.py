"""Academic Service for Attendance Tracking, Absence Logging, Assignment Marking, and PDF Generation."""
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any

from app.database import get_db_connection
from app.models.academic import (
    AttendanceRecord,
    AttendanceRecordCreate,
    AttendanceStatusEnum,
    SubjectAttendanceSummary,
    OverallAttendanceSummary,
    Assignment,
    AssignmentCreate,
    AssignmentUpdate,
    AssignmentStatusEnum
)
from app.services import profile_service

logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def mark_attendance(
    subject: str,
    status: str = "PRESENT",
    date: Optional[str] = None,
    period: int = 1,
    notes: Optional[str] = None
) -> AttendanceRecord:
    """Records class attendance (PRESENT or ABSENT)."""
    conn = get_db_connection()
    rec_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    record_date = date or datetime.now().strftime("%Y-%m-%d")
    status_clean = status.upper().strip()
    if status_clean not in ("PRESENT", "ABSENT"):
        status_clean = "PRESENT"

    with conn:
        conn.execute("""
            INSERT INTO attendance_records (id, subject, status, date, period, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (rec_id, subject.strip(), status_clean, record_date, period, notes, now_iso))

    return AttendanceRecord(
        id=rec_id,
        subject=subject.strip(),
        status=AttendanceStatusEnum(status_clean),
        date=record_date,
        period=period,
        notes=notes,
        created_at=now_iso
    )


def get_absent_history(limit: int = 50) -> List[AttendanceRecord]:
    """Retrieves all logged absences ordered by date descending."""
    conn = get_db_connection()
    cur = conn.execute("""
        SELECT id, subject, status, date, period, notes, created_at
        FROM attendance_records
        WHERE status = 'ABSENT'
        ORDER BY date DESC, created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    return [
        AttendanceRecord(
            id=r["id"],
            subject=r["subject"],
            status=AttendanceStatusEnum(r["status"]),
            date=r["date"],
            period=r["period"],
            notes=r["notes"],
            created_at=r["created_at"]
        ) for r in rows
    ]


def get_attendance_summary() -> OverallAttendanceSummary:
    """Computes overall and per-subject attendance percentages with 75% threshold analysis."""
    conn = get_db_connection()
    cur = conn.execute("""
        SELECT subject, status, COUNT(*) as count
        FROM attendance_records
        GROUP BY subject, status
    """)
    rows = cur.fetchall()

    subject_data: Dict[str, Dict[str, int]] = {}
    total_classes = 0
    total_attended = 0
    total_absent = 0

    for r in rows:
        sub = r["subject"]
        st = r["status"]
        cnt = r["count"]
        if sub not in subject_data:
            subject_data[sub] = {"attended": 0, "absent": 0}
        if st == "PRESENT":
            subject_data[sub]["attended"] += cnt
            total_attended += cnt
        elif st == "ABSENT":
            subject_data[sub]["absent"] += cnt
            total_absent += cnt
        total_classes += cnt

    subjects_summary: List[SubjectAttendanceSummary] = []
    for sub, counts in sorted(subject_data.items()):
        att = counts["attended"]
        ab = counts["absent"]
        tot = att + ab
        pct = round((att / tot) * 100.0, 1) if tot > 0 else 100.0
        is_safe = pct >= 75.0

        # Calculate how many consecutive classes are needed to reach 75%
        # (att + x) / (tot + x) >= 0.75  =>  att + x >= 0.75*tot + 0.75*x  =>  0.25*x >= 0.75*tot - att
        needed = 0
        if pct < 75.0 and tot > 0:
            import math
            needed = max(0, math.ceil((0.75 * tot - att) / 0.25))

        subjects_summary.append(SubjectAttendanceSummary(
            subject=sub,
            total_classes=tot,
            attended=att,
            absent=ab,
            percentage=pct,
            is_safe=is_safe,
            classes_needed_for_75=needed
        ))

    overall_pct = round((total_attended / total_classes) * 100.0, 1) if total_classes > 0 else 100.0
    recent_absences = get_absent_history(limit=10)

    return OverallAttendanceSummary(
        total_classes=total_classes,
        total_attended=total_attended,
        total_absent=total_absent,
        overall_percentage=overall_pct,
        is_safe=overall_pct >= 75.0,
        subjects=subjects_summary,
        recent_absences=recent_absences
    )


# ---------------- Assignments ----------------

def add_assignment(
    subject: str,
    title: str,
    due_date: str,
    description: Optional[str] = None,
    max_marks: float = 100.0
) -> Assignment:
    """Adds a new academic assignment."""
    conn = get_db_connection()
    ass_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    with conn:
        conn.execute("""
            INSERT INTO assignments (id, subject, title, description, due_date, status, max_marks, created_at)
            VALUES (?, ?, ?, ?, ?, 'PENDING', ?, ?)
        """, (ass_id, subject.strip(), title.strip(), description, due_date.strip(), max_marks, now_iso))

    return Assignment(
        id=ass_id,
        subject=subject.strip(),
        title=title.strip(),
        description=description,
        due_date=due_date.strip(),
        status=AssignmentStatusEnum.PENDING,
        max_marks=max_marks,
        created_at=now_iso
    )


def list_assignments(status: Optional[str] = None) -> List[Assignment]:
    """Retrieves list of assignments optionally filtered by status."""
    conn = get_db_connection()
    if status:
        cur = conn.execute("""
            SELECT id, subject, title, description, due_date, status, marks_obtained, max_marks, submitted_at, created_at
            FROM assignments
            WHERE status = ?
            ORDER BY due_date ASC
        """, (status.upper(),))
    else:
        cur = conn.execute("""
            SELECT id, subject, title, description, due_date, status, marks_obtained, max_marks, submitted_at, created_at
            FROM assignments
            ORDER BY CASE status WHEN 'PENDING' THEN 1 WHEN 'SUBMITTED' THEN 2 ELSE 3 END, due_date ASC
        """)

    rows = cur.fetchall()
    return [
        Assignment(
            id=r["id"],
            subject=r["subject"],
            title=r["title"],
            description=r["description"],
            due_date=r["due_date"],
            status=AssignmentStatusEnum(r["status"]),
            marks_obtained=r["marks_obtained"],
            max_marks=r["max_marks"],
            submitted_at=r["submitted_at"],
            created_at=r["created_at"]
        ) for r in rows
    ]


def update_assignment_status(
    assignment_id: str,
    status: str,
    marks_obtained: Optional[float] = None,
    description: Optional[str] = None
) -> Optional[Assignment]:
    """Updates an assignment status and marks obtained."""
    conn = get_db_connection()
    status_clean = status.upper().strip()
    now_iso = datetime.now(timezone.utc).isoformat()
    submitted_at = now_iso if status_clean in ("SUBMITTED", "GRADED") else None

    with conn:
        cur = conn.execute("SELECT id FROM assignments WHERE id = ? OR id LIKE ?", (assignment_id, f"{assignment_id}%"))
        row = cur.fetchone()
        if not row:
            return None
        real_id = row["id"]

        conn.execute("""
            UPDATE assignments
            SET status = ?, marks_obtained = COALESCE(?, marks_obtained), submitted_at = COALESCE(?, submitted_at)
            WHERE id = ?
        """, (status_clean, marks_obtained, submitted_at, real_id))

    assignments = list_assignments()
    return next((a for a in assignments if a.id == real_id), None)


# ---------------- PDF Report Generation ----------------

def generate_academic_pdf_report(output_filename: Optional[str] = None) -> str:
    """
    Generates a professional executive PDF report containing:
    - College & Student details
    - Attendance summary and subject-wise breakdown with >=75% compliance
    - Detailed Absence Log
    - Assignments & Marks Status
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    summary = get_attendance_summary()
    assignments = list_assignments()
    absences = get_absent_history(limit=30)
    profile = profile_service.get_profile()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_filename or f"attendance_academic_report_{timestamp}.pdf"
    pdf_path = REPORTS_DIR / filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom palette
    PRIMARY = colors.HexColor("#1A365D")    # Deep Navy
    SECONDARY = colors.HexColor("#2B6CB0")  # Slate Blue
    ACCENT = colors.HexColor("#2C5282")
    SUCCESS = colors.HexColor("#22543D")   # Forest Green
    WARNING = colors.HexColor("#9B2C2C")   # Crimson Red
    BG_LIGHT = colors.HexColor("#F7FAFC")
    BORDER = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=SECONDARY
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2D3748")
    )
    bold_cell = ParagraphStyle(
        'BoldCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1A202C")
    )
    kpi_number = ParagraphStyle(
        'KPINumber',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=PRIMARY
    )
    kpi_label = ParagraphStyle(
        'KPILabel',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#718096")
    )

    story = []

    # 1. Header Banner
    college_name = profile.college or "Mar Baselios Christian College of Engineering & Technology"
    student_name = profile.full_name or "Mohil"
    degree = profile.education or "B.Tech Computer Science with Artificial Intelligence ('27)"

    story.append(Paragraph("ACADEMIC ATTENDANCE & ASSIGNMENT REPORT", title_style))
    story.append(Paragraph(f"<b>Institution:</b> {college_name}<br/><b>Student:</b> {student_name} | {degree} | <b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceBefore=4, spaceAfter=14))

    # 2. KPI Summary Cards Table
    overall_color = SUCCESS if summary.is_safe else WARNING
    kpi_data = [
        [
            Paragraph(f"<font color='{overall_color.hexval()}'>{summary.overall_percentage}%</font>", kpi_number),
            Paragraph(f"{summary.total_attended} / {summary.total_classes}", kpi_number),
            Paragraph(f"<font color='{WARNING.hexval()}'>{summary.total_absent}</font>", kpi_number),
            Paragraph(f"{len([a for a in assignments if a.status == AssignmentStatusEnum.PENDING])}", kpi_number)
        ],
        [
            Paragraph("Overall Attendance", kpi_label),
            Paragraph("Classes Attended", kpi_label),
            Paragraph("Total Absences", kpi_label),
            Paragraph("Pending Assignments", kpi_label)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[130, 130, 130, 130])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 16))

    # 3. Subject-wise Attendance Breakdown
    story.append(Paragraph("Subject-Wise Attendance Status (Minimum Requirement: 75%)", section_heading))

    sub_header = [
        Paragraph("<b>Subject</b>", bold_cell),
        Paragraph("<b>Total</b>", bold_cell),
        Paragraph("<b>Attended</b>", bold_cell),
        Paragraph("<b>Absent</b>", bold_cell),
        Paragraph("<b>Attendance %</b>", bold_cell),
        Paragraph("<b>Status / Action</b>", bold_cell)
    ]
    sub_rows = [sub_header]

    if summary.subjects:
        for s in summary.subjects:
            status_text = "<font color='#22543D'><b>Safe</b></font>" if s.is_safe else f"<font color='#9B2C2C'><b>Needs {s.classes_needed_for_75} classes</b></font>"
            pct_color = "#22543D" if s.is_safe else "#9B2C2C"
            sub_rows.append([
                Paragraph(s.subject, body_style),
                Paragraph(str(s.total_classes), body_style),
                Paragraph(str(s.attended), body_style),
                Paragraph(str(s.absent), body_style),
                Paragraph(f"<font color='{pct_color}'><b>{s.percentage}%</b></font>", body_style),
                Paragraph(status_text, body_style)
            ])
    else:
        sub_rows.append([
            Paragraph("<i>No attendance logged yet. Use /attendance or /absent to start recording.</i>", body_style),
            Paragraph("-", body_style), Paragraph("-", body_style), Paragraph("-", body_style), Paragraph("-", body_style), Paragraph("-", body_style)
        ])

    sub_table = Table(sub_rows, colWidths=[170, 50, 60, 50, 80, 110])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, PRIMARY),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 16))

    # 4. Detailed Absenteeism Log
    story.append(Paragraph("Detailed Absenteeism Log", section_heading))
    ab_header = [
        Paragraph("<b>Date</b>", bold_cell),
        Paragraph("<b>Subject</b>", bold_cell),
        Paragraph("<b>Period</b>", bold_cell),
        Paragraph("<b>Notes / Reason</b>", bold_cell)
    ]
    ab_rows = [ab_header]
    if absences:
        for ab in absences:
            ab_rows.append([
                Paragraph(ab.date, body_style),
                Paragraph(ab.subject, body_style),
                Paragraph(f"Period {ab.period}", body_style),
                Paragraph(ab.notes or "Absent noted", body_style)
            ])
    else:
        ab_rows.append([
            Paragraph("-", body_style),
            Paragraph("<i>Zero absences recorded! Perfect 100% attendance.</i>", body_style),
            Paragraph("-", body_style),
            Paragraph("-", body_style)
        ])

    ab_table = Table(ab_rows, colWidths=[90, 150, 70, 210])
    ab_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, PRIMARY),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(ab_table)
    story.append(Spacer(1, 16))

    # 5. Assignments & Marking Table
    story.append(Paragraph("Assignment Tracker & Evaluation", section_heading))
    as_header = [
        Paragraph("<b>Subject</b>", bold_cell),
        Paragraph("<b>Assignment Title</b>", bold_cell),
        Paragraph("<b>Due Date</b>", bold_cell),
        Paragraph("<b>Status</b>", bold_cell),
        Paragraph("<b>Marks</b>", bold_cell)
    ]
    as_rows = [as_header]
    if assignments:
        for a in assignments:
            st_color = "#D69E2E" if a.status == AssignmentStatusEnum.PENDING else ("#3182CE" if a.status == AssignmentStatusEnum.SUBMITTED else "#22543D")
            marks_str = f"{a.marks_obtained}/{a.max_marks}" if a.marks_obtained is not None else f"-/{a.max_marks}"
            as_rows.append([
                Paragraph(a.subject, body_style),
                Paragraph(a.title, body_style),
                Paragraph(a.due_date, body_style),
                Paragraph(f"<font color='{st_color}'><b>{a.status.value}</b></font>", body_style),
                Paragraph(marks_str, body_style)
            ])
    else:
        as_rows.append([
            Paragraph("<i>No assignments logged yet.</i>", body_style),
            Paragraph("-", body_style), Paragraph("-", body_style), Paragraph("-", body_style), Paragraph("-", body_style)
        ])

    as_table = Table(as_rows, colWidths=[120, 160, 80, 80, 80])
    as_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, PRIMARY),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(as_table)
    story.append(Spacer(1, 20))

    # Footer notice
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph("<i>Meiyon Personal AI Manager & Chief of Staff • Confidential Academic Record</i>", ParagraphStyle(
        'FooterNotice',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.HexColor("#A0AEC0"),
        alignment=1
    )))

    doc.build(story)
    logger.info("Academic PDF report generated successfully at: %s", str(pdf_path))
    return str(pdf_path)
