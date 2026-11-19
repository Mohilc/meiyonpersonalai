"""LangChain Agentic AI Orchestration Service for Meiyon.

Provides an autonomous ReAct/Tool-Calling Agent powered by LangChain and NVIDIA NIM:
- Binds college attendance, assignments, task commitments, Zapier MCP, Google Search,
  Gmail inbox, and self-learning memory into callable LangChain Tools.
- Enables multi-step reasoning, plan-and-solve execution, and factual grounding.
"""
import os
import json
import logging
from typing import Optional, List, Dict, Any

from app.config import settings
from app.models.task import TaskCreate, PriorityEnum, CategoryEnum, TaskSourceEnum, TaskStatusEnum
from app.models.academic import AttendanceStatusEnum, AssignmentStatusEnum
from app.services import (
    academic_service,
    task_service,
    learning_service,
    search_service,
    briefing_service,
    profile_service,
    mcp_service
)

logger = logging.getLogger(__name__)

# Lazy imports for LangChain to avoid startup failure if package is loading
try:
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI
    from langchain.agents import create_agent
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain packages not fully installed. Agentic service in fallback mode.")


# ==============================================================================
# 1. LANGCHAIN TOOL DEFINITIONS
# ==============================================================================

if LANGCHAIN_AVAILABLE:

    @tool
    def get_college_attendance() -> str:
        """Retrieves Mohil's live college attendance status, overall percentage,
        75% compliance alert, and detailed subject breakdown with classes needed."""
        try:
            summary = academic_service.get_attendance_summary()
            status_text = "Safe (Compliant >= 75%)" if summary.is_safe else "CRITICAL ALERT (< 75%)"
            lines = [
                f"Overall College Attendance: {summary.overall_percentage}% [{status_text}]",
                f"Total Classes: {summary.total_classes} | Attended: {summary.total_attended} | Absences: {summary.total_absent}",
                "Subject Breakdown:"
            ]
            for s in summary.subjects:
                sub_status = "Safe" if s.is_safe else f"LOW ATTENDANCE - need {s.classes_needed_for_75} classes to reach 75%"
                lines.append(f"• {s.subject}: {s.percentage}% ({s.attended}/{s.total_classes} classes) - {sub_status}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving attendance: {str(e)}"

    @tool
    def mark_subject_attendance(subject: str, status: str = "PRESENT", notes: Optional[str] = None) -> str:
        """Records attendance for a college class today.
        Args:
            subject: Name of the subject (e.g. AI, DBMS, OS, TOC, Mathematics)
            status: Either 'PRESENT' or 'ABSENT' (defaults to 'PRESENT')
            notes: Optional reason or note for this attendance entry
        """
        try:
            clean_status = status.upper().strip()
            if clean_status not in ("PRESENT", "ABSENT"):
                clean_status = "PRESENT"
            rec = academic_service.mark_attendance(
                subject=subject.strip(),
                status=clean_status,
                notes=notes
            )
            summary = academic_service.get_attendance_summary()
            return f"Recorded {rec.subject} as {rec.status.value} on {rec.date}. New overall attendance: {summary.overall_percentage}%."
        except Exception as e:
            return f"Error marking attendance: {str(e)}"

    @tool
    def get_pending_assignments() -> str:
        """Retrieves Mohil's academic assignments, deadlines, and pending homework."""
        try:
            assignments = academic_service.list_assignments()
            pending = [a for a in assignments if a.status == AssignmentStatusEnum.PENDING]
            if not pending:
                return "All clear! Zero pending college assignments right now."
            lines = [f"Found {len(pending)} pending assignment(s):"]
            for a in pending:
                lines.append(f"• [{a.subject}] {a.title} | Due: {a.due_date} (ID: {a.id[:8]})")
            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving assignments: {str(e)}"

    @tool
    def add_college_assignment(subject: str, title: str, due_date: str, description: Optional[str] = None) -> str:
        """Adds a new college assignment and deadline to the academic tracker.
        Args:
            subject: Subject name (e.g. Machine Learning, Computer Networks, AI)
            title: Title or topic of the assignment
            due_date: Submission deadline formatted as YYYY-MM-DD (or description of due date)
            description: Optional details, requirements, or submission guidelines
        """
        try:
            ass = academic_service.add_assignment(
                subject=subject.strip(),
                title=title.strip(),
                due_date=due_date.strip(),
                description=description
            )
            return f"Added assignment '{ass.title}' for {ass.subject} with deadline {ass.due_date}."
        except Exception as e:
            return f"Error adding assignment: {str(e)}"

    @tool
    def list_scheduled_tasks() -> str:
        """Lists active scheduled tasks, commitments, and daily priorities."""
        try:
            tasks = task_service.list_tasks(status=TaskStatusEnum.PENDING)
            if not tasks:
                return "No pending tasks scheduled right now."
            lines = [f"Found {len(tasks)} active task commitments:"]
            for t in tasks:
                due_str = f" | Due: {t.due_date}" if t.due_date else ""
                lines.append(f"• [{t.priority.value}] {t.title}{due_str} (ID: {t.id[:8]})")
            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving tasks: {str(e)}"

    @tool
    def add_task_commitment(title: str, priority: str = "P2_HIGH", due_date: Optional[str] = None) -> str:
        """Creates a new task or commitment, synced with Zapier Tasks MCP.
        Args:
            title: What needs to be done
            priority: Priority level ('P1_URGENT', 'P2_HIGH', 'P3_MEDIUM', 'P4_LOW')
            due_date: Optional due date (YYYY-MM-DD or time)
        """
        try:
            p_map = {
                "P1": PriorityEnum.P1_URGENT, "URGENT": PriorityEnum.P1_URGENT,
                "P1_URGENT": PriorityEnum.P1_URGENT, "P2": PriorityEnum.P2_HIGH,
                "HIGH": PriorityEnum.P2_HIGH, "P2_HIGH": PriorityEnum.P2_HIGH,
                "P3": PriorityEnum.P3_MEDIUM, "MEDIUM": PriorityEnum.P3_MEDIUM,
                "P3_MEDIUM": PriorityEnum.P3_MEDIUM, "P4": PriorityEnum.P4_LOW,
                "LOW": PriorityEnum.P4_LOW, "P4_LOW": PriorityEnum.P4_LOW
            }
            p_enum = p_map.get(priority.upper().strip(), PriorityEnum.P2_HIGH)
            task = task_service.create_task(TaskCreate(
                title=title.strip(),
                priority=p_enum,
                due_date=due_date,
                category=CategoryEnum.CAREER if hasattr(CategoryEnum, "CAREER") else CategoryEnum.PROJECT,
                source=TaskSourceEnum.MANUAL
            ))
            return f"Created task: '{task.title}' [{task.priority.value}] (ID: {task.id[:8]})."
        except Exception as e:
            return f"Error creating task: {str(e)}"

    @tool
    def complete_task_commitment(task_id: str) -> str:
        """Marks a task commitment as finished or completed.
        Args:
            task_id: The ID or first 8 characters of the task ID
        """
        try:
            all_tasks = task_service.list_tasks()
            match = next((t for t in all_tasks if t.id.startswith(task_id.strip())), None)
            if not match:
                return f"No task found with ID prefix '{task_id}'."
            completed = task_service.complete_task(match.id)
            return f"Marked task '{completed.title}' as COMPLETED."
        except Exception as e:
            return f"Error completing task: {str(e)}"

    @tool
    def search_google_web(query: str) -> str:
        """Performs live real-time Google search via SerpApi for facts, news, documentation, or technical information.
        Args:
            query: The search query string
        """
        try:
            if not search_service.is_search_available():
                return "Google Search (SerpApi) is not configured in environment."
            result = search_service.search_and_summarize(query.strip(), max_results=3)
            return result or "No relevant search results found."
        except Exception as e:
            return f"Google search error: {str(e)}"

    @tool
    def get_recent_inbox_emails(limit: int = 4) -> str:
        """Fetches active unread/recent emails and recruiter communications from Gmail (via Zapier Mail MCP / IMAP).
        Args:
            limit: Number of emails to retrieve (1-5)
        """
        try:
            emails = mcp_service.get_active_inbox_emails(limit=limit, sync_live=False)
            if not emails:
                return "Your inbox is clear! No active unread emails found."
            lines = [f"Found {len(emails)} recent emails:"]
            for i, em in enumerate(emails, 1):
                snip = em.body.replace("\n", " ")[:120].strip()
                lines.append(f"{i}. From: {em.sender} | Subject: {em.subject}\n   Snippet: {snip}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error reading emails: {str(e)}"

    @tool
    def get_executive_briefing() -> str:
        """Retrieves today's complete executive briefing, top 3 priorities, overdue items, and pending sign-offs."""
        try:
            briefing = briefing_service.generate_daily_briefing()
            lines = ["Daily Executive Briefing:"]
            if briefing.top_three_priorities:
                lines.append("Top Priorities:")
                for i, t in enumerate(briefing.top_three_priorities, 1):
                    lines.append(f"{i}. {t.title} [{t.priority}]")
            else:
                lines.append("Top Priorities: No urgent priorities today.")
            lines.append(f"Overdue Tasks: {len(briefing.overdue_commitments)}")
            lines.append(f"Pending Approvals: {len(briefing.tasks_awaiting_approval)}")
            if briefing.executive_summary:
                lines.append(f"Executive Summary: {briefing.executive_summary}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error retrieving briefing: {str(e)}"

    @tool
    def remember_user_rule(preference_or_rule: str) -> str:
        """Teaches Meiyon a permanent preference, habit, or instruction (persisted to self-learning memory).
        Args:
            preference_or_rule: The rule, preference, or fact to remember (e.g. 'Call me bro', 'I study late at night')
        """
        try:
            import re
            key_slug = re.sub(r"[^a-z0-9_]+", "_", preference_or_rule[:25].lower()).strip("_")
            mem = learning_service.add_or_update_memory(
                category="PREFERENCE",
                key=f"user_{key_slug}",
                content=preference_or_rule.strip(),
                source="EXPLICIT_USER_COMMAND"
            )
            return f"Learned and saved to memory: '{mem.content}'."
        except Exception as e:
            return f"Error saving memory: {str(e)}"

    @tool
    def get_learned_memories() -> str:
        """Retrieves all active memories and preferences that Meiyon has learned about Mohil."""
        try:
            mems = learning_service.list_active_memories()
            if not mems:
                return "No custom learned memories recorded yet."
            lines = [f"Found {len(mems)} active learned memory rule(s):"]
            for m in mems:
                lines.append(f"• [{m.category.value}] {m.key}: {m.content}")
            return "\n".join(lines)
        except Exception as e:
            return f"Error reading memories: {str(e)}"

    ALL_AGENT_TOOLS = [
        get_college_attendance,
        mark_subject_attendance,
        get_pending_assignments,
        add_college_assignment,
        list_scheduled_tasks,
        add_task_commitment,
        complete_task_commitment,
        search_google_web,
        get_recent_inbox_emails,
        get_executive_briefing,
        remember_user_rule,
        get_learned_memories
    ]
else:
    ALL_AGENT_TOOLS = []


# ==============================================================================
# 2. AGENT INITIALIZATION & EXECUTION
# ==============================================================================

_AGENT_CACHE: Dict[str, Any] = {}

def get_agent_instance():
    """Initializes or returns cached LangChain agent with tool binding and NVIDIA NIM."""
    if not LANGCHAIN_AVAILABLE:
        return None

    if "agent" in _AGENT_CACHE:
        return _AGENT_CACHE["agent"]

    api_key = (
        settings.NVIDIA_GENERAL_KEY
        or settings.NVIDIA_REASONING_KEY
        or settings.AI_API_KEY
    )
    if not api_key:
        logger.warning("No NVIDIA API key configured for LangChain agent.")
        return None

    model_name = settings.NVIDIA_REASONING_MODEL or "mistralai/mistral-large-4-1t-a52b"

    try:
        llm = ChatOpenAI(
            base_url=settings.NVIDIA_BASE_URL,
            api_key=api_key,
            model=model_name,
            temperature=0.3,
            request_timeout=15.0,
            max_retries=1
        )

        profile = profile_service.get_profile()
        learned_rules = learning_service.compile_learned_prompt_instructions()
        learned_block = f"\n\nLearned User Preferences:\n{learned_rules}" if learned_rules else ""

        system_prompt = (
            f"You are Meiyon, the Executive Personal AI Manager & Partner for {profile.full_name}, "
            f"a B.Tech student in Computer Science & Engineering with AI (Class of 2027) at "
            f"Mar Baselios Christian College of Engineering & Technology, passionate about autonomous drone systems.\n\n"
            f"Core Operational Guidelines:\n"
            f"1. You have direct tools to check and update college attendance, assignments, tasks, emails, search Google, and store memories.\n"
            f"2. Use tools proactively whenever answering factual, academic, task, or search-related questions.\n"
            f"3. Maintain a warm, encouraging, conversational human tone while being efficient and clear.\n"
            f"4. Format responses cleanly for mobile screens with brief paragraphs and bullet points.\n"
            f"5. If attendance is below 75%, highlight the risk and needed classes clearly.\n"
            f"{learned_block}"
        )

        agent = create_agent(
            model=llm,
            tools=ALL_AGENT_TOOLS,
            system_prompt=system_prompt
        )
        _AGENT_CACHE["agent"] = agent
        logger.info("⚡ LangChain Agentic AI engine initialized with %d tools.", len(ALL_AGENT_TOOLS))
        return agent
    except Exception as e:
        logger.error("Failed to initialize LangChain agent: %s", str(e))
        return None


def run_agent(
    prompt: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    platform: str = "telegram"
) -> Optional[str]:
    """
    Executes prompt through the LangChain Agentic loop with tool calling.
    Returns agent's final reasoning response, or None if agent cannot run.
    """
    agent = get_agent_instance()
    if not agent:
        return None

    try:
        messages = []
        if conversation_history:
            for turn in conversation_history[-8:]:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                if not content:
                    continue
                if role == "user":
                    messages.append(("user", content))
                elif role == "assistant":
                    messages.append(("assistant", content))

        messages.append(("user", prompt))

        result = agent.invoke({"messages": messages})
        output_messages = result.get("messages", [])
        if output_messages:
            final_msg = output_messages[-1]
            content = getattr(final_msg, "content", "")
            if isinstance(content, str) and content.strip():
                return content.strip()
            elif isinstance(content, list):
                # Flatten list of content chunks
                parts = [str(p.get("text", p)) if isinstance(p, dict) else str(p) for p in content]
                return "\n".join(parts).strip()
        return None
    except Exception as e:
        logger.warning("LangChain agent execution fallback notice: %s", str(e))
        return None


def is_agent_available() -> bool:
    """Checks whether the LangChain agent is fully configured and ready."""
    return LANGCHAIN_AVAILABLE and bool(
        settings.NVIDIA_GENERAL_KEY or settings.NVIDIA_REASONING_KEY or settings.AI_API_KEY
    )
