"""Messaging Bot Service for Telegram & WhatsApp Executive AI Access."""
import os
import json
import logging
from typing import Optional, Dict, Any, List
import httpx

from app.config import settings
from app.services import (
    briefing_service,
    audit_service,
    task_service,
    mcp_service,
    llm_service,
    profile_service
)
from app.models.approval import ApprovalDecision, ApprovalStatusEnum, RiskLevelEnum
from app.prompts import (
    build_executive_system_prompt,
    format_permission_request,
    format_action_executed_notification,
    format_action_rejected_notification,
    PLATFORM_TELEGRAM,
    PLATFORM_WHATSAPP
)

logger = logging.getLogger(__name__)

# Track Telegram message offset to avoid duplicate processing
_LAST_TELEGRAM_OFFSET = 0

def handle_incoming_text(sender_id: str, platform: str, text: str) -> str:
    """
    Unified entry point for both Telegram and WhatsApp incoming messages.
    Enforces security authorization, parses commands, or routes to AI reasoning.
    """
    clean_text = text.strip()
    cmd = clean_text.lower()

    # 1. Security Authorization Gate
    if platform == "telegram" and settings.TELEGRAM_ALLOWED_CHAT_ID:
        if str(sender_id) != str(settings.TELEGRAM_ALLOWED_CHAT_ID):
            return "🔒 Unauthorized: This Personal AI Manager is strictly locked to its executive owner."
            
    if platform == "whatsapp" and settings.WHATSAPP_ALLOWED_NUMBER:
        clean_sender = sender_id.replace("whatsapp:", "").strip()
        clean_allowed = settings.WHATSAPP_ALLOWED_NUMBER.replace("whatsapp:", "").strip()
        if clean_sender != clean_allowed:
            return "🔒 Unauthorized: This Personal AI Manager is strictly locked to its executive owner."

    profile = profile_service.get_profile()

    # 2. Executive Commands Routing
    if cmd in ("/start", "help", "/help", "menu"):
        return (
            f"👋 *Welcome, {profile.full_name}!* I am *Meiyon*, your Personal AI Manager.\n\n"
            "Here are your quick executive commands:\n"
            "• `/briefing` - Today's top priorities & strategic AI advice\n"
            "• `/emails` - Check Gmail & unread recruiter triage\n"
            "• `/approvals` - View staged actions awaiting your approval\n"
            "• `/approve <id>` - Authorize staged email reply or post\n"
            "• `/reject <id>` - Decline staged action\n"
            "• `/tasks` - View scheduled task commitments\n\n"
            "💬 *Or just talk naturally!* You can ask me to draft emails, evaluate job offers, or plan your schedule."
        )

    if cmd in ("/briefing", "briefing", "today", "schedule"):
        briefing = briefing_service.generate_daily_briefing()
        p_lines = []
        for i, t in enumerate(briefing.top_three_priorities, 1):
            p_lines.append(f"{i}. *{t.title}* [{t.priority}]")
        priorities_str = "\n".join(p_lines) if p_lines else "No urgent tasks today."

        overdue_str = f"⚠️ *Overdue:* {len(briefing.overdue_commitments)}" if briefing.overdue_commitments else "✅ Zero overdue tasks"
        approvals_str = f"🛡️ *Pending Approvals:* {len(briefing.tasks_awaiting_approval)}" if briefing.tasks_awaiting_approval else "✅ All clear"

        return (
            f"📊 *DAILY EXECUTIVE BRIEFING*\n"
            f"_{briefing.greeting}_\n\n"
            f"🎯 *Top Priorities:*\n{priorities_str}\n\n"
            f"{overdue_str} | {approvals_str}\n\n"
            f"💡 *Executive Summary & AI Insight:*\n{briefing.executive_summary}"
        )

    if cmd in ("/emails", "emails", "sync emails"):
        res = mcp_service.sync_unread_emails_via_mcp(limit=3)
        if not res.new_emails:
            return "📬 *Gmail MCP:* Zero new unread recruiter emails right now. Inbox is clean!"
        lines = [f"📬 *Synced {len(res.new_emails)} Inquiries via Gmail MCP:*"]
        for e in res.new_emails:
            risk_badge = f"[{e.phishing_risk.value}]" if e.phishing_risk.value != "LOW" else "✅ Verified"
            lines.append(f"\n• *From:* {e.sender}\n  *Subject:* {e.subject}\n  *Status:* {risk_badge} ({e.detected_intent.value})")
        lines.append("\nType `/approvals` to review any staged responses.")
        return "\n".join(lines)

    if cmd in ("/approvals", "approvals"):
        pending = audit_service.list_approvals(status="PENDING")
        if not pending:
            return "🛡️ *Security Gate:* No actions currently awaiting approval. Everything is up to date."
        lines = ["🛡️ *Pending Human Approvals:*"]
        for a in pending:
            short_id = a.id[:8]
            lines.append(f"\n• *[{short_id}]* {a.title}\n  _{a.description}_\n  Action: `/approve {short_id}` or `/reject {short_id}`")
        return "\n".join(lines)

    if cmd.startswith("/approve ") or cmd.startswith("approve "):
        prefix = "/approve " if cmd.startswith("/approve ") else "approve "
        short_id = clean_text[len(prefix):].strip()
        pending = audit_service.list_approvals(status="PENDING")
        matched = next((a for a in pending if a.id.startswith(short_id)), None)
        if not matched:
            return f"❌ No pending approval found matching ID '{short_id}'."
        dec = audit_service.decide_approval(
            matched.id,
            ApprovalDecision(decision=ApprovalStatusEnum.APPROVED, reason="Authorized via Mobile Messaging")
        )
        mcp_res = mcp_service.execute_approved_action(matched.id)
        return format_action_executed_notification(
            action_title=matched.title,
            approval_id=matched.id,
            result_summary=f"Status: {mcp_res.get('status', 'EXECUTED')}",
            platform=platform
        )

    if cmd.startswith("/reject ") or cmd.startswith("reject "):
        prefix = "/reject " if cmd.startswith("/reject ") else "reject "
        short_id = clean_text[len(prefix):].strip()
        pending = audit_service.list_approvals(status="PENDING")
        matched = next((a for a in pending if a.id.startswith(short_id)), None)
        if not matched:
            return f"❌ No pending approval found matching ID '{short_id}'."
        audit_service.decide_approval(
            matched.id,
            ApprovalDecision(decision=ApprovalStatusEnum.REJECTED, reason="Rejected via Mobile Messaging")
        )
        return format_action_rejected_notification(
            action_title=matched.title,
            approval_id=matched.id,
            reason="Declined via Mobile Messaging",
            platform=platform
        )

    if cmd in ("/tasks", "tasks"):
        tasks = task_service.list_tasks(status="PENDING")
        if not tasks:
            return "📋 No pending tasks on your board right now."
        lines = ["📋 *Active Commitments:*"]
        for t in tasks[:5]:
            due = f"(Due: {t.due_date[:10]})" if t.due_date else ""
            lines.append(f"• *{t.title}* [{t.priority.value}] {due}")
        return "\n".join(lines)

    # 3. Agentic Intent Detection: Proactive Permission Staging for Outbound Actions
    if cmd.startswith("post on linkedin:") or cmd.startswith("post to linkedin:"):
        prefix = "post on linkedin:" if cmd.startswith("post on linkedin:") else "post to linkedin:"
        post_content = clean_text[len(prefix):].strip()
        if post_content:
            appr = audit_service.create_approval_request(
                title="Publish LinkedIn Post",
                description="Community career/technical update drafted via mobile messaging.",
                action_payload={
                    "action_type": "LINKEDIN_POST",
                    "post_body": post_content,
                    "visibility": "PUBLIC"
                },
                risk_level=RiskLevelEnum.MEDIUM
            )
            return format_permission_request(
                approval_id=appr.id,
                action_type="LINKEDIN_POST",
                title="Publish LinkedIn Post",
                description="Community career/technical update drafted via mobile messaging.",
                payload_preview=post_content,
                risk_level="MEDIUM",
                platform=platform
            )

    # 4. Natural Language Reasoning with NVIDIA Nemotron & Centralized Prompts
    system_prompt = build_executive_system_prompt(
        platform=platform,
        user_profile=profile,
        autonomy_mode=settings.AUTONOMY_MODE
    )
    ai_response = llm_service.generate_completion(
        prompt=clean_text,
        system_prompt=system_prompt,
        task_type="reasoning",
        max_tokens=512
    )
    return ai_response or "I received your request. You can check `/briefing`, `/emails`, or `/tasks` anytime."


