"""Models for Daily Briefing and Executive Summaries."""
from typing import List, Optional
from pydantic import BaseModel
from app.models.task import TaskResponse
from app.models.approval import ApprovalRequest

class DailyBriefing(BaseModel):
    generated_at: str
    timezone: str
    greeting: str
    top_three_priorities: List[TaskResponse]
    todays_tasks: List[TaskResponse]
    upcoming_deadlines: List[TaskResponse]
    overdue_commitments: List[TaskResponse]
    tasks_awaiting_approval: List[ApprovalRequest]
    active_reminders_count: int
    executive_summary: str
    recommendations: List[str]
