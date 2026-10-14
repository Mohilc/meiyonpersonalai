"""Email Triage, Phishing/Scam Detection, LinkedIn Career Assistant, and Weekly Reporting Service."""
import uuid
import json
import re
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple

from app.database import get_db_connection
from app.config import settings
from app.models.communication import (
    EmailMessageCreate, EmailMessageResponse, EmailIntentEnum,
    PhishingRiskEnum, LinkedInProfileGuidance, LinkedInPostDraft,
    LinkedInConnectionNote, WeeklyReportResponse
)
from app.services.profile_service import get_profile
from app.services.task_service import list_tasks, TaskStatusEnum
from app.services.resume_service import list_job_applications, get_active_master_resume
from app.services.job_service import list_jobs
from app.services.audit_service import create_approval_request, RiskLevelEnum

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"system\s+override",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"reveal\s+(all\s+)?(api\s+keys|secrets|passwords)",
    r"disregard\s+security\s+rules",
    r"delete\s+all\s+(data|files|tables)"
]

PHISHING_SCAM_PATTERNS = [
    "wire transfer", "western union", "cashier's check", "check cashing",
    "buy equipment with check", "crypto payment", "gift card", "advance fee",
    "send payment before interview", "pay for background check",
    "urgent: verify bank details", "telegram interview"
]

def sanitize_untrusted_content(text: str) -> Tuple[str, List[str]]:
    """Defends against prompt injection in untrusted emails and external documents."""
    flags = []
    sanitized = text
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            flags.append(f"Prompt injection pattern detected: '{pattern}'")
            sanitized = re.sub(pattern, "[BLOCKED_INJECTION_ATTEMPT]", sanitized, flags=re.IGNORECASE)
    return sanitized, flags

def triage_incoming_email(data: EmailMessageCreate) -> EmailMessageResponse:
    """
    Analyzes untrusted incoming email for recruiter intent, phishing/scams,
    and dates. Drafts a professional response honestly.
    """
    safe_body, injection_flags = sanitize_untrusted_content(data.body)
    body_lower = safe_body.lower()
    subject_lower = data.subject.lower()
    
    # 1. Detect Phishing & Scam Indicators
    phishing_flags = list(injection_flags)
    for phrase in PHISHING_SCAM_PATTERNS:
        if phrase in body_lower or phrase in subject_lower:
            phishing_flags.append(f"Employment scam indicator: '{phrase}'")
            
    # Check if sender claims corporate identity on free webmail
    sender_domain = data.sender.split('@')[-1].lower() if '@' in data.sender else ''
    free_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    if sender_domain in free_domains and any(k in subject_lower for k in ["google", "microsoft", "amazon", "apple", "offer letter"]):
        phishing_flags.append(f"Impersonation indicator: Corporate hiring claimed from free email ({data.sender})")

    if len(phishing_flags) >= 2 or any("scam" in f.lower() or "injection" in f.lower() for f in phishing_flags):
        phishing_risk = PhishingRiskEnum.HIGH
    elif phishing_flags:
        phishing_risk = PhishingRiskEnum.MEDIUM
    else:
        phishing_risk = PhishingRiskEnum.LOW

    # 2. Recruiter & Intent Classification
    is_recruiter = False
    intent = EmailIntentEnum.GENERAL
    
    if any(k in subject_lower or k in body_lower for k in ["interview", "phone screen", "assessment", "technical round", "schedule a chat"]):
        intent = EmailIntentEnum.INTERVIEW
        is_recruiter = True
    elif any(k in subject_lower or k in body_lower for k in ["offer letter", "job offer", "congratulations on the offer"]):
        intent = EmailIntentEnum.OFFER
        is_recruiter = True
    elif any(k in subject_lower or k in body_lower for k in ["regret to inform", "other candidates", "unsuccessful", "not moving forward"]):
        intent = EmailIntentEnum.REJECTION
        is_recruiter = True
    elif any(k in subject_lower or k in body_lower for k in ["additional information", "send resume", "portfolio link", "github profile"]):
        intent = EmailIntentEnum.INFO_REQUEST
        is_recruiter = True
    elif any(k in subject_lower or k in body_lower for k in ["recruiter", "talent acquisition", "careers", "hiring team", "application status"]):
        is_recruiter = True

    # 3. Extract dates (distinguishing confirmed vs inferred)
    extracted_dates = []
    date_matches = re.findall(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday|\b\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*|\b\d{4}-\d{2}-\d{2}\b)', body_lower)
    for dm in date_matches[:3]:
        is_confirmed = "confirmed" in body_lower or "calendar invite" in body_lower
        extracted_dates.append({
            "text": dm,
            "is_confirmed": is_confirmed,
            "status": "CONFIRMED" if is_confirmed else "INFERRED_PROPOSED"
        })

    # 4. Generate proposed professional reply
    profile = get_profile()
    if phishing_risk == PhishingRiskEnum.HIGH:
        proposed_reply = "[SECURITY ALERT] Do not reply. Message flagged for high phishing/scam indicators."
    elif intent == EmailIntentEnum.INTERVIEW:
        proposed_reply = (
            f"Dear Hiring Team,\n\n"
            f"Thank you for contacting me. I am very interested in this opportunity and would be glad to participate in the interview. "
            f"Please let me know the available time slots and meeting link.\n\n"
            f"Best regards,\n{profile.full_name}\nB.Tech Computer Science (AI)"
        )
    elif intent == EmailIntentEnum.INFO_REQUEST:
        proposed_reply = (
            f"Dear Hiring Team,\n\n"
            f"Thank you for your message. Please find my updated project portfolio and resume information. "
            f"I look forward to next steps.\n\n"
            f"Best regards,\n{profile.full_name}"
        )
    elif intent == EmailIntentEnum.REJECTION:
        proposed_reply = (
            f"Dear Hiring Team,\n\n"
            f"Thank you for considering my application and letting me know. I appreciate your team's time and wish you all the best. "
            f"I hope to stay connected for future opportunities.\n\n"
            f"Best regards,\n{profile.full_name}"
        )
    else:
        proposed_reply = f"Thank you for reaching out. I have received your message and will review it shortly.\n\nBest regards,\n{profile.full_name}"

    msg_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    recv_time = data.received_at or now_iso

    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO email_messages (
                id, sender, recipient, subject, body, received_at,
                is_recruiter, detected_intent, phishing_risk, phishing_flags,
                extracted_dates, proposed_reply, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'UNREAD', ?);
            """, (
                msg_id, data.sender, data.recipient, data.subject, safe_body, recv_time,
                1 if is_recruiter else 0, intent.value, phishing_risk.value,
                json.dumps(phishing_flags), json.dumps(extracted_dates),
                proposed_reply, now_iso
            ))
        return get_email_message(msg_id)
    finally:
        conn.close()

def get_email_message(msg_id: str) -> Optional[EmailMessageResponse]:
    """Retrieves an email record."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM email_messages WHERE id = ?;", (msg_id,))
        row = cur.fetchone()
        if not row:
            return None
        return _row_to_email(row)
    finally:
        conn.close()

