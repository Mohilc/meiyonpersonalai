"""Pydantic schemas for User Profile."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserProfile(BaseModel):
    id: int = 1
    full_name: str
    education: str
    college: str
    expected_graduation: str
    technical_interests: List[str]
    career_objectives: List[str]
    operating_environment: str
    existing_skills: List[str]
    budget_preference: str
    timezone: str
    updated_at: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    education: Optional[str] = None
    college: Optional[str] = None
    expected_graduation: Optional[str] = None
    technical_interests: Optional[List[str]] = None
    career_objectives: Optional[List[str]] = None
    operating_environment: Optional[str] = None
    existing_skills: Optional[List[str]] = None
    budget_preference: Optional[str] = None
    timezone: Optional[str] = None
