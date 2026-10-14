"""Models for Email Triage, Recruiter Communications, LinkedIn Assistance, and Weekly Reports."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EmailIntentEnum(str, Enum):
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTION = "REJECTION"
    INFO_REQUEST = "INFO_REQUEST"
    GENERAL = "GENERAL"

class PhishingRiskEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class EmailMessageCreate(BaseModel):
    sender: str
    recipient: str = "mohil@example.com"
    subject: str
    body: str
    received_at: Optional[str] = None

class EmailMessageResponse(BaseModel):
    id: str
    sender: str
    recipient: str
    subject: str
    body: str
    received_at: str
    is_recruiter: bool
    detected_intent: EmailIntentEnum
    phishing_risk: PhishingRiskEnum
    phishing_flags: List[str] = []
    extracted_dates: List[Dict[str, Any]] = []
    proposed_reply: Optional[str] = None
    status: str
    created_at: str

class EmailReplyRequest(BaseModel):
    custom_notes: Optional[str] = None

class LinkedInProfileGuidance(BaseModel):
    headline_options: List[str]
    about_section: str
    highlighted_skills: List[str]
    suggested_featured_projects: List[str]

class LinkedInPostDraft(BaseModel):
    topic: str
    hook: str
    post_body: str
    call_to_action: str
    hashtags: List[str]

class LinkedInConnectionNote(BaseModel):
    recipient_name: str
    recipient_role: str
    character_count: int
    note: str

class WeeklyReportResponse(BaseModel):
    generated_at: str
    period_label: str
    applications_submitted_count: int
    opportunities_discovered_count: int
    interviews_scheduled_count: int
    tasks_completed_count: int
    skills_practiced: List[str]
    executive_reflection: str
    recommended_priorities_next_week: List[str]
