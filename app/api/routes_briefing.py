"""API Route for Daily Executive Briefing."""
from fastapi import APIRouter
from app.models.briefing import DailyBriefing
from app.services import briefing_service

router = APIRouter(prefix="/api/briefing", tags=["Briefing"])

@router.get("", response_model=DailyBriefing)
def get_daily_briefing():
    return briefing_service.generate_daily_briefing()
