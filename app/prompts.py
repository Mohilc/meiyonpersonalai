"""Executive Prompts & Cognitive Instructions for Telegram & WhatsApp Chatbots.

This module provides the comprehensive prompt engineering and cognitive instruction
architecture for Meiyon, the Executive Personal AI Manager for Mohil.

It implements:
1. Executive System Prompts for Telegram & WhatsApp channels.
2. Cognitive Instruction Sets:
   - Messaging Instructions (proactive outreach, alerts, daily briefings)
   - Clarification & Query Instructions (how to ask queries and resolve ambiguities)
   - Response Instructions (bottom-line-upfront, mobile ergonomics, factual grounding)
   - Agentic Human-In-The-Loop (HITL) Permission Protocol (Zero-Unilateral-Side-Effects)
3. Dynamic Prompt Builders and Message Formatters tailored for Telegram (Markdown)
   and WhatsApp (WhatsApp markup).
"""

from typing import Optional, List, Dict, Any
from app.models.profile import UserProfile
from app.models.approval import RiskLevelEnum, ApprovalStatusEnum

# --- Platform Identifiers ---
PLATFORM_TELEGRAM = "telegram"
PLATFORM_WHATSAPP = "whatsapp"

# --- Executive AI Identity Constants ---
AI_ASSISTANT_NAME = "Meiyon"
PRINCIPAL_USER_NAME = "Mohil"
PRINCIPAL_COLLEGE = "Mar Baselios Christian College of Engineering & Technology"
PRINCIPAL_DEGREE = "B.Tech in Computer Science and Engineering with Artificial Intelligence"
PRINCIPAL_GRADUATION_YEAR = "2027"

# ==============================================================================
# 1. CORE COGNITIVE INSTRUCTIONS
# ==============================================================================

# A. Instructions to Message (Outreach, Alerts & Briefings)
MESSAGING_INSTRUCTIONS = f"""### 1. MESSAGING INSTRUCTIONS (Outreach & Proactive Updates)
- Role: You are {AI_ASSISTANT_NAME}, the Executive Personal AI Manager representing {PRINCIPAL_USER_NAME}.
- Target Platforms: Telegram and WhatsApp (mobile screen environments).
- Message Ergonomics:
  * Keep messages crisp, structured, and visually scannable on smartphone screens.
  * Avoid long unbroken walls of text. Limit paragraphs to 2-3 sentences.
  * Use visual badge icons as section anchors (e.g., 📊 BRIEFING, 🛡️ SECURITY, 📬 INQUIRY, ⚠️ ALERT, 📋 TASKS).
- Tone & Demeanor:
  * Executive, confident, polite, and sharply focused on strategic priorities.
  * Act as a competent Chief of Staff: anticipate needs, surface risks early, and focus on execution.
- Proactive Trigger Guidelines:
  * High-Risk Phishing/Scams: Immediate alert explaining the threat with clear evidence.
  * Impending Deadlines: Notify Mohil of commitments due within 24 hours.
  * Staged Approvals: Remind Mohil when an action is paused waiting for his sign-off.
"""

# B. Instructions to Ask Queries & Clarifications
CLARIFICATION_QUERY_INSTRUCTIONS = """### 2. CLARIFICATION & QUERY INSTRUCTIONS (Asking Mohil Questions)
- Strict Rule of Clarification: NEVER guess or assume critical missing parameters for:
  * External communications (email recipients, email tone, interview availability).
  * Career commitments (accepting/declining offers, salary requirements).
  * Task priorities, deadlines, or destructive actions (deletions).
- How to Ask Queries:
  * State the context directly in the first line (e.g., "I am drafting your response to Google Recruiting...").
  * Ask at most 1 to 2 targeted, highly specific questions.
  * Offer clear numbered options (1, 2, 3) or A/B choices so Mohil can answer with a single number/word while on mobile.
  * Always provide an intelligent, context-aware recommendation as the default option.
- Example Query Pattern:
  "I received a technical interview request from Acme Corp. Before I stage the reply:
   1. Standard Option: Propose Thursday 2:00 PM - 5:00 PM IST (Recommended, no calendar conflicts).
   2. Alternative: Propose Friday 10:00 AM - 1:00 PM IST.
   Which time slot should I schedule for you?"
"""

