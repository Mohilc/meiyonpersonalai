"""API endpoints for Self-Learning Engine, Memory Management, and Adaptive Persona."""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.models.learning import (
    LearnedMemory,
    LearnedMemoryCreate,
    LearningFeedbackCreate
)
from app.services import learning_service

router = APIRouter(prefix="/api/learning", tags=["Self-Learning & Adaptive Persona"])


@router.get("/memories", response_model=List[LearnedMemory])
def list_learned_memories(category: Optional[str] = Query(None)):
    """Retrieves all active learned memories, preferences, and persona guidelines."""
    return learning_service.list_active_memories(category=category)


@router.post("/memories", response_model=LearnedMemory)
def create_learned_memory(payload: LearnedMemoryCreate):
    """Manually teaches the AI a new rule, user preference, or factual memory."""
    return learning_service.add_or_update_memory(
        category=payload.category.value,
        key=payload.key,
        content=payload.content,
        source=payload.source.value,
        confidence_score=payload.confidence_score
    )


@router.delete("/memories/{memory_id}")
def delete_learned_memory(memory_id: str):
    """Deactivates a learned memory or preference rule."""
    success = learning_service.deactivate_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Learned memory not found")
    return {"message": f"Memory '{memory_id}' successfully deactivated."}


@router.post("/feedback")
def submit_tone_feedback(payload: LearningFeedbackCreate):
    """Submits feedback on conversational style and adapts tone immediately."""
    feedback_text = payload.user_feedback
    if payload.desired_tone:
        feedback_text += f" | Preferred tone: {payload.desired_tone}"

    mem = learning_service.add_or_update_memory(
        category="FEEDBACK",
        key=f"feedback_{abs(hash(payload.user_feedback)) % 100000}",
        content=feedback_text,
        source="FEEDBACK_ADJUSTMENT"
    )
    return {
        "message": "Feedback recorded! Persona and response tone adapted successfully.",
        "memory": mem
    }


@router.get("/prompt-context")
def view_compiled_prompt_context():
    """Returns the compiled self-learning instructions injected into AI prompts."""
    return {"prompt_instructions": learning_service.compile_learned_prompt_instructions()}

