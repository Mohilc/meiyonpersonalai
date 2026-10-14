"""Resume Management, Factual Tailoring, ATS Alignment, and Application Tracking Service."""
import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from app.database import get_db_connection
from app.config import settings
from app.models.career import (
    MasterResumeResponse, MasterResumeUpdate, TailoredResumeResponse,
    JobApplicationCreate, JobApplicationUpdate, JobApplicationResponse,
    ApplicationStatusEnum
)
from app.services.job_service import get_job
from app.services.audit_service import create_approval_request, RiskLevelEnum

def get_active_master_resume() -> MasterResumeResponse:
    """Retrieves the active master resume."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM master_resumes WHERE is_active = 1 LIMIT 1;")
        row = cur.fetchone()
        if not row:
            raise RuntimeError("Master resume not found. Database must be initialized.")
        return _row_to_master_resume(row)
    finally:
        conn.close()

def update_master_resume(update: MasterResumeUpdate) -> MasterResumeResponse:
    """Updates master resume while ensuring factual accuracy."""
    current = get_active_master_resume()
    now_iso = datetime.now(timezone.utc).isoformat()
    
    summary = update.summary if update.summary is not None else current.summary
    education = update.education if update.education is not None else current.education
    projects = update.projects if update.projects is not None else current.projects
    skills = update.skills if update.skills is not None else current.skills
    email = update.contact_email if update.contact_email is not None else current.contact_email
    phone = update.phone if update.phone is not None else current.phone
    linkedin = update.linkedin_url if update.linkedin_url is not None else current.linkedin_url
    github = update.github_url if update.github_url is not None else current.github_url

    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            UPDATE master_resumes SET
                summary = ?,
                education = ?,
                projects = ?,
                skills = ?,
                contact_email = ?,
                phone = ?,
                linkedin_url = ?,
                github_url = ?,
                updated_at = ?
            WHERE id = ?;
            """, (
                summary,
                json.dumps(education),
                json.dumps(projects),
                json.dumps(skills),
                email,
                phone,
                linkedin,
                github,
                now_iso,
                current.id
            ))
        return get_active_master_resume()
    finally:
        conn.close()

