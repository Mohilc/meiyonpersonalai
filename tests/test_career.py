"""Tests for Job Discovery, Fraud Detection, Resume Tailoring, and Application Tracking."""
import pytest
from app.database import init_db
from app.services import job_service, resume_service, audit_service
from app.models.career import (
    JobListingCreate, VerificationStatusEnum, JobTypeEnum,
    JobApplicationCreate, ApplicationStatusEnum, MasterResumeUpdate
)

def test_fraud_detection_and_evidence_reporting():
    init_db()
    
    # 1. Test Advance Fee Fraud Trap -> Must be HIGH_RISK
    scam_job = job_service.create_or_import_job(JobListingCreate(
        title="Remote AI Data Entry",
        company="Global Tech Scam Inc",
        source_url="https://scam-job-portal.xyz/apply",
        source_name="Suspicious Board",
        description="Earn $5000 a week no experience. Mandatory application fee and background check processing fee of $49 via wire transfer or gift card."
    ))
    assert scam_job.verification_status == VerificationStatusEnum.HIGH_RISK
    assert len(scam_job.verification_report.suspicious_indicators) >= 1
    assert "DO NOT APPLY" in scam_job.verification_report.recommended_action
    
    # 2. Test Verified Corporate ATS -> Must be VERIFIED_BY_EVIDENCE
    legit_job = job_service.create_or_import_job(JobListingCreate(
        title="Junior Python & Machine Learning Engineer",
        company="DeepMind Technologies",
        source_url="https://boards.greenhouse.io/deepmind/jobs/987654",
        source_name="Official Career Portal",
        description="Looking for an intern or junior engineer experienced in Python, Machine Learning, and algorithms. Contact: careers@deepmind.com"
    ))
    assert legit_job.verification_status == VerificationStatusEnum.VERIFIED_BY_EVIDENCE
    assert legit_job.match_score >= 70
    assert "Python" in legit_job.matching_skills
    assert "Verified by available evidence" in legit_job.verification_report.recommended_action

def test_master_resume_and_factual_tailoring():
    init_db()
    
    # 1. Get seeded master resume
    master = resume_service.get_active_master_resume()
    assert master.full_name == "Mohil"
    assert "Python" in master.skills
    assert master.ats_score > 80
    
    # 2. Create target job
    job = job_service.create_or_import_job(JobListingCreate(
        title="Drone Vision & ML Intern",
        company="AeroRobotics Lab",
        source_url="https://jobs.lever.co/aerorobotics/drone-intern-101",
        source_name="Company Lever Portal",
        description="Work on aerial drone systems, computer vision, and machine learning telemetry using Python."
    ))
    
    # 3. Tailor resume for this specific job
    tailored = resume_service.tailor_resume_for_job(job.id)
    assert tailored is not None
    assert tailored.job_id == job.id
    # Factual accuracy check: Drone projects prioritized
    assert "Drone" in tailored.tailored_projects[0]["title"]
    assert "AeroRobotics Lab" in tailored.cover_letter
    assert "Why are you interested in this role?" in tailored.application_answers
    assert len(tailored.changes_made) >= 3

def test_application_lifecycle_and_approval_gate():
    init_db()
    
    job = job_service.create_or_import_job(JobListingCreate(
        title="Python Software Intern",
        company="Starlight Systems",
        source_url="https://jobs.ashbyhq.com/starlight/py-intern",
        source_name="Ashby ATS",
        description="Python development, API integration, and database systems."
    ))
    
    # Create application
    app_record = resume_service.create_job_application(JobApplicationCreate(
        job_id=job.id,
        company="Starlight Systems",
        position="Python Software Intern",
        job_url=job.source_url,
        notes="Applied via official Ashby portal"
    ))
    
    assert app_record.id is not None
    assert app_record.status == ApplicationStatusEnum.READY_FOR_APPROVAL
    assert app_record.approval_id is not None
    
    # Verify approval gate exists in approvals table
    approvals = audit_service.list_approvals(status="PENDING")
    matching_appr = [a for a in approvals if a.id == app_record.approval_id]
    assert len(matching_appr) == 1
    assert "Starlight Systems" in matching_appr[0].title
