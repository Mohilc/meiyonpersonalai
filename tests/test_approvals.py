"""Tests for Approval Gate and Security Audit trail."""
from app.database import init_db
from app.services import audit_service
from app.models.approval import RiskLevelEnum, ApprovalDecision, ApprovalStatusEnum

def test_approval_workflow_and_audit_logging():
    init_db()
    
    # 1. Create approval request
    req = audit_service.create_approval_request(
        title="Submit Job Application to Tech Corp",
        description="Applying for ML Intern role using tailored resume v2",
        action_payload={"company": "Tech Corp", "role": "ML Intern", "resume_version": "v2"},
        risk_level=RiskLevelEnum.HIGH
    )
    assert req.id is not None
    assert req.status == ApprovalStatusEnum.PENDING
    assert req.risk_level == RiskLevelEnum.HIGH
    
    # 2. Authorize action
    approved = audit_service.decide_approval(
        req.id,
        ApprovalDecision(decision=ApprovalStatusEnum.APPROVED, reason="Verified by Mohil")
    )
    assert approved.status == ApprovalStatusEnum.APPROVED
    assert approved.decided_at is not None
    assert approved.decision_reason == "Verified by Mohil"
    
    # 3. Verify audit log has recorded the event
    logs = audit_service.list_audit_logs(limit=10)
    assert len(logs) > 0
    actions = [l.action_type for l in logs]
    assert "APPROVAL_APPROVED" in actions
