"""API Routes for Live Google Search, Web Intelligence & Autonomous Learning (SerpApi)."""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.services import search_service

router = APIRouter(prefix="/api/search", tags=["Live Google Search & Web Intelligence"])


class LearnTopicRequest(BaseModel):
    topic: str


@router.get("/status")
def get_search_status():
    """Returns connectivity and availability status of the SerpApi Google Search engine."""
    available = search_service.is_search_available()
    return {
        "status": "ready" if available else "missing_key",
        "serpapi_available": available,
        "engine": "google"
    }


@router.get("")
def perform_google_search(
    q: str = Query(..., description="Query string to search on Google"),
    num: int = Query(5, ge=1, le=10, description="Number of results to retrieve")
):
    """Executes a real-time Google search via SerpApi and returns structured results."""
    if not search_service.is_search_available():
        raise HTTPException(status_code=503, detail="SerpApi API key not configured on server.")
    results = search_service.search_google(query=q, num=num)
    summary = search_service.search_and_summarize(query=q, max_results=num)
    return {
        "query": q,
        "summary": summary,
        "raw_results": results
    }


@router.post("/learn")
def learn_topic_from_web(req: LearnTopicRequest):
    """Researches a topic on Google and automatically commits findings to the self-learning memory bank."""
    if not search_service.is_search_available():
        raise HTTPException(status_code=503, detail="SerpApi API key not configured on server.")
    res = search_service.search_and_learn_topic(req.topic)
    return {
        "status": "success",
        "topic": req.topic,
        "message": res
    }