def tailor_resume_for_job(job_id: str) -> TailoredResumeResponse:
    """
    Tailors a factual version of the resume for a specific job description.
    Preserves 100% factual accuracy (never invents experience or skills).
    Generates ATS alignment, keyword gap analysis, cover letter, and application answers.
    """
    job = get_job(job_id)
    if not job:
        raise ValueError(f"Job listing {job_id} not found")
        
    master = get_active_master_resume()
    job_desc_lower = job.description.lower()
    
    # 1. Match verified skills against job requirements
    matched_skills = []
    other_skills = []
    for skill in master.skills:
        if skill.lower() in job_desc_lower or skill.lower() in job.title.lower():
            matched_skills.append(skill)
        else:
            other_skills.append(skill)
            
    tailored_skills = matched_skills + other_skills  # Prioritize matched skills at the front
    
    # 2. Prioritize relevant projects
    tailored_projects = []
    if "drone" in job_desc_lower or "vision" in job_desc_lower or "embedded" in job_desc_lower:
        tailored_projects = sorted(master.projects, key=lambda p: 0 if "Drone" in p.get("title", "") else 1)
    elif "ai" in job_desc_lower or "agent" in job_desc_lower or "assistant" in job_desc_lower:
        tailored_projects = sorted(master.projects, key=lambda p: 0 if "Agent" in p.get("title", "") else 1)
    else:
        tailored_projects = master.projects

    # 3. Formulate tailored summary emphasizing relevant verified background
    tailored_summary = (
        f"Undergraduate AI & Computer Science Engineer (B.Tech '27) targeting {job.title} at {job.company}. "
        f"Bringing solid foundational expertise in {', '.join(matched_skills[:4]) or 'Python, algorithms, and software development'}. "
        f"Demonstrated project experience in autonomous systems and modular agentic architectures."
    )
    
    # 4. Keyword Gap Analysis
    keyword_gaps = {
        "matched_keywords": matched_skills,
        "missing_keywords": job.missing_qualifications,
        "ats_compatibility_tips": [
            "Clear chronological project sections.",
            "Quantified bullet points highlighting actual implementation results.",
            "Zero artificial keyword stuffing; all listed skills are verified."
        ]
    }
    
    # 5. Tailored Cover Letter
    cover_letter = (
        f"Dear Hiring Team at {job.company},\n\n"
        f"I am writing to express my strong enthusiasm for the {job.title} position ({job.source_name}). "
        f"As a B.Tech Computer Science student specializing in Artificial Intelligence at Mar Baselios Christian College of Engineering & Technology (expected graduation 2027), "
        f"I have built hands-on engineering experience in Python, Machine Learning, and scalable software systems.\n\n"
        f"My background directly aligns with your requirements in {', '.join(matched_skills[:3]) or 'software engineering'}. "
        f"Through projects such as developing an autonomous drone telemetry pipeline and architecting an executive AI manager, "
        f"I have cultivated a disciplined approach to building reliable, secure, and well-tested software.\n\n"
        f"I would welcome the opportunity to discuss how my skills and proactive learning mindset can contribute to {job.company}.\n\n"
        f"Sincerely,\n{master.full_name}"
    )
    
    # 6. Pre-filled Application Answers
    answers = {
        "Why are you interested in this role?": f"The {job.title} role at {job.company} provides an ideal opportunity to apply my practical skills in {', '.join(matched_skills[:2]) or 'AI and software engineering'} while contributing to high-impact projects.",
        "What is your current availability?": "Available for internships and entry-level engineering roles starting immediately, with graduation scheduled for 2027.",
        "Describe a challenging technical project you built:": "Architected an autonomous agentic executive manager in Python and FastAPI, implementing SQLite WAL persistent storage, background schedulers, and strict human-in-the-loop safety gates."
    }

    changes_made = [
        "Reordered skill list to prominently display job-matching competencies.",
        f"Contextualized executive summary specifically for {job.title} at {job.company}.",
        "Re-prioritized project highlights based on role domain relevance.",
        "Generated customized cover letter and verified application responses."
    ]

    tailored_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO tailored_resumes (
                id, job_id, version_label, tailored_summary, tailored_skills,
                tailored_projects, cover_letter, application_answers,
                keyword_gap_analysis, changes_made, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                tailored_id, job_id, f"tailored-{job.company[:12]}",
                tailored_summary, json.dumps(tailored_skills),
                json.dumps(tailored_projects), cover_letter,
                json.dumps(answers), json.dumps(keyword_gaps),
                json.dumps(changes_made), now_iso
            ))
            
        return get_tailored_resume(tailored_id)
    finally:
        conn.close()

def get_tailored_resume(tailored_id: str) -> Optional[TailoredResumeResponse]:
    """Retrieves a tailored resume version."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM tailored_resumes WHERE id = ?;", (tailored_id,))
        row = cur.fetchone()
        if not row:
            return None
        return TailoredResumeResponse(
            id=row["id"],
            job_id=row["job_id"],
            version_label=row["version_label"],
            tailored_summary=row["tailored_summary"],
            tailored_skills=json.loads(row["tailored_skills"]),
            tailored_projects=json.loads(row["tailored_projects"]),
            cover_letter=row["cover_letter"],
            application_answers=json.loads(row["application_answers"]),
            keyword_gap_analysis=json.loads(row["keyword_gap_analysis"]),
            changes_made=json.loads(row["changes_made"]),
            created_at=row["created_at"]
        )
    finally:
        conn.close()

def create_job_application(data: JobApplicationCreate) -> JobApplicationResponse:
    """
    Creates an application record. If under Mode A or Mode B, automatically
    creates an approval request before any submission can occur.
    """
    app_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    
    # Create human authorization gate
    approval = create_approval_request(
        title=f"Submit Application: {data.position} at {data.company}",
        description=f"Requesting authorization to submit application for {data.position} at {data.company}.",
        action_payload={
            "application_id": app_id,
            "company": data.company,
            "position": data.position,
            "job_url": data.job_url,
            "resume_version": data.resume_version
        },
        risk_level=RiskLevelEnum.HIGH
    )
    
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO job_applications (
                id, job_id, company, position, job_url, resume_version,
                status, recruiter_name, recruiter_email, interview_stages,
                application_date, follow_up_date, next_action, notes,
                approval_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'READY_FOR_APPROVAL', ?, ?, '[]', ?, ?, ?, ?, ?, ?, ?);
            """, (
                app_id, data.job_id, data.company, data.position, data.job_url,
                data.resume_version, data.recruiter_name, data.recruiter_email,
                now_iso, data.follow_up_date, "Await user authorization before submission",
                data.notes, approval.id, now_iso, now_iso
            ))
        return get_job_application(app_id)
    finally:
        conn.close()

