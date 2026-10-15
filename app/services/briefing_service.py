"""Service for generating Daily Prioritized Executive Briefings."""
from datetime import datetime, timezone, timedelta
from typing import List
from zoneinfo import ZoneInfo
from app.config import settings
from app.models.briefing import DailyBriefing
from app.models.task import TaskStatusEnum, PriorityEnum, TaskResponse
from app.services.task_service import list_tasks
from app.services.audit_service import list_approvals
from app.services.reminder_service import list_reminders
from app.services.profile_service import get_profile

def generate_daily_briefing() -> DailyBriefing:
    """
    Synthesizes current database state into a comprehensive daily briefing.
    Uses user timezone (default Asia/Kolkata).
    """
    profile = get_profile()
    user_tz_str = profile.timezone or settings.TIMEZONE
    try:
        user_tz = ZoneInfo(user_tz_str)
    except Exception:
        user_tz = ZoneInfo("Asia/Kolkata")
        
    now_local = datetime.now(user_tz)
    now_utc = datetime.now(timezone.utc)
    now_iso = now_utc.isoformat()
    
    # Date bounds for today in user timezone
    today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = now_local.replace(hour=23, minute=59, second=59, microsecond=999999)
    next_week = today_end + timedelta(days=7)

    all_tasks = list_tasks()
    
    # Filter tasks
    open_tasks = [t for t in all_tasks if t.status in (TaskStatusEnum.PENDING, TaskStatusEnum.IN_PROGRESS)]
    
    # Overdue tasks
    overdue: List[TaskResponse] = []
    todays_tasks: List[TaskResponse] = []
    upcoming: List[TaskResponse] = []
    
    for t in open_tasks:
        if t.due_date:
            try:
                task_dt = datetime.fromisoformat(t.due_date.replace("Z", "+00:00"))
                # If naive, assume user local timezone
                if task_dt.tzinfo is None:
                    task_dt = task_dt.replace(tzinfo=user_tz)
                else:
                    task_dt = task_dt.astimezone(user_tz)
                    
                if task_dt < today_start:
                    overdue.append(t)
                elif today_start <= task_dt <= today_end:
                    todays_tasks.append(t)
                elif today_end < task_dt <= next_week:
                    upcoming.append(t)
            except Exception:
                # If unparseable date, keep in general pool
                pass
                
    # Top 3 Priorities: Sorted by Priority (P1 > P2 > P3 > P4) then earliest deadline
    top_three = open_tasks[:3]
    
    # Approvals pending
    pending_approvals = list_approvals(status="PENDING")
    
    # Active reminders
    active_rems = list_reminders(status="SCHEDULED")
    
    # Greeting based on time of day
    hour = now_local.hour
    if hour < 12:
        greeting = f"Good morning, {profile.full_name}."
    elif hour < 17:
        greeting = f"Good afternoon, {profile.full_name}."
    else:
        greeting = f"Good evening, {profile.full_name}."
        
    # Generate executive summary
    summary_parts = []
    if overdue:
        summary_parts.append(f"Attention needed: {len(overdue)} overdue commitment(s).")
    if todays_tasks:
        summary_parts.append(f"You have {len(todays_tasks)} scheduled task(s) due today.")
    if pending_approvals:
        summary_parts.append(f"{len(pending_approvals)} action(s) require your explicit approval.")
    if not summary_parts:
        summary_parts.append("Your schedule is in good order with no overdue items.")
        
    exec_summary = " ".join(summary_parts)
    
    # AI-Enhanced Strategic Synthesis using NVIDIA Nemotron
    if settings.AI_PROVIDER != "local_heuristic":
        try:
            from app.services import llm_service
            p_text = "\n".join([f"- {t.title} (Priority: {t.priority})" for t in top_three]) or "No urgent tasks."
            ai_synthesis = llm_service.synthesize_executive_briefing_with_ai(
                priorities_text=p_text,
                unread_count=len(todays_tasks) + len(overdue),
                pending_approvals=len(pending_approvals),
                candidate_name=profile.full_name
            )
            if ai_synthesis:
                exec_summary = f"{exec_summary} | Strategic AI Insight: {ai_synthesis}"
        except Exception:
            pass
    
    # Recommendations
    recommendations = []
    if overdue:
        recommendations.append(f"Clear or reschedule the overdue task: '{overdue[0].title}'")
    if pending_approvals:
        recommendations.append("Review pending approval requests in the Security & Approvals panel.")
    if top_three:
        recommendations.append(f"Focus deep work block on top priority: '{top_three[0].title}'")
    else:
        recommendations.append("Add your study milestones and job search targets for the week.")

    return DailyBriefing(
        generated_at=now_iso,
        timezone=user_tz_str,
        greeting=greeting,
        top_three_priorities=top_three,
        todays_tasks=todays_tasks,
        upcoming_deadlines=upcoming,
        overdue_commitments=overdue,
        tasks_awaiting_approval=pending_approvals,
        active_reminders_count=len(active_rems),
        executive_summary=exec_summary,
        recommendations=recommendations
    )
