"""MCP Integration Service for Personal AI Manager.

Orchestrates communication between the Executive Personal AI Manager and the
Model Context Protocol (MCP) servers for Gmail and LinkedIn.

Features:
- Automated Gmail sync with prompt injection sanitization and phishing triage
- Automated LinkedIn messages and connection requests sync
- Enforced Human-In-The-Loop gate execution for approved emails, notes, and posts
- Diagnostic health monitoring for MCP connections
"""
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.database import get_db_connection
from app.config import settings
from app.models.communication import (
    EmailMessageCreate, EmailMessageResponse,
    MCPEmailSyncResponse, MCPLinkedInSyncResponse,
    LinkedInInteractionItem, MCPStatusResponse
)
from app.services import communication_service, audit_service
from app.services.audit_service import get_approval, ApprovalStatusEnum, RiskLevelEnum

# Import MCP server tool interfaces directly
from mcp_servers import gmail_server, linkedin_server

def get_mcp_system_status() -> MCPStatusResponse:
    """Returns the live connection health and mode of Gmail and LinkedIn MCP servers."""
    gmail_status_raw = gmail_server.get_mailbox_status()
    linkedin_status_raw = linkedin_server.get_linkedin_status()
    
    gmail_info = json.loads(gmail_status_raw)
    linkedin_info = json.loads(linkedin_status_raw)
    
    is_ready = bool(gmail_info.get("connected") and linkedin_info.get("connected"))
    
    return MCPStatusResponse(
        gmail=gmail_info,
        linkedin=linkedin_info,
        is_ready=is_ready
    )

def sync_unread_emails_via_mcp(limit: int = 10, query: str = "") -> MCPEmailSyncResponse:
    """
    Pulls unread emails via the Gmail MCP server, runs them through the
    prompt-injection sanitizer and phishing classifier, and stores new messages in SQLite.
    """
    raw_res = gmail_server.list_unread_emails(max_results=limit, query=query)
    data = json.loads(raw_res)
    
    if data.get("status") not in ("SUCCESS", "FALLBACK_SANDBOX"):
        return MCPEmailSyncResponse(
            synced_count=0,
            new_emails=[],
            status=data.get("status", "ERROR"),
            message=data.get("error", "Unknown error while querying Gmail MCP server.")
        )
        
    incoming_emails = data.get("emails", [])
    synced_items: List[EmailMessageResponse] = []
    
    conn = get_db_connection()
    try:
        for item in incoming_emails:
            ext_id = item.get("id")
            
            # Check for duplicates using external_id
            if ext_id:
                cur = conn.execute("SELECT id FROM email_messages WHERE external_id = ?;", (ext_id,))
                if cur.fetchone():
                    continue
                    
            # Ingest through communication_service for security & intent triage
            email_payload = EmailMessageCreate(
                sender=item.get("sender", "unknown@sender.com"),
                recipient=item.get("recipient", "mohil@mbcpe.ac.in"),
                subject=item.get("subject", "(No Subject)"),
                body=item.get("body", ""),
                received_at=item.get("date"),
                external_id=ext_id
            )
            
            triaged = communication_service.triage_incoming_email(email_payload)
            synced_items.append(triaged)
            
            # Record security audit log
            audit_service.log_audit(
                action_type="MCP_EMAIL_SYNCED",
                target_entity="email_message",
                details={
                    "external_id": ext_id,
                    "sender": triaged.sender,
                    "subject": triaged.subject,
                    "intent": triaged.detected_intent.value,
                    "phishing_risk": triaged.phishing_risk.value,
                    "injection_flags": triaged.phishing_flags
                },
                status="SUCCESS"
            )
    finally:
        conn.close()
        
    return MCPEmailSyncResponse(
        synced_count=len(synced_items),
        new_emails=synced_items,
        status="SUCCESS",
        message=f"Successfully synced {len(synced_items)} new emails via Gmail MCP server."
    )

