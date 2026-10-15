"""LLM Orchestration Service for NVIDIA NIM Multi-Model Pool and Local AI Fallback."""
import logging
from typing import Optional, List, Dict, Any
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

def generate_completion(
    prompt: str,
    system_prompt: Optional[str] = None,
    task_type: str = "general",
    max_tokens: int = 1024,
    temperature: float = 0.6
) -> Optional[str]:
    """
    Executes a chat completion across the configured AI provider.
    Supported task_types: 'reasoning', 'general', 'vision'.
    Gracefully falls back to None on timeout or network error.
    """
    if settings.AI_PROVIDER != "nvidia_nim":
        return None

    # Select appropriate model and key from multi-model pool
    if task_type == "reasoning":
        api_key = settings.NVIDIA_REASONING_KEY or settings.NVIDIA_GENERAL_KEY
        model_name = settings.NVIDIA_REASONING_MODEL
    elif task_type == "vision":
        api_key = settings.NVIDIA_VISION_KEY or settings.NVIDIA_GENERAL_KEY
        model_name = settings.NVIDIA_VISION_MODEL
    else:
        api_key = settings.NVIDIA_GENERAL_KEY or settings.NVIDIA_REASONING_KEY
        model_name = settings.NVIDIA_GENERAL_MODEL

    if not api_key:
        logger.warning("NVIDIA NIM API key not configured for task_type: %s", task_type)
        return None

    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    url = f"{settings.NVIDIA_BASE_URL.rstrip('/')}/chat/completions"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.error("NVIDIA NIM API Error (%d): %s", resp.status_code, resp.text)
                return None
            data = resp.json()
            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content")
            
            # Fallback for reasoning models where answer may be within reasoning_content
            if not content and message.get("reasoning_content"):
                reasoning = message.get("reasoning_content")
                # Look for drafted responses or final lines
                lines = [l.strip() for l in reasoning.splitlines() if l.strip()]
                if lines:
                    content = lines[-1]
            return content.strip() if content else None
    except Exception as e:
        logger.error("Failed invoking NVIDIA NIM (%s): %s", model_name, str(e))
        return None


def draft_recruiter_reply_with_ai(
    sender: str,
    subject: str,
    body: str,
    detected_intent: str,
    candidate_name: str = "Mohil",
    background_summary: str = "B.Tech in CSE with Artificial Intelligence at Mar Baselios Christian College '27"
) -> Optional[str]:
    """Generates an intelligent recruiter reply using Meta Muse Glimmer."""
    system_prompt = (
        f"You are Meiyon, an executive AI personal manager representing {candidate_name}. "
        "Draft a polite, professional, and succinct email response. "
        "Keep it under 4 sentences. Maintain 100% factual accuracy."
    )
    prompt = (
        f"Candidate: {candidate_name} ({background_summary})\n"
        f"From Recruiter: {sender}\n"
        f"Subject: {subject}\n"
        f"Intent: {detected_intent}\n"
        f"Email Content:\n{body}\n\n"
        "Draft the professional response now:"
    )
    return generate_completion(
        prompt=prompt,
        system_prompt=system_prompt,
        task_type="general",
        max_tokens=512,
        temperature=0.5
    )


def synthesize_executive_briefing_with_ai(
    priorities_text: str,
    unread_count: int,
    pending_approvals: int,
    candidate_name: str = "Mohil"
) -> Optional[str]:
    """Synthesizes high-level executive strategic guidance using Nemotron Reasoning."""
    system_prompt = (
        f"You are Meiyon, the executive strategic advisor for {candidate_name}. "
        "Provide a crisp, 2-3 sentence strategic morning briefing. "
        "Focus on execution efficiency, deadline awareness, and high-impact commitments."
    )
    prompt = (
        f"Executive: {candidate_name}\n"
        f"Unread Inquiries: {unread_count}\n"
        f"Pending Security Approvals: {pending_approvals}\n"
        f"Key Priorities Scheduled Today:\n{priorities_text}\n\n"
        "Synthesize the strategic daily briefing:"
    )
    return generate_completion(
        prompt=prompt,
        system_prompt=system_prompt,
        task_type="reasoning",
        max_tokens=1024,
        temperature=0.6
    )
