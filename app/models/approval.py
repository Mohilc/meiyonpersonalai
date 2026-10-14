"""Models for Approval Gates and Audit Logging."""
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

class RiskLevelEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ApprovalStatusEnum(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class ApprovalRequest(BaseModel):
    id: str
    title: str
    description: str
    action_payload: str
    risk_level: RiskLevelEnum
    status: ApprovalStatusEnum
    created_at: str
    decided_at: Optional[str] = None
    decision_reason: Optional[str] = None

class ApprovalDecision(BaseModel):
    decision: ApprovalStatusEnum  # APPROVED or REJECTED
    reason: Optional[str] = None

class AuditLogEntry(BaseModel):
    id: str
    action_type: str
    target_entity: str
    details: Optional[str] = None
    mode: str
    status: str
    created_at: str