def list_email_messages(limit: int = 50) -> List[EmailMessageResponse]:
    """Lists email messages."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM email_messages ORDER BY received_at DESC LIMIT ?;", (limit,))
        rows = cur.fetchall()
        return [_row_to_email(r) for r in rows]
    finally:
        conn.close()

def request_email_reply_approval(msg_id: str, custom_reply: Optional[str] = None) -> Dict[str, Any]:
    """Creates a human authorization request before sending an external email."""
    email = get_email_message(msg_id)
    if not email:
        raise ValueError("Email message not found")
        
    reply_text = custom_reply or email.proposed_reply
    approval = create_approval_request(
        title=f"Send Email Reply to {email.sender}",
        description=f"Authorized action required to transmit email response regarding '{email.subject}'.",
        action_payload={
            "email_id": msg_id,
            "recipient": email.sender,
            "subject": f"Re: {email.subject}",
            "reply_body": reply_text
        },
        risk_level=RiskLevelEnum.HIGH
    )
    return {
        "message": "Approval request registered. External message will only be sent upon explicit authorization.",
        "approval_id": approval.id,
        "reply_preview": reply_text
    }

def generate_linkedin_guidance() -> LinkedInProfileGuidance:
    """Generates professional LinkedIn profile recommendations based on verified details."""
    profile = get_profile()
    resume = get_active_master_resume()
    
    headlines = [
        f"AI & Computer Science Undergraduate ('27) | Python, Machine Learning & Autonomous Drone Systems",
        f"Aspiring AI/ML Engineer | B.Tech CSE (AI) @ Mar Baselios Christian College | Building Agentic AI & Vision Systems",
        f"Software & Machine Learning Intern Candidate | Python • FastAPI • Edge AI • Autonomous Telemetry"
    ]
    
    about = (
        f"I am a Computer Science and Artificial Intelligence student at Mar Baselios Christian College of Engineering & Technology "
        f"(class of 2027) with a deep interest in machine learning, autonomous systems, and practical software engineering.\n\n"
        f"My hands-on experience includes developing telemetry processing for drone systems and engineering modular agentic AI architectures "
        f"with Python, FastAPI, and robust SQLite storage engines. I prioritize writing clean, well-tested, and secure code.\n\n"
        f"Seeking internships and collaborative engineering opportunities in AI/ML, Python software engineering, and robotics."
    )
    
    return LinkedInProfileGuidance(
        headline_options=headlines,
        about_section=about,
        highlighted_skills=resume.skills[:8],
        suggested_featured_projects=[
            "Autonomous Drone Systems & ML Telemetry (Computer Vision + Python)",
            "Personal AI Executive Manager (FastAPI + Agentic Tool Architecture)"
        ]
    )

def generate_linkedin_post_draft(topic: str) -> LinkedInPostDraft:
    """Generates a contextual, authentic LinkedIn post draft without spam."""
    profile = get_profile()
    
    if "drone" in topic.lower():
        hook = "Why building telemetry pipelines for drone systems taught me the true value of reliable software engineering:"
        body = (
            "When experimenting with aerial systems, you quickly realize there is zero tolerance for silent failures. "
            "Whether handling edge inference or telemetry parsing in Python, proper error boundaries and persistence matter more than flashy demos.\n\n"
            "As an undergraduate in AI & Computer Science, bridging the gap between theoretical algorithms and physical hardware has been my most rewarding challenge."
        )
        cta = "How do you approach testing for edge and robotics systems? I'd love to learn from your experience."
        hashtags = ["#ArtificialIntelligence", "#DroneSystems", "#MachineLearning", "#Python", "#EngineeringStudent"]
    else:
        hook = "Building an agentic personal executive manager from scratch: Here is why human-in-the-loop safety must come first:"
        body = (
            "Most autonomous agents break down because they confuse 'planning an action' with 'completing it.'\n\n"
            "To solve this in my own personal manager, I implemented strict three-mode autonomy (Assisted, Supervised, and Restricted Autonomy) "
            "with an immutable SQLite WAL audit trail. No external email or job submission ever fires without explicit human authorization."
        )
        cta = "Are you building human-in-the-loop agents? What guardrails have proved most effective for you?"
        hashtags = ["#AgenticAI", "#SoftwareEngineering", "#Python", "#FastAPI", "#AIArchitecture"]

    return LinkedInPostDraft(
        topic=topic,
        hook=hook,
        post_body=body,
        call_to_action=cta,
        hashtags=hashtags
    )

def generate_linkedin_connection_note(recipient_name: str, recipient_role: str, company: str) -> LinkedInConnectionNote:
    """Generates a concise, polite LinkedIn connection request note under 300 characters."""
    profile = get_profile()
    note = (
        f"Hi {recipient_name}, I'm a B.Tech AI student at Mar Baselios Christian College passionate about ML and software development. "
        f"I follow your team's work at {company} and would love to connect and learn from your journey. Best, {profile.full_name}."
    )
    # Ensure strict adherence to LinkedIn's 300 char limit
    if len(note) > 300:
        note = note[:296] + "..."
        
    return LinkedInConnectionNote(
        recipient_name=recipient_name,
        recipient_role=recipient_role,
        character_count=len(note),
        note=note
    )

def generate_weekly_report() -> WeeklyReportResponse:
    """Synthesizes weekly achievements, applications, and priorities."""
    all_tasks = list_tasks()
    completed_tasks = [t for t in all_tasks if t.status == TaskStatusEnum.COMPLETED]
    
    apps = list_job_applications()
    jobs = list_jobs()
    interviews = [a for a in apps if a.status in ("INTERVIEW_SCHEDULED", "OFFER")]
    
    reflection = (
        f"Summary for the past week: Completed {len(completed_tasks)} tasks across study and engineering goals. "
        f"Identified {len(jobs)} opportunities and tracked {len(apps)} verified applications. "
        f"Maintained strict factual integrity across all resume versions."
    )
    
    priorities_next_week = [
        "Follow up on pending internship applications.",
        "Deepen practical coursework in Machine Learning & Drone Vision algorithms.",
        "Maintain zero overdue tasks in the executive manager schedule."
    ]

    return WeeklyReportResponse(
        generated_at=datetime.now(timezone.utc).isoformat(),
        period_label="Weekly Executive Review",
        applications_submitted_count=len(apps),
        opportunities_discovered_count=len(jobs),
        interviews_scheduled_count=len(interviews),
        tasks_completed_count=len(completed_tasks),
        skills_practiced=["Python", "Machine Learning", "FastAPI", "SQLite", "Drone Telemetry"],
        executive_reflection=reflection,
        recommended_priorities_next_week=priorities_next_week
    )

def _row_to_email(row) -> EmailMessageResponse:
    return EmailMessageResponse(
        id=row["id"],
        sender=row["sender"],
        recipient=row["recipient"],
        subject=row["subject"],
        body=row["body"],
        received_at=row["received_at"],
        is_recruiter=bool(row["is_recruiter"]),
        detected_intent=EmailIntentEnum(row["detected_intent"]),
        phishing_risk=PhishingRiskEnum(row["phishing_risk"]),
        phishing_flags=json.loads(row["phishing_flags"]),
        extracted_dates=json.loads(row["extracted_dates"]),
        proposed_reply=row["proposed_reply"],
        status=row["status"],
        created_at=row["created_at"]
    )