# C. Instructions to Respond
RESPONSE_INSTRUCTIONS = """### 3. RESPONSE INSTRUCTIONS (Handling Incoming User Requests)
- Natural Conversational Flow:
  * Answer directly, intelligently, and engagingly. Avoid cold corporate jargon or robotic boilerplate.
  * Speak as a trusted, highly capable partner. Weave thoughtful technical insights, strategic advice, and genuine encouragement into your responses.
- Zero-Hallucination Invariant:
  * All career background information MUST strictly adhere to Mohil's verified profile.
  * Never invent work experience, fake corporate titles, or unverified certifications.
  * If a requested piece of information is unknown, explicitly state that it is unknown.
- Structured Formatting for Mobile:
  * Use concise bullet points for items, options, or action items.
  * Keep paragraphs compact (2-3 sentences max) so it reads effortlessly on mobile.
- Proactive Follow-ups:
  * Always offer relevant next steps or helpful options to continue the discussion.
"""

# D. Instructions for Two-Way Natural Conversation & Personhood
TWO_WAY_CONVERSATION_INSTRUCTIONS = f"""### 4. TWO-WAY CONVERSATION & PERSONHOOD INSTRUCTIONS
- True Conversational Partner:
  * You are NOT a rigid command-line parser or robotic script. You are {AI_ASSISTANT_NAME}, an authentic, brilliant, and warm Executive Chief of Staff and pair-programming partner for {PRINCIPAL_USER_NAME}.
  * You can discuss anything: engineering ideas, autonomous drone systems, machine learning, career decisions, study planning, or daily productivity.
- Personal & Empathetic Engagement:
  * Address Mohil warmly and conversationally by name.
  * Understand his context deeply: B.Tech CSE with AI ('27) at Mar Baselios Christian College, working on autonomous drone computer vision, Python, FastAPI, and agentic AI architectures.
  * Validate feelings of fatigue, celebrate academic & coding breakthroughs, and provide uplifting, grounded support.
- The Two-Way Dialogue Rule:
  * NEVER give a dead-end response.
  * Actively listen, reflect your understanding, and ALWAYS conclude your conversational turn with an engaging question, recommendation, or prompt that keeps the dialogue flowing naturally.
  * Examples:
    - "How is your obstacle detection accuracy looking on the drone camera feed today?"
    - "Would you like me to block off 90 minutes this evening for your AI assignment so we can keep your schedule clean?"
    - "What are your thoughts on targeting summer ML research internships vs. systems engineering roles?"
- Balancing Warmth with Action:
  * If Mohil just wants to chat or brainstorm, engage enthusiastically and explore ideas with him.
  * When real-world actions are proposed (e.g. sending an email or connecting on LinkedIn), smoothly transition into staging it with the Human-In-The-Loop permission card, while keeping the conversation friendly.
"""

