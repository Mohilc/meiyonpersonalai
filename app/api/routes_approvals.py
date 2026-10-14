"""API Routes for Approvals and Audit Logging."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.approval import ApprovalRequest, ApprovalDecision, AuditLogEntry
from app.services import audit_service

router = APIRouter(prefix="/api/approvals", tags=["Approvals & Security"])

@router.get("", response_model=List[ApprovalRequest])
def list_approvals(status: Optional[str] = Query(None)):
    return audit_service.list_approvals(status=status)

@router.post("/{approval_id}/decide", response_model=ApprovalRequest)
def decide_approval(approval_id: str, decision: ApprovalDecision):
    updated = audit_service.decide_approval(approval_id, decision)
    if not updated:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return updated

@router.get("/audit/logs", response_model=List[AuditLogEntry])
def get_audit_logs(limit: int = Query(50, le=200)):
    return audit_service.list_audit_logs(limit=limit)