def send_telegram_message(chat_id: str, text: str) -> bool:
    """Dispatches a message to a user on Telegram."""
    if not settings.TELEGRAM_BOT_TOKEN:
        return False
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, json=payload)
            return resp.status_code == 200
    except Exception as e:
        logger.error("Failed sending Telegram message: %s", str(e))
        return False


def send_whatsapp_message(
    to_number: str,
    text: Optional[str] = None,
    content_sid: Optional[str] = None,
    content_variables: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Dispatches a WhatsApp message using Twilio API.
    Supports standard Body text or pre-approved Content Template SID.
    """
    sid = settings.TWILIO_ACCOUNT_SID or os.environ.get("TWILIO_ACCOUNT_SID", "")
    token = settings.TWILIO_AUTH_TOKEN or os.environ.get("TWILIO_AUTH_TOKEN", "")
    if not (sid and token):
        logger.warning("Twilio credentials not configured in settings.")
        return False

    clean_to = to_number if to_number.startswith("whatsapp:") else f"whatsapp:{to_number}"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    auth = (sid, token)
    data: Dict[str, Any] = {
        "From": settings.TWILIO_WHATSAPP_NUMBER,
        "To": clean_to,
    }
    
    target_sid = content_sid or (settings.TWILIO_CONTENT_SID if not text else None)
    if target_sid:
        data["ContentSid"] = target_sid
        if content_variables:
            data["ContentVariables"] = json.dumps(content_variables)
    elif text:
        data["Body"] = text
    else:
        logger.error("Neither text nor content_sid provided for WhatsApp message.")
        return False

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, auth=auth, data=data)
            if resp.status_code in (200, 201):
                msg_info = resp.json()
                logger.info("Twilio WhatsApp sent successfully! SID: %s", msg_info.get("sid"))
                return True
            else:
                logger.error("Twilio WhatsApp API Error (%d): %s", resp.status_code, resp.text)
                return False
    except Exception as e:
        logger.error("Failed sending WhatsApp message: %s", str(e))
        return False


def dispatch_whatsapp_with_sid(
    to_number: str = "whatsapp:+918590144798",
    content_sid: Optional[str] = None,
    content_variables: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Sends an outbound WhatsApp message using a Twilio Content Template SID.
    Returns the exact message SID and response details.
    """
    sid = settings.TWILIO_ACCOUNT_SID or os.environ.get("TWILIO_ACCOUNT_SID", "")
    token = settings.TWILIO_AUTH_TOKEN or os.environ.get("TWILIO_AUTH_TOKEN", "")
    if not (sid and token):
        return {
            "success": False,
            "error": "TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN not configured. Please set them in your .env file."
        }

    clean_to = to_number if to_number.startswith("whatsapp:") else f"whatsapp:{to_number}"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
    auth = (sid, token)
    data: Dict[str, Any] = {
        "From": settings.TWILIO_WHATSAPP_NUMBER,
        "To": clean_to,
        "ContentSid": content_sid or settings.TWILIO_CONTENT_SID
    }
    if content_variables:
        data["ContentVariables"] = json.dumps(content_variables)

    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, auth=auth, data=data)
            if resp.status_code in (200, 201):
                res_json = resp.json()
                logger.info("WhatsApp template delivered! SID: %s", res_json.get("sid"))
                return {
                    "success": True,
                    "sid": res_json.get("sid"),
                    "status": res_json.get("status"),
                    "to": clean_to,
                    "from": settings.TWILIO_WHATSAPP_NUMBER,
                    "content_sid": data["ContentSid"]
                }
            else:
                logger.error("Twilio WhatsApp error (%d): %s", resp.status_code, resp.text)
                return {
                    "success": False,
                    "status_code": resp.status_code,
                    "error": resp.text
                }
    except Exception as e:
        logger.error("Twilio WhatsApp exception: %s", str(e))
        return {"success": False, "error": str(e)}


def poll_telegram_updates_once():
    """
    Pulls recent Telegram updates via long polling so no public URL or ngrok is required.
    Runs periodically inside the background scheduler.
    """
    global _LAST_TELEGRAM_OFFSET
    if not (settings.TELEGRAM_ENABLED and settings.TELEGRAM_BOT_TOKEN):
        return

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"offset": _LAST_TELEGRAM_OFFSET, "timeout": 2}
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code != 200:
                return
            data = resp.json()
            updates = data.get("result", [])
            for update in updates:
                update_id = update.get("update_id", 0)
                _LAST_TELEGRAM_OFFSET = max(_LAST_TELEGRAM_OFFSET, update_id + 1)
                
                message = update.get("message", {})
                chat = message.get("chat", {})
                chat_id = str(chat.get("id", ""))
                text = message.get("text", "")
                
                if chat_id and text:
                    reply_text = handle_incoming_text(sender_id=chat_id, platform="telegram", text=text)
                    send_telegram_message(chat_id=chat_id, text=reply_text)
    except Exception as e:
        logger.debug("Telegram polling tick: %s", str(e))