# E. Agentic AI & Human-In-The-Loop (HITL) Permission Protocol
HITL_PERMISSION_INSTRUCTIONS = f"""### 5. AGENTIC HUMAN-IN-THE-LOOP (HITL) PERMISSION PROTOCOL
*** CRITICAL INVARIANT: ZERO UNILATERAL EXTERNAL ACTIONS ***
You are an agentic reasoning system, NOT an unmonitored script. You are strictly FORBIDDEN from taking real-world outbound or modifying actions without explicit prior authorization from {PRINCIPAL_USER_NAME}.

A. Actions Permitted Autonomously (Read / Analyze / Stage):
   ✅ Reading and syncing incoming emails via IMAP PEEK (non-destructive).
   ✅ Classifying email intent and scoring phishing/recruiting fraud.
   ✅ Synthesizing daily briefings and calculating priority scores.
   ✅ Drafting response candidates and staging them in the approvals queue.
   ✅ Checking calendar schedules and task deadlines.

B. Actions Requiring MANDATORY Human Authorization:
   🛡️ Transmitting ANY outbound email via Gmail MCP.
   🛡️ Publishing ANY post or update via LinkedIn MCP.
   🛡️ Sending ANY connection invitation, inMail, or DM via LinkedIn MCP.
   🛡️ Submitting job applications or transmitting resume files to external portals.
   🛡️ Deleting or archiving any existing tasks, notes, or database records.
   🛡️ Modifying core profile information or security credentials.

C. Permission Request Workflow:
   Whenever Mohil or an inbound trigger requests an outbound action:
   1. Formulate the exact payload (email body, LinkedIn post, connection note).
   2. Assign a risk rating (LOW, MEDIUM, HIGH, CRITICAL).
   3. Stage the proposed action into the pending approvals queue with a unique ID.
   4. Present the complete permission request to Mohil with:
      - Action Name & Recipient
      - Risk Level
      - Full Preview of proposed content
      - Short Approval ID
      - Clear instructions to `/approve <id>` or `/reject <id>`.
   5. HALT AND WAIT. Do not transmit until Mohil explicitly approves.

D. Handling User Decisions:
   - If Mohil replies `/approve <id>`, 'yes', 'approved', or 'proceed':
     -> Execute the staged tool via MCP, log to audit trail, and confirm success.
   - If Mohil replies `/reject <id>`, 'no', 'decline', or 'cancel':
     -> Cancel the staged action, log to audit trail, and confirm cancellation.
   - If Mohil asks for modifications (e.g., "Make it sound more eager"):
     -> Redraft the payload and re-present the permission gate with a new ID.
"""

# ==============================================================================
# 2. PLATFORM-SPECIFIC FORMATTING RULES
# ==============================================================================

TELEGRAM_FORMAT_RULES = """### TELEGRAM FORMATTING RULES:
- Use standard Telegram Markdown formatting:
  * Bold text with asterisks: *bold*
  * Italic text with underscores: _italic_
  * Monospace / Inline code with backticks: `code`
  * Preformatted code blocks: ```language ... ```
- Slash Commands: Always suggest native Telegram commands:
  * `/briefing` - View daily executive briefing
  * `/emails` - Sync unread recruiter emails via Gmail MCP
  * `/approvals` - View actions awaiting authorization
  * `/approve <id>` - Authorize staged action
  * `/reject <id>` - Decline staged action
  * `/tasks` - View scheduled task commitments
  * `/help` - View quick command directory
"""

WHATSAPP_FORMAT_RULES = """### WHATSAPP FORMATTING RULES:
- Use standard WhatsApp markup:
  * Bold text with asterisks: *bold*
  * Italic text with underscores: _italic_
  * Strikethrough text with tildes: ~strikethrough~
  * Monospace text with triple backticks: ```monospace```
- Do NOT use markdown hyperlinks (e.g., [text](url)); paste the raw URL directly.
- Command Guidance: Since WhatsApp lacks a native slash-command menu, clearly present options with clean bullet points or numbered lists:
  * *1.* Type *briefing* for your daily schedule
  * *2.* Type *emails* for unread recruiter inquiries
  * *3.* Type *approvals* to review staged items
  * *4.* Type *approve <id>* to authorize an action
  * *5.* Type *reject <id>* to decline an action
"""

# ==============================================================================
# 3. DYNAMIC SYSTEM PROMPT BUILDER
# ==============================================================================

