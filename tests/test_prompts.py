"""Tests for Executive Chatbot Prompts, Cognitive Instructions, and HITL Permission Gates."""
import pytest
from app.prompts import (
    build_executive_system_prompt,
    format_permission_request,
    format_action_executed_notification,
    format_action_rejected_notification,
    format_clarification_query,
    build_recruiter_triage_prompt,
    build_daily_briefing_prompt,
    build_linkedin_ghostwrite_prompt,
    build_ambiguity_resolution_prompt,
    PLATFORM_TELEGRAM,
    PLATFORM_WHATSAPP,
    MESSAGING_INSTRUCTIONS,
    CLARIFICATION_QUERY_INSTRUCTIONS,
    RESPONSE_INSTRUCTIONS,
    HITL_PERMISSION_INSTRUCTIONS
)
from app.database import init_db
from app.services import messaging_bot_service, audit_service
from app.models.approval import RiskLevelEnum, ApprovalStatusEnum

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_telegram_system_prompt_structure():
    """Verifies that the Telegram system prompt contains all cognitive instructions, persona, and HITL gates."""
    prompt = build_executive_system_prompt(platform=PLATFORM_TELEGRAM)
    
    # 1. Identity & Principal
    assert "Meiyon" in prompt
    assert "Mohil" in prompt
    assert "Mar Baselios Christian College" in prompt
    
    # 2. Cognitive instruction sets
    assert "MESSAGING INSTRUCTIONS" in prompt
    assert "CLARIFICATION & QUERY INSTRUCTIONS" in prompt
    assert "RESPONSE INSTRUCTIONS" in prompt
    assert "HUMAN-IN-THE-LOOP (HITL) PERMISSION PROTOCOL" in prompt
    
    # 3. Telegram specific commands
    assert "/briefing" in prompt
    assert "/approvals" in prompt
    assert "/approve" in prompt
    assert "/reject" in prompt

def test_whatsapp_system_prompt_structure():
    """Verifies that the WhatsApp system prompt includes WhatsApp markup rules and numbered commands."""
    prompt = build_executive_system_prompt(platform=PLATFORM_WHATSAPP)
    
    assert "Meiyon" in prompt
    assert "Mohil" in prompt
    assert "WHATSAPP FORMATTING RULES" in prompt
    assert "HUMAN-IN-THE-LOOP" in prompt
    assert "*bold*" in prompt
    assert "_italic_" in prompt

def test_format_permission_request_telegram():
    """Verifies the Telegram permission request format."""
    msg = format_permission_request(
        approval_id="test-approval-123456",
        action_type="EMAIL_REPLY",
        title="Reply to Google Recruiter",
        description="Interview availability confirmation for Thursday 2 PM.",
        payload_preview="Hi Sarah,\nThank you for reaching out. Thursday at 2 PM IST works perfectly.\nBest,\nMohil",
        risk_level="HIGH",
        platform=PLATFORM_TELEGRAM
    )
    
    assert "SECURITY GATE: AUTHORIZATION REQUIRED" in msg
    assert "EMAIL_REPLY" in msg
    assert "HIGH RISK" in msg
    assert "test-app" in msg  # short id
    assert "/approve test-app" in msg
    assert "/reject test-app" in msg
    assert "Hi Sarah" in msg

def test_format_permission_request_whatsapp():
    """Verifies the WhatsApp permission request format."""
    msg = format_permission_request(
        approval_id="test-whatsapp-789012",
        action_type="LINKEDIN_POST",
        title="Publish Agentic AI Milestone",
        description="Post discussing multi-model AI manager deployment.",
        payload_preview="Excited to share my latest architecture on autonomous career agents!",
        risk_level="MEDIUM",
        platform=PLATFORM_WHATSAPP
    )
    
    assert "SECURITY GATE: AUTHORIZATION REQUIRED" in msg
    assert "*LINKEDIN_POST*" in msg
    assert "MEDIUM RISK" in msg
    assert "approve test-wha" in msg
    assert "reject test-wha" in msg

def test_format_clarification_query():
    """Verifies formatted query asking Mohil for options."""
    query = format_clarification_query(
        context_title="Interview Time Slot Conflict",
        question="The recruiter offered two times. Which fits your schedule?",
        options=[
            "Thursday 2:00 PM IST (Recommended, free slot)",
            "Friday 11:00 AM IST (Overlaps with project review)"
        ],
        recommended_option_index=1,
        platform=PLATFORM_TELEGRAM
    )
    
    assert "EXECUTIVE CLARIFICATION NEEDED" in query
    assert "Context" in query
    assert "Thursday 2:00 PM IST" in query
    assert "(Recommended)" in query
    assert "Reply with your preferred number" in query

def test_action_notifications():
    """Verifies executed and rejected action notifications."""
    exec_msg = format_action_executed_notification(
        action_title="Send Interview Reply",
        approval_id="appr-9999-uuid",
        result_summary="Status: EXECUTED via Gmail MCP",
        platform=PLATFORM_TELEGRAM
    )
    assert "ACTION EXECUTED SUCCESSFULLY" in exec_msg
    assert "appr-999" in exec_msg
    assert "Gmail MCP" in exec_msg

    reject_msg = format_action_rejected_notification(
        action_title="Publish LinkedIn Update",
        approval_id="appr-8888-uuid",
        reason="Post requires revisions on technical citations",
        platform=PLATFORM_TELEGRAM
    )
    assert "ACTION CANCELLED BY USER" in reject_msg
    assert "safely discarded" in reject_msg
    assert "technical citations" in reject_msg