def sync_linkedin_activity_via_mcp(limit: int = 10) -> MCPLinkedInSyncResponse:
    """
    Pulls recent LinkedIn recruiter messages and connection invitations via the
    LinkedIn MCP server and stores them in SQLite.
    """
    messages_raw = linkedin_server.list_recent_messages(limit=limit)
    connections_raw = linkedin_server.list_connection_requests(limit=limit)
    
    messages_data = json.loads(messages_raw)
    connections_data = json.loads(connections_raw)
    
    new_interactions: List[LinkedInInteractionItem] = []
    now_iso = datetime.now(timezone.utc).isoformat()
    
    conn = get_db_connection()
    try:
        with conn:
            # 1. Process Recruiter Messages
            for msg in messages_data.get("messages", []):
                ext_id = msg.get("id")
                cur = conn.execute("SELECT id FROM linkedin_interactions WHERE external_id = ?;", (ext_id,))
                if cur.fetchone():
                    continue
                    
                interaction_id = str(uuid.uuid4())
                conn.execute("""
                INSERT INTO linkedin_interactions (
                    id, interaction_type, sender_name, sender_title, company,
                    content, profile_url, external_id, status, created_at
                ) VALUES (?, 'MESSAGE', ?, ?, ?, ?, ?, ?, 'RECEIVED', ?);
                """, (
                    interaction_id,
                    msg.get("sender_name"),
                    msg.get("sender_title"),
                    msg.get("company"),
                    msg.get("content", ""),
                    msg.get("profile_url"),
                    ext_id,
                    now_iso
                ))
                
                new_interactions.append(LinkedInInteractionItem(
                    id=interaction_id,
                    interaction_type="MESSAGE",
                    sender_name=msg.get("sender_name"),
                    sender_title=msg.get("sender_title"),
                    company=msg.get("company"),
                    content=msg.get("content", ""),
                    profile_url=msg.get("profile_url"),
                    external_id=ext_id,
                    status="RECEIVED",
                    created_at=now_iso
                ))
                
            # 2. Process Connection Invitations
            for conn_item in connections_data.get("connections", []):
                ext_id = conn_item.get("id")
                cur = conn.execute("SELECT id FROM linkedin_interactions WHERE external_id = ?;", (ext_id,))
                if cur.fetchone():
                    continue
                    
                interaction_id = str(uuid.uuid4())
                conn.execute("""
                INSERT INTO linkedin_interactions (
                    id, interaction_type, sender_name, sender_title, company,
                    content, profile_url, external_id, status, created_at
                ) VALUES (?, 'CONNECTION_REQUEST', ?, ?, ?, ?, ?, ?, 'PENDING', ?);
                """, (
                    interaction_id,
                    conn_item.get("sender_name"),
                    conn_item.get("sender_title"),
                    conn_item.get("company"),
                    conn_item.get("invitation_note", ""),
                    conn_item.get("profile_url"),
                    ext_id,
                    now_iso
                ))
                
                new_interactions.append(LinkedInInteractionItem(
                    id=interaction_id,
                    interaction_type="CONNECTION_REQUEST",
                    sender_name=conn_item.get("sender_name"),
                    sender_title=conn_item.get("sender_title"),
                    company=conn_item.get("company"),
                    content=conn_item.get("invitation_note", ""),
                    profile_url=conn_item.get("profile_url"),
                    external_id=ext_id,
                    status="PENDING",
                    created_at=now_iso
                ))

        audit_service.log_audit(
            action_type="MCP_LINKEDIN_SYNCED",
            target_entity="linkedin_interaction",
            details={"synced_items_count": len(new_interactions)},
            status="SUCCESS"
        )
    finally:
        conn.close()
        
    return MCPLinkedInSyncResponse(
        synced_messages_count=len([i for i in new_interactions if i.interaction_type == "MESSAGE"]),
        pending_connections_count=len([i for i in new_interactions if i.interaction_type == "CONNECTION_REQUEST"]),
        interactions=new_interactions,
        status="SUCCESS",
        message=f"Synced {len(new_interactions)} new LinkedIn interactions via MCP."
    )

def list_linkedin_interactions(limit: int = 50) -> List[LinkedInInteractionItem]:
    """Retrieves stored LinkedIn interactions from database."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM linkedin_interactions ORDER BY created_at DESC LIMIT ?;", (limit,))
        rows = cur.fetchall()
        return [
            LinkedInInteractionItem(
                id=r["id"],
                interaction_type=r["interaction_type"],
                sender_name=r["sender_name"],
                sender_title=r["sender_title"],
                company=r["company"],
                content=r["content"],
                profile_url=r["profile_url"],
                external_id=r["external_id"],
                status=r["status"],
                created_at=r["created_at"]
            )
            for r in rows
        ]
    finally:
        conn.close()

def execute_approved_mcp_action(approval_id: str) -> Dict[str, Any]:
    """
    Executes an action via MCP only after verifying explicit human authorization
    in the approvals table.
    """
    approval = get_approval(approval_id)
    if not approval:
        raise ValueError(f"Approval request '{approval_id}' not found.")
        
    if approval.status != ApprovalStatusEnum.APPROVED:
        raise ValueError(f"Action cannot be executed. Approval status is '{approval.status.value}', expected 'APPROVED'.")
        
    payload = json.loads(approval.action_payload)
    action_type = payload.get("action_type") or ("EMAIL_REPLY" if "recipient" in payload else "LINKEDIN_ACTION")
    
    result = {}
    if action_type == "EMAIL_REPLY":
        to = payload.get("recipient")
        subject = payload.get("subject", "Re: Follow up")
        body = payload.get("reply_body", "")
        send_res = gmail_server.send_email(to=to, subject=subject, body=body, approved=True)
        result = json.loads(send_res)
    elif action_type == "LINKEDIN_POST":
        text = payload.get("post_body", "")
        visibility = payload.get("visibility", "PUBLIC")
        post_res = linkedin_server.publish_post(text=text, visibility=visibility, approved=True)
        result = json.loads(post_res)
    elif action_type == "LINKEDIN_INVITE":
        profile_url = payload.get("profile_url", "")
        note = payload.get("note", "")
        invite_res = linkedin_server.send_connection_invite(profile_url=profile_url, custom_note=note, approved=True)
        result = json.loads(invite_res)
    else:
        raise ValueError(f"Unsupported action payload type: '{action_type}'")

    audit_service.log_audit(
        action_type="MCP_ACTION_EXECUTED",
        target_entity="mcp_execution",
        details={"approval_id": approval_id, "result": result},
        status="SUCCESS"
    )
    
    return {
        "status": "EXECUTED",
        "approval_id": approval_id,
        "mcp_result": result
    }

# Backward and cross-module compatibility alias
execute_approved_action = execute_approved_mcp_action
