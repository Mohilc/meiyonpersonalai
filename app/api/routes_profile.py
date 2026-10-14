"""API Routes for User Profile."""
from fastapi import APIRouter, HTTPException
from app.models.profile import UserProfile, UserProfileUpdate
from app.services import profile_service, audit_service

router = APIRouter(prefix="/api/profile", tags=["Profile"])

@router.get("", response_model=UserProfile)
def get_user_profile():
    return profile_service.get_profile()

@router.put("", response_model=UserProfile)
def update_user_profile(payload: UserProfileUpdate):
    updated = profile_service.update_profile(payload)
    audit_service.log_audit(
        action_type="PROFILE_UPDATED",
        target_entity="user_profile",
        details=payload.model_dump(exclude_unset=True),
        status="SUCCESS"
    )
    return updated
