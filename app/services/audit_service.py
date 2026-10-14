"""Service for Audit Trail, Security logging, and Approval Gates."""
import uuid
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.config import settings
from app.database import get_db_connection
from app.models.approval import (
    ApprovalRequest, ApprovalDecision, ApprovalStatusEnum,
    RiskLevelEnum, AuditLogEntry
)

def log_audit(
    action_type: str,
    target_entity: str,
    details: Optional[Dict[str, Any]] = None,
    status: str = "SUCCESS",
    mode: Optional[str] = None
) -> AuditLogEntry:
    """Records an immutable audit entry."""
    entry_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    op_mode = mode or settings.AUTONOMY_MODE
    details_str = json.dumps(details or {})
    
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO audit_logs (id, action_type, target_entity, details, mode, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (entry_id, action_type, target_entity, details_str, op_mode, status, now_iso))
        return AuditLogEntry(
            id=entry_id,
            action_type=action_type,
            target_entity=target_entity,
            details=details_str,
            mode=op_mode,
            status=status,
            created_at=now_iso
        )
    finally:
        conn.close()

def create_approval_request(
    title: str,
    description: str,
    action_payload: Dict[str, Any],
    risk_level: RiskLevelEnum = RiskLevelEnum.MEDIUM
) -> ApprovalRequest:
    """Registers an action requiring explicit human authorization."""
    appr_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    payload_str = json.dumps(action_payload)
    
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO approvals (id, title, description, action_payload, risk_level, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'PENDING', ?);
            """, (appr_id, title, description, payload_str, risk_level.value, now_iso))
            
            # Also record in audit log
            conn.execute("""
            INSERT INTO audit_logs (id, action_type, target_entity, details, mode, status, created_at)
            VALUES (?, 'APPROVAL_REQUESTED', 'approval', ?, ?, 'PENDING_APPROVAL', ?);
            """, (str(uuid.uuid4()), json.dumps({"title": title, "risk": risk_level.value}), settings.AUTONOMY_MODE, now_iso))
            
        return get_approval(appr_id)
    finally:
        conn.close()

def get_approval(approval_id: str) -> Optional[ApprovalRequest]:
    """Retrieves an approval request."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM approvals WHERE id = ?;", (approval_id,))
        row = cur.fetchone()
        if not row:
            return None
        return ApprovalRequest(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            action_payload=row["action_payload"],
            risk_level=RiskLevelEnum(row["risk_level"]),
            status=ApprovalStatusEnum(row["status"]),
            created_at=row["created_at"],
            decided_at=row["decided_at"],
            decision_reason=row["decision_reason"]
        )
    finally:
        conn.close()

def decide_approval(approval_id: str, decision: ApprovalDecision) -> Optional[ApprovalRequest]:
    """Processes user approval decision (Approve or Reject)."""
    current = get_approval(approval_id)
    if not current:
        return None
        
    now_iso = datetime.now(timezone.utc).isoformat()
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            UPDATE approvals SET
                status = ?,
                decided_at = ?,
                decision_reason = ?
            WHERE id = ?;
            """, (decision.decision.value, now_iso, decision.reason, approval_id))
            
            # Record audit entry in the same transaction
            conn.execute("""
            INSERT INTO audit_logs (id, action_type, target_entity, details, mode, status, created_at)
            VALUES (?, ?, 'approval', ?, ?, 'SUCCESS', ?);
            """, (
                str(uuid.uuid4()),
                f"APPROVAL_{decision.decision.value}",
                json.dumps({"approval_id": approval_id, "reason": decision.reason}),
                settings.AUTONOMY_MODE,
                now_iso
            ))
        return get_approval(approval_id)
    finally:
        conn.close()

def list_approvals(status: Optional[str] = None) -> List[ApprovalRequest]:
    """Lists approval requests."""
    conn = get_db_connection()
    try:
        if status:
            cur = conn.execute("SELECT * FROM approvals WHERE status = ? ORDER BY created_at DESC;", (status,))
        else:
            cur = conn.execute("SELECT * FROM approvals ORDER BY created_at DESC;")
        rows = cur.fetchall()
        return [
            ApprovalRequest(
                id=r["id"],
                title=r["title"],
                description=r["description"],
                action_payload=r["action_payload"],
                risk_level=RiskLevelEnum(r["risk_level"]),
                status=ApprovalStatusEnum(r["status"]),
                created_at=r["created_at"],
                decided_at=r["decided_at"],
                decision_reason=r["decision_reason"]
            ) for r in rows
        ]
    finally:
        conn.close()

def list_audit_logs(limit: int = 50) -> List[AuditLogEntry]:
    """Retrieves recent audit logs."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?;", (limit,))
        rows = cur.fetchall()
        return [
            AuditLogEntry(
                id=r["id"],
                action_type=r["action_type"],
                target_entity=r["target_entity"],
                details=r["details"],
                mode=r["mode"],
                status=r["status"],
                created_at=r["created_at"]
            ) for r in rows
        ]
    finally:
        conn.close()