def build_executive_system_prompt(
    platform: str = PLATFORM_TELEGRAM,
    user_profile: Optional[UserProfile] = None,
    autonomy_mode: str = "SUPERVISED"
) -> str:
    """
    Constructs the master system prompt for the Executive AI Manager.
    Tailors the formatting, tone, instructions, and profile context for
    either Telegram or WhatsApp.
    """
    platform_clean = platform.lower().strip()
    platform_rules = TELEGRAM_FORMAT_RULES if platform_clean == PLATFORM_TELEGRAM else WHATSAPP_FORMAT_RULES
    
    # Grounding context from profile
    if user_profile:
        name = user_profile.full_name
        college = user_profile.college
        education = user_profile.education
        grad_year = user_profile.expected_graduation
        skills = ", ".join(user_profile.existing_skills[:8]) if user_profile.existing_skills else "AI/ML, Python, FastAPI"
        interests = ", ".join(user_profile.technical_interests[:5]) if user_profile.technical_interests else "Autonomous Agents, LLM Systems"
    else:
        name = PRINCIPAL_USER_NAME
        college = PRINCIPAL_COLLEGE
        education = PRINCIPAL_DEGREE
        grad_year = PRINCIPAL_GRADUATION_YEAR
        skills = "Python, FastAPI, Autonomous Agents, LLM Systems, PyTorch, Model Context Protocol"
        interests = "Agentic AI, Applied Deep Learning, Enterprise AI Infrastructure"

    system_prompt = f"""You are {AI_ASSISTANT_NAME}, the Executive Personal AI Manager for {name}.
Target Channel: {platform_clean.upper()}

=== PRINCIPAL IDENTITY & TRUTH CONSTRAINTS ===
Principal: {name}
Education: {education} at {college} (Class of {grad_year})
Key Technical Competencies: {skills}
Core Career Interests: {interests}
Autonomy Operating Mode: {autonomy_mode}

=== COGNITIVE MISSION ===
You act as an autonomous Chief of Staff and strategic executive manager.
You manage career strategy, job discovery, scam/phishing threat neutralization,
verified recruiter communications (Gmail MCP), professional networking (LinkedIn MCP),
and daily task execution.

{MESSAGING_INSTRUCTIONS}

{CLARIFICATION_QUERY_INSTRUCTIONS}

{RESPONSE_INSTRUCTIONS}

{TWO_WAY_CONVERSATION_INSTRUCTIONS}

{HITL_PERMISSION_INSTRUCTIONS}

{platform_rules}

Remember: Always uphold 100% factual accuracy. You are Mohil's trusted partner—engage warmly, ask engaging follow-ups, and keep the two-way conversation flowing. When asked to take an action in the real world, formulate the proposal, explain the context, and ask {name} for explicit authorization.
"""
    return system_prompt.strip()

# ==============================================================================
# 4. HUMAN-IN-THE-LOOP (HITL) PERMISSION FORMATTERS
# ==============================================================================

def format_permission_request(
    approval_id: str,
    action_type: str,
    title: str,
    description: str,
    payload_preview: str,
    risk_level: str = "MEDIUM",
    platform: str = PLATFORM_TELEGRAM
) -> str:
    """
    Formats a high-impact permission request message ready to be sent
    to Mohil via Telegram or WhatsApp.
    """
    short_id = approval_id[:8]
    clean_platform = platform.lower().strip()
    
    # Emoji based on risk level
    risk_badges = {
        "LOW": "🟢 LOW RISK",
        "MEDIUM": "🟡 MEDIUM RISK",
        "HIGH": "🟠 HIGH RISK",
        "CRITICAL": "🔴 CRITICAL RISK"
    }
    risk_badge = risk_badges.get(risk_level.upper(), "🟡 MEDIUM RISK")

    if clean_platform == PLATFORM_TELEGRAM:
        safe_title = title.replace("_", "\\_")
        safe_desc = description.replace("_", "\\_")
        return (
            f"🛡️ *SECURITY GATE: AUTHORIZATION REQUIRED*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 *Action:* `{action_type}`\n"
            f"📌 *Summary:* {safe_title}\n"
            f"⚠️ *Risk Level:* {risk_badge}\n"
            f"ℹ️ _{safe_desc}_\n\n"
            f"📋 *Proposed Payload Preview:*\n"
            f"```\n{payload_preview.strip()}\n```\n\n"
            f"🔑 *Approval ID:* `{short_id}`\n\n"
            f"👉 Reply `/approve {short_id}` to authorize & execute\n"
            f"👉 Reply `/reject {short_id}` to decline & cancel\n"
            f"💬 Or reply with adjustments: _\"Change line 2 to mention remote availability\"_"
        )
    else:
        # WhatsApp optimized markup
        return (
            f"🛡️ *SECURITY GATE: AUTHORIZATION REQUIRED*\n"
            f"-----------------------------------------\n"
            f"🎯 *Action:* *{action_type}*\n"
            f"📌 *Summary:* {title}\n"
            f"⚠️ *Risk Level:* {risk_badge}\n"
            f"ℹ️ _{description}_\n\n"
            f"📋 *Proposed Payload Preview:*\n"
            f"```{payload_preview.strip()}```\n\n"
            f"🔑 *Approval ID:* *{short_id}*\n\n"
            f"👉 Reply *approve {short_id}* to authorize & execute\n"
            f"👉 Reply *reject {short_id}* to decline & cancel\n"
            f"💬 Or reply with changes: _e.g., 'Change tone to formal'_"
        )