def test_llm_prompt_builders():
    """Verifies prompt builder helpers for LLM reasoning."""
    triage = build_recruiter_triage_prompt(
        sender="recruiter@microsoft.com",
        subject="SWE Internship 2027",
        body="We reviewed your GitHub and would like to schedule a call.",
        detected_intent="INTERVIEW",
        phishing_risk="LOW"
    )
    assert "recruiter@microsoft.com" in triage
    assert "SWE Internship 2027" in triage
    assert "Approvals Gate" in triage

    briefing = build_daily_briefing_prompt(
        candidate_name="Mohil",
        priorities_summary="1. Submit CV to Amazon\n2. Prepare for Mock Interview",
        overdue_count=0,
        unread_emails_count=2,
        pending_approvals_count=1
    )
    assert "Mohil" in briefing
    assert "Unread Recruiter Emails: 2" in briefing

    ghostwrite = build_linkedin_ghostwrite_prompt(
        topic="Model Context Protocol in Agentic Systems",
        key_takeaways="Standardized stdio bridging between LLM reasoning and real tools."
    )
    assert "Model Context Protocol" in ghostwrite
    assert "approvals queue" in ghostwrite

    ambiguity = build_ambiguity_resolution_prompt(
        user_instruction="Apply to Google",
        missing_aspects=["Target role (SWE vs ML)", "Preferred location", "Resume version"]
    )
    assert "Apply to Google" in ambiguity
    assert "Target role" in ambiguity

def test_end_to_end_messaging_bot_permission_staging():
    """Verifies that an outbound command triggers permission request and approval flow."""
    # 1. User says "post on linkedin: ..."
    res = messaging_bot_service.handle_incoming_text(
        sender_id="any",
        platform="telegram",
        text="post on linkedin: Deploying Meiyon executive AI agent architecture!"
    )
    
    assert "SECURITY GATE: AUTHORIZATION REQUIRED" in res
    assert "Publish LinkedIn Post" in res
    assert "/approve " in res
    assert "/reject " in res
    
    # Extract approval ID
    lines = res.splitlines()
    id_line = next(line for line in lines if "Approval ID" in line)
    short_id = id_line.split("`")[1]
    
    # 2. User approves the action
    res_approve = messaging_bot_service.handle_incoming_text(
        sender_id="any",
        platform="telegram",
        text=f"/approve {short_id}"
    )
    
    assert "ACTION EXECUTED SUCCESSFULLY" in res_approve
    assert "Publish LinkedIn Post" in res_approve

def test_end_to_end_messaging_bot_rejection():
    """Verifies that rejecting an action safely cancels it."""
    # Stage an approval
    appr = audit_service.create_approval_request(
        title="Draft Test Email",
        description="Test description",
        action_payload={"action_type": "EMAIL_REPLY", "recipient": "test@example.com"},
        risk_level=RiskLevelEnum.LOW
    )
    short_id = appr.id[:8]
    
    res_reject = messaging_bot_service.handle_incoming_text(
        sender_id="any",
        platform="telegram",
        text=f"/reject {short_id}"
    )
    
    assert "ACTION CANCELLED BY USER" in res_reject
    
    # Verify status in database
    updated = audit_service.get_approval(appr.id)
    assert updated.status == ApprovalStatusEnum.REJECTED

def test_two_way_conversational_dialogue_and_memory():
    """Verifies that the chatbot maintains two-way conversational history and responds contextually."""
    sender_id = "test_conversation_user_99"
    messaging_bot_service.clear_conversation_history(sender_id)
    assert len(messaging_bot_service.get_conversation_history(sender_id)) == 0

    # Turn 1: Casual conversation
    reply1 = messaging_bot_service.handle_incoming_text(
        sender_id=sender_id,
        platform="telegram",
        text="Hey Meiyon, I am working on my autonomous drone vision project today."
    )
    assert len(reply1) > 0
    history1 = messaging_bot_service.get_conversation_history(sender_id)
    assert len(history1) == 2  # 1 user + 1 assistant
    assert history1[0]["role"] == "user"
    assert "autonomous drone vision" in history1[0]["content"]

    # Turn 2: Follow-up question using previous turn context
    reply2 = messaging_bot_service.handle_incoming_text(
        sender_id=sender_id,
        platform="telegram",
        text="What are some good ways to benchmark latency on a Raspberry Pi?"
    )
    assert len(reply2) > 0
    history2 = messaging_bot_service.get_conversation_history(sender_id)
    assert len(history2) == 4  # 2 user + 2 assistant

    # Clear memory test
    res_clear = messaging_bot_service.handle_incoming_text(
        sender_id=sender_id,
        platform="telegram",
        text="/clear"
    )
    assert "Memory Cleared" in res_clear
    assert len(messaging_bot_service.get_conversation_history(sender_id)) == 0
