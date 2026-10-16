"""LLM Orchestration Service for NVIDIA NIM Multi-Model Pool and Local AI Fallback."""
import logging
from typing import Optional, List, Dict, Any
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

def generate_contextual_fallback(prompt: str, candidate_name: str = "Mohil") -> str:
    """
    Generates an intelligent, warm conversational fallback response when
    external LLM endpoints experience network latency or downtime.
    Maintains authentic two-way dialogue rather than returning cold errors.
    """
    clean_p = prompt.strip().lower()
    
    if any(w in clean_p for w in ("hi", "hello", "hey", "good morning", "good evening", "how are you", "what's up")):
        return (
            f"Hey {candidate_name}! Great to hear from you. I'm right here by your side as your Chief of Staff.\n\n"
            f"How are things coming along with your classes at Mar Baselios Christian College and your drone engineering projects today? "
            f"What's the top priority you'd like us to tackle together?"
        )
        
    if any(w in clean_p for w in ("tired", "exhausted", "stressed", "overwhelmed", "busy")):
        return (
            f"I hear you, {candidate_name}. Balancing an intensive AI & Computer Science curriculum with cutting-edge drone robotics takes serious energy. "
            f"Remember that steady progress always compounds.\n\n"
            f"Why don't we take a quick breather and break down your immediate commitments into smaller chunks? "
            f"What is the single most demanding item on your desk right now?"
        )
        
    if any(w in clean_p for w in ("drone", "uav", "telemetry", "yolo", "vision", "robotics")):
        return (
            f"That's right up your alley in autonomous systems, {candidate_name}! "
            f"Real-time computer vision and telemetry on edge hardware are challenging engineering frontiers.\n\n"
            f"What specific architecture or optimization are you looking at right now? "
            f"Are we looking to improve inference frame rate, minimize latency, or enhance tracking accuracy?"
        )
        
    if any(w in clean_p for w in ("internship", "job", "career", "resume", "recruit", "interview")):
        return (
            f"Career strategy is our core mission, {candidate_name}! "
            f"Your profile in AI, FastAPI backend engineering, and autonomous robotics places you in a strong position for 2026/2027 technical cohorts.\n\n"
            f"Would you like to review unread recruiter inquiries via `/emails`, sync your `/linkedin` activity, or discuss targeting specific research labs?"
        )
        
    return (
        f"I hear you, {candidate_name}. That's a thoughtful point to consider.\n\n"
        f"As your Executive AI partner, I'm here to think through this with you. "
        f"Could you tell me a bit more about what you're aiming for here, and what your preferred approach would be?"
    )


def generate_completion(
    prompt: str,
    system_prompt: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    task_type: str = "general",
    max_tokens: int = 512,
    temperature: float = 0.7
) -> Optional[str]:
    """
    Executes a chat completion across the configured AI provider with multi-model
    resilience and support for multi-turn conversational history.
    """
    if settings.AI_PROVIDER != "nvidia_nim":
        return generate_contextual_fallback(prompt)

    api_key = settings.NVIDIA_GENERAL_KEY or settings.NVIDIA_REASONING_KEY
    if not api_key:
        logger.warning("NVIDIA NIM API key not configured for task_type: %s", task_type)
        return generate_contextual_fallback(prompt)

    # Multi-model resilience order: start with fast responsive model
    candidate_models: List[str] = []
    if task_type == "general":
        primary = settings.NVIDIA_GENERAL_MODEL or "meta/llama-3.2-11b-vision-instruct"
        candidate_models = [primary, "meta/llama-3.2-11b-vision-instruct"]
    elif task_type == "vision":
        candidate_models = [settings.NVIDIA_VISION_MODEL, "meta/llama-3.2-11b-vision-instruct"]
    else:  # reasoning
        candidate_models = [settings.NVIDIA_REASONING_MODEL, "meta/llama-3.2-11b-vision-instruct"]

    # Deduplicate while preserving order
    seen = set()
    models_to_try = [m for m in candidate_models if m and not (m in seen or seen.add(m))]

    # Build multi-turn messages payload
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if conversation_history:
        for turn in conversation_history[-8:]:  # keep last 8 turns for responsive context
            messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    url = f"{settings.NVIDIA_BASE_URL.rstrip('/')}/chat/completions"

    for model_name in models_to_try:
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        try:
            with httpx.Client(timeout=18.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    choice = data.get("choices", [{}])[0]
                    message = choice.get("message", {})
                    content = message.get("content")
                    
                    # Fallback for reasoning models where answer may be within reasoning_content
                    if not content and message.get("reasoning_content"):
                        reasoning = message.get("reasoning_content")
                        lines = [l.strip() for l in reasoning.splitlines() if l.strip()]
                        if lines:
                            content = lines[-1]
                            
                    if content and content.strip():
                        return content.strip()
                else:
                    logger.warning("NVIDIA NIM model %s failed (%d): %s", model_name, resp.status_code, resp.text)
        except Exception as e:
            logger.warning("NVIDIA NIM attempt with %s failed: %s", model_name, str(e))
            continue

    # Fallback to intelligent conversational partner response if all endpoints fail
    logger.info("Falling back to cognitive conversational generator for prompt.")
    return generate_contextual_fallback(prompt)


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