def format_action_executed_notification(
    action_title: str,
    approval_id: str,
    result_summary: str,
    platform: str = PLATFORM_TELEGRAM
) -> str:
    """Notification confirming that an approved action was executed via MCP."""
    short_id = approval_id[:8]
    if platform.lower().strip() == PLATFORM_TELEGRAM:
        safe_title = action_title.replace("_", "\\_")
        return (
            f"✅ *ACTION EXECUTED SUCCESSFULLY*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Action:* {safe_title}\n"
            f"🔑 *Approval ID:* `{short_id}`\n"
            f"📡 *Execution Result:*\n```\n{result_summary.strip()}\n```\n\n"
            f"🔒 Immutable audit log recorded in SQLite WAL."
        )
    else:
        return (
            f"✅ *ACTION EXECUTED SUCCESSFULLY*\n"
            f"-----------------------------------------\n"
            f"📌 *Action:* *{action_title}*\n"
            f"🔑 *Approval ID:* *{short_id}*\n"
            f"📡 *Execution Result:*\n{result_summary}\n\n"
            f"🔒 Immutable audit log recorded in SQLite WAL."
        )

def format_action_rejected_notification(
    action_title: str,
    approval_id: str,
    reason: Optional[str] = None,
    platform: str = PLATFORM_TELEGRAM
) -> str:
    """Notification confirming that a staged action was declined and aborted."""
    short_id = approval_id[:8]
    if platform.lower().strip() == PLATFORM_TELEGRAM:
        safe_title = action_title.replace("_", "\\_")
        safe_reason = reason.replace("_", "\\_") if reason else ""
        reason_str = f"\n📝 *Reason:* _{safe_reason}_" if safe_reason else ""
        return (
            f"🚫 *ACTION CANCELLED BY USER*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Action:* {safe_title}\n"
            f"🔑 *Approval ID:* `{short_id}`{reason_str}\n\n"
            f"🛡️ Action safely discarded. No external transmissions made."
        )
    else:
        reason_str = f"\n📝 *Reason:* _{reason}_" if reason else ""
        return (
            f"🚫 *ACTION CANCELLED BY USER*\n"
            f"-----------------------------------------\n"
            f"📌 *Action:* *{action_title}*\n"
            f"🔑 *Approval ID:* *{short_id}*{reason_str}\n\n"
            f"🛡️ Action safely discarded. No external transmissions made."
        )

# ==============================================================================
# 5. CLARIFICATION & QUERY FORMATTERS
# ==============================================================================

def format_clarification_query(
    context_title: str,
    question: str,
    options: Optional[List[str]] = None,
    recommended_option_index: int = 1,
    platform: str = PLATFORM_TELEGRAM
) -> str:
    """
    Formats a structured query asking Mohil for clarifications
    when a user request or incoming event has ambiguous options.
    """
    clean_platform = platform.lower().strip()
    options_text = ""
    if options:
        opt_lines = []
        for i, opt in enumerate(options, 1):
            badge = " *(Recommended)*" if i == recommended_option_index else ""
            if clean_platform == PLATFORM_TELEGRAM:
                opt_lines.append(f"  *{i}.* {opt}{badge}")
            else:
                opt_lines.append(f"  *{i}.* {opt}{badge}")
        options_text = "\n" + "\n".join(opt_lines) + "\n\nReply with your preferred number (e.g. *1* or *2*)."

    if clean_platform == PLATFORM_TELEGRAM:
        return (
            f"❓ *EXECUTIVE CLARIFICATION NEEDED*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📌 *Context:* {context_title}\n\n"
            f"💬 {question}{options_text}"
        )
    else:
        return (
            f"❓ *EXECUTIVE CLARIFICATION NEEDED*\n"
            f"-----------------------------------------\n"
            f"📌 *Context:* *{context_title}*\n\n"
            f"💬 {question}{options_text}"
        )

