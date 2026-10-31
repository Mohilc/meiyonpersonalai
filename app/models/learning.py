"""Data models for Self-Learning Engine and User Persona Adaptation."""
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class MemoryCategoryEnum(str, Enum):
    PREFERENCE = "PREFERENCE"
    COMMUNICATION_STYLE = "COMMUNICATION_STYLE"
    FACTUAL_KNOWLEDGE = "FACTUAL_KNOWLEDGE"
    CORRECTION = "CORRECTION"
    ROUTINE = "ROUTINE"
    FEEDBACK = "FEEDBACK"

class MemorySourceEnum(str, Enum):
    EXPLICIT_USER_COMMAND = "EXPLICIT_USER_COMMAND"
    AUTOMATIC_EXTRACTION = "AUTOMATIC_EXTRACTION"
    FEEDBACK_ADJUSTMENT = "FEEDBACK_ADJUSTMENT"

class LearnedMemoryCreate(BaseModel):
    category: MemoryCategoryEnum = MemoryCategoryEnum.PREFERENCE
    key: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=1000)
    source: MemorySourceEnum = MemorySourceEnum.EXPLICIT_USER_COMMAND
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)

class LearnedMemory(BaseModel):
    id: str
    category: MemoryCategoryEnum
    key: str
    content: str
    source: MemorySourceEnum
    confidence_score: float
    is_active: bool
    created_at: str
    updated_at: str

class LearningFeedbackCreate(BaseModel):
    user_feedback: str
    desired_tone: Optional[str] = None
    rating: Optional[int] = Field(default=None, ge=1, le=5)

