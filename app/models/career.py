"""Data models for Job Discovery, Fraud Detection, Resumes, and Application Tracking."""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class VerificationStatusEnum(str, Enum):
    VERIFIED_BY_EVIDENCE = "VERIFIED_BY_EVIDENCE"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    HIGH_RISK = "HIGH_RISK"

class JobTypeEnum(str, Enum):
    INTERNSHIP = "INTERNSHIP"
    ENTRY_LEVEL = "ENTRY_LEVEL"
    GRADUATE = "GRADUATE"
    FULL_TIME = "FULL_TIME"

class ApplicationStatusEnum(str, Enum):
    DRAFTED = "DRAFTED"
    READY_FOR_APPROVAL = "READY_FOR_APPROVAL"
    SUBMITTED = "SUBMITTED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

class JobVerificationReport(BaseModel):
    employer_identity: str
    official_website: Optional[str] = None
    careers_page_status: str
    recruiter_domain_consistency: str
    application_url_safety: str
    suspicious_indicators: List[str] = []
    evidence_findings: List[str] = []
    confidence_level: str  # HIGH, MEDIUM, LOW
    recommended_action: str

class JobListingCreate(BaseModel):
    title: str
    company: str
    location: Optional[str] = "Remote / India"
    is_remote: bool = False
    job_type: JobTypeEnum = JobTypeEnum.INTERNSHIP
    source_url: str
    source_name: str = "Manual Entry"
    description: str
    salary_info: Optional[str] = None
    application_deadline: Optional[str] = None

class JobListingResponse(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str] = None
    is_remote: bool
    job_type: JobTypeEnum
    source_url: str
    source_name: str
    description: str
    salary_info: Optional[str] = None
    application_deadline: Optional[str] = None
    match_score: int
    suitability_explanation: Optional[str] = None
    missing_qualifications: List[str] = []
    matching_skills: List[str] = []
    verification_status: VerificationStatusEnum
    verification_report: JobVerificationReport
    discovered_at: str
    created_at: str

class MasterResumeResponse(BaseModel):
    id: str
    version_label: str
    full_name: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    summary: str
    education: List[Dict[str, Any]]
    experience: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    skills: List[str]
    certifications: List[Dict[str, Any]]
    ats_score: int
    ats_feedback: List[str]
    raw_text: Optional[str] = None
    is_active: bool
    updated_at: str

class MasterResumeUpdate(BaseModel):
    summary: Optional[str] = None
    education: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    skills: Optional[List[str]] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None

class TailoredResumeResponse(BaseModel):
    id: str
    job_id: str
    version_label: str
    tailored_summary: str
    tailored_skills: List[str]
    tailored_projects: List[Dict[str, Any]]
    cover_letter: str
    application_answers: Dict[str, str]
    keyword_gap_analysis: Dict[str, Any]
    changes_made: List[str]
    created_at: str

class JobApplicationCreate(BaseModel):
    job_id: Optional[str] = None
    company: str
    position: str
    job_url: Optional[str] = None
    resume_version: Optional[str] = "v1.0-master"
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    follow_up_date: Optional[str] = None
    notes: Optional[str] = None

class JobApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatusEnum] = None
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    interview_stages: Optional[List[Dict[str, Any]]] = None
    follow_up_date: Optional[str] = None
    next_action: Optional[str] = None
    notes: Optional[str] = None

class JobApplicationResponse(BaseModel):
    id: str
    job_id: Optional[str] = None
    company: str
    position: str
    job_url: Optional[str] = None
    resume_version: Optional[str] = None
    status: ApplicationStatusEnum
    recruiter_name: Optional[str] = None
    recruiter_email: Optional[str] = None
    interview_stages: List[Dict[str, Any]] = []
    application_date: Optional[str] = None
    follow_up_date: Optional[str] = None
    next_action: Optional[str] = None
    notes: Optional[str] = None
    approval_id: Optional[str] = None
    created_at: str
    updated_at: str