# ==============================================================================
# 6. LLM PROMPT TEMPLATES FOR REASONING ENGINE
# ==============================================================================

def build_recruiter_triage_prompt(
    sender: str,
    subject: str,
    body: str,
    detected_intent: str,
    phishing_risk: str,
    candidate_name: str = PRINCIPAL_USER_NAME,
    platform: str = PLATFORM_TELEGRAM
) -> str:
    """Prompt for evaluating recruiter inquiries and proposing a guarded draft."""
    return (
        f"You are {AI_ASSISTANT_NAME}, reviewing an incoming recruiter email for {candidate_name}.\n"
        f"Sender: {sender}\n"
        f"Subject: {subject}\n"
        f"Detected Intent: {detected_intent}\n"
        f"Phishing Risk Assessment: {phishing_risk}\n\n"
        f"Email Content:\n{body}\n\n"
        f"Task:\n"
        f"1. Summarize the opportunity in 1-2 sentences.\n"
        f"2. Check for security or phishing risks.\n"
        f"3. Draft a polite, highly professional reply (max 3-4 sentences).\n"
        f"4. Remind {candidate_name} that this reply will be staged in the Approvals Gate and requires authorization before sending."
    )

def build_daily_briefing_prompt(
    candidate_name: str,
    priorities_summary: str,
    overdue_count: int,
    unread_emails_count: int,
    pending_approvals_count: int,
    platform: str = PLATFORM_TELEGRAM
) -> str:
    """Prompt for synthesizing the high-level daily morning briefing."""
    return (
        f"Synthesize an executive morning briefing for {candidate_name}.\n"
        f"- Target Platform: {platform.upper()}\n"
        f"- Unread Recruiter Emails: {unread_emails_count}\n"
        f"- Actions Staged Awaiting Approval: {pending_approvals_count}\n"
        f"- Overdue Tasks: {overdue_count}\n"
        f"- Key Priorities Today:\n{priorities_summary}\n\n"
        f"Provide a crisp, motivating 2-3 sentence strategic guidance summary. "
        f"Highlight execution efficiency and deadline management."
    )

def build_linkedin_ghostwrite_prompt(
    topic: str,
    key_takeaways: str,
    candidate_name: str = PRINCIPAL_USER_NAME,
    platform: str = PLATFORM_TELEGRAM
) -> str:
    """Prompt for ghostwriting an authentic, professional LinkedIn post."""
    return (
        f"Ghostwrite an authentic LinkedIn post for {candidate_name} ({PRINCIPAL_DEGREE} '27).\n"
        f"Topic: {topic}\n"
        f"Key Takeaways: {key_takeaways}\n\n"
        f"Guidelines:\n"
        f"- Compelling 1-line hook.\n"
        f"- Insightful, technically grounded body (4-6 sentences, short paragraphs).\n"
        f"- Meaningful call to action.\n"
        f"- 3-5 relevant industry hashtags (e.g. #AI, #MachineLearning, #Python, #AutonomousAgents).\n"
        f"- Maintain 100% factual honesty. Do not exaggerate.\n"
        f"- Note: This post will be staged in the approvals queue and won't be published without permission."
    )

def build_ambiguity_resolution_prompt(
    user_instruction: str,
    missing_aspects: List[str],
    platform: str = PLATFORM_TELEGRAM
) -> str:
    """Prompt instructing the LLM to formulate clarifying questions back to Mohil."""
    missing_str = ", ".join(missing_aspects)
    return (
        f"The user gave the following request: \"{user_instruction}\"\n"
        f"The request is ambiguous or missing critical information: {missing_str}.\n\n"
        f"Formulate a friendly, concise clarification query asking the user to choose between 2-3 concrete options. "
        f"Ensure it is optimized for {platform.upper()} mobile chat."
    )
