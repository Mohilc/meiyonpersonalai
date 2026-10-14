"""API Routes for Email Triage, LinkedIn Assistance, and Weekly Executive Reports."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models.communication import (
    EmailMessageCreate, EmailMessageResponse, EmailReplyRequest,
    LinkedInProfileGuidance, LinkedInPostDraft, LinkedInConnectionNote,
    WeeklyReportResponse
)
from app.services import communication_service, audit_service

router = APIRouter(prefix="/api/communication", tags=["Communications & Reports"])

class PostDraftRequest(BaseModel):
    topic: str = "Drone Systems & Machine Learning"

class ConnectionNoteRequest(BaseModel):
    recipient_name: str
    recipient_role: str
    company: str

# Email Triage
@router.get("/emails", response_model=List[EmailMessageResponse])
def list_emails(limit: int = Query(50)):
    return communication_service.list_email_messages(limit=limit)

@router.post("/emails/triage", response_model=EmailMessageResponse, status_code=201)
def triage_email(payload: EmailMessageCreate):
    triaged = communication_service.triage_incoming_email(payload)
    audit_service.log_audit(
        action_type="EMAIL_TRIAGED",
        target_entity="email_message",
        details={"sender": triaged.sender, "intent": triaged.detected_intent.value, "phishing_risk": triaged.phishing_risk.value},
        status="SUCCESS"
    )
    return triaged

@router.post("/emails/{email_id}/reply")
def request_reply_approval(email_id: str, payload: EmailReplyRequest):
    return communication_service.request_email_reply_approval(email_id, custom_reply=payload.custom_notes)

# LinkedIn Assistant
@router.get("/linkedin/guidance", response_model=LinkedInProfileGuidance)
def get_linkedin_guidance():
    return communication_service.generate_linkedin_guidance()

@router.post("/linkedin/post-draft", response_model=LinkedInPostDraft)
def draft_linkedin_post(payload: PostDraftRequest):
    return communication_service.generate_linkedin_post_draft(payload.topic)

@router.post("/linkedin/connection-note", response_model=LinkedInConnectionNote)
def draft_connection_note(payload: ConnectionNoteRequest):
    return communication_service.generate_linkedin_connection_note(
        recipient_name=payload.recipient_name,
        recipient_role=payload.recipient_role,
        company=payload.company
    )

# Weekly Executive Report
@router.get("/reports/weekly", response_model=WeeklyReportResponse)
def get_weekly_report():
    return communication_service.generate_weekly_report()
