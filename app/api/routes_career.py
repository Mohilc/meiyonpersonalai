"""API Routes for Job Discovery, Fraud Detection, Resume Tailoring, and Applications."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query

from app.models.career import (
    JobListingCreate, JobListingResponse, MasterResumeResponse,
    MasterResumeUpdate, TailoredResumeResponse, JobApplicationCreate,
    JobApplicationUpdate, JobApplicationResponse
)
from app.services import job_service, resume_service, audit_service

router = APIRouter(prefix="/api/career", tags=["Career & Job Discovery"])

# Jobs
@router.get("/jobs", response_model=List[JobListingResponse])
def list_jobs(
    verification_status: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    is_remote: Optional[bool] = Query(None),
    min_score: Optional[int] = Query(None)
):
    return job_service.list_jobs(
        verification_status=verification_status,
        job_type=job_type,
        is_remote=is_remote,
        min_score=min_score
    )

@router.post("/jobs", response_model=JobListingResponse, status_code=201)
def create_job(payload: JobListingCreate):
    created = job_service.create_or_import_job(payload)
    audit_service.log_audit(
        action_type="JOB_DISCOVERED",
        target_entity="job_listing",
        details={"job_id": created.id, "title": created.title, "verification": created.verification_status.value},
        status="SUCCESS"
    )
    return created

@router.post("/jobs/discover", response_model=List[JobListingResponse])
def discover_live_jobs():
    """Fetches and parses live job opportunities from permitted job APIs."""
    discovered = job_service.discover_live_remote_jobs()
    audit_service.log_audit(
        action_type="JOB_DISCOVERY_FETCH",
        target_entity="job_listings",
        details={"found_count": len(discovered)},
        status="SUCCESS"
    )
    return discovered

@router.get("/jobs/{job_id}", response_model=JobListingResponse)
def get_job(job_id: str):
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job listing not found")
    return job

# Resumes
@router.get("/resume", response_model=MasterResumeResponse)
def get_master_resume():
    return resume_service.get_active_master_resume()

@router.put("/resume", response_model=MasterResumeResponse)
def update_master_resume(payload: MasterResumeUpdate):
    updated = resume_service.update_master_resume(payload)
    audit_service.log_audit(
        action_type="MASTER_RESUME_UPDATED",
        target_entity="master_resume",
        details={"version": updated.version_label},
        status="SUCCESS"
    )
    return updated

@router.post("/jobs/{job_id}/tailor", response_model=TailoredResumeResponse)
def tailor_resume_for_job(job_id: str):
    tailored = resume_service.tailor_resume_for_job(job_id)
    audit_service.log_audit(
        action_type="RESUME_TAILORED",
        target_entity="tailored_resume",
        details={"job_id": job_id, "tailored_id": tailored.id},
        status="SUCCESS"
    )
    return tailored

# Applications
@router.get("/applications", response_model=List[JobApplicationResponse])
def list_applications(status: Optional[str] = Query(None)):
    return resume_service.list_job_applications(status=status)

@router.post("/applications", response_model=JobApplicationResponse, status_code=201)
def create_application(payload: JobApplicationCreate):
    created = resume_service.create_job_application(payload)
    audit_service.log_audit(
        action_type="APPLICATION_DRAFTED",
        target_entity="job_application",
        details={"application_id": created.id, "company": created.company, "role": created.position},
        status="SUCCESS"
    )
    return created

@router.put("/applications/{app_id}", response_model=JobApplicationResponse)
def update_application(app_id: str, payload: JobApplicationUpdate):
    updated = resume_service.update_job_application(app_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Job application not found")
    audit_service.log_audit(
        action_type="APPLICATION_STAGE_UPDATED",
        target_entity="job_application",
        details={"application_id": app_id, "new_status": updated.status.value},
        status="SUCCESS"
    )
    return updated