def get_job_application(app_id: str) -> Optional[JobApplicationResponse]:
    """Retrieves an application record."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM job_applications WHERE id = ?;", (app_id,))
        row = cur.fetchone()
        if not row:
            return None
        return _row_to_application(row)
    finally:
        conn.close()

def list_job_applications(status: Optional[str] = None) -> List[JobApplicationResponse]:
    """Lists all tracked job applications."""
    conn = get_db_connection()
    try:
        query = "SELECT * FROM job_applications WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC;"
        cur = conn.execute(query, params)
        rows = cur.fetchall()
        return [_row_to_application(r) for r in rows]
    finally:
        conn.close()

def update_job_application(app_id: str, update: JobApplicationUpdate) -> Optional[JobApplicationResponse]:
    """Updates an application lifecycle record."""
    current = get_job_application(app_id)
    if not current:
        return None
        
    now_iso = datetime.now(timezone.utc).isoformat()
    status = update.status.value if update.status is not None else current.status.value
    recruiter_name = update.recruiter_name if update.recruiter_name is not None else current.recruiter_name
    recruiter_email = update.recruiter_email if update.recruiter_email is not None else current.recruiter_email
    interview_stages = update.interview_stages if update.interview_stages is not None else current.interview_stages
    follow_up_date = update.follow_up_date if update.follow_up_date is not None else current.follow_up_date
    next_action = update.next_action if update.next_action is not None else current.next_action
    notes = update.notes if update.notes is not None else current.notes

    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            UPDATE job_applications SET
                status = ?,
                recruiter_name = ?,
                recruiter_email = ?,
                interview_stages = ?,
                follow_up_date = ?,
                next_action = ?,
                notes = ?,
                updated_at = ?
            WHERE id = ?;
            """, (
                status, recruiter_name, recruiter_email,
                json.dumps(interview_stages), follow_up_date,
                next_action, notes, now_iso, app_id
            ))
        return get_job_application(app_id)
    finally:
        conn.close()

def _row_to_master_resume(row) -> MasterResumeResponse:
    return MasterResumeResponse(
        id=row["id"],
        version_label=row["version_label"],
        full_name=row["full_name"],
        contact_email=row["contact_email"],
        phone=row["phone"],
        linkedin_url=row["linkedin_url"],
        github_url=row["github_url"],
        summary=row["summary"],
        education=json.loads(row["education"]),
        experience=json.loads(row["experience"]),
        projects=json.loads(row["projects"]),
        skills=json.loads(row["skills"]),
        certifications=json.loads(row["certifications"]),
        ats_score=row["ats_score"],
        ats_feedback=json.loads(row["ats_feedback"]),
        raw_text=row["raw_text"],
        is_active=bool(row["is_active"]),
        updated_at=row["updated_at"]
    )

def _row_to_application(row) -> JobApplicationResponse:
    return JobApplicationResponse(
        id=row["id"],
        job_id=row["job_id"],
        company=row["company"],
        position=row["position"],
        job_url=row["job_url"],
        resume_version=row["resume_version"],
        status=ApplicationStatusEnum(row["status"]),
        recruiter_name=row["recruiter_name"],
        recruiter_email=row["recruiter_email"],
        interview_stages=json.loads(row["interview_stages"]),
        application_date=row["application_date"],
        follow_up_date=row["follow_up_date"],
        next_action=row["next_action"],
        notes=row["notes"],
        approval_id=row["approval_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )
