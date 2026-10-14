"""Service for managing the verified User Profile."""
import json
from datetime import datetime, timezone
from app.database import get_db_connection
from app.models.profile import UserProfile, UserProfileUpdate

def get_profile() -> UserProfile:
    """Fetches the singleton user profile."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM user_profile WHERE id = 1;")
        row = cur.fetchone()
        if not row:
            raise RuntimeError("User profile not found. Database must be initialized.")
        return UserProfile(
            id=row["id"],
            full_name=row["full_name"],
            education=row["education"],
            college=row["college"],
            expected_graduation=row["expected_graduation"],
            technical_interests=json.loads(row["technical_interests"]),
            career_objectives=json.loads(row["career_objectives"]),
            operating_environment=row["operating_environment"],
            existing_skills=json.loads(row["existing_skills"]),
            budget_preference=row["budget_preference"],
            timezone=row["timezone"],
            updated_at=row["updated_at"]
        )
    finally:
        conn.close()

def update_profile(update: UserProfileUpdate) -> UserProfile:
    """Updates user profile attributes cleanly without inventing data."""
    current = get_profile()
    updated_at = datetime.now(timezone.utc).isoformat()
    
    full_name = update.full_name if update.full_name is not None else current.full_name
    education = update.education if update.education is not None else current.education
    college = update.college if update.college is not None else current.college
    expected_graduation = update.expected_graduation if update.expected_graduation is not None else current.expected_graduation
    technical_interests = update.technical_interests if update.technical_interests is not None else current.technical_interests
    career_objectives = update.career_objectives if update.career_objectives is not None else current.career_objectives
    operating_environment = update.operating_environment if update.operating_environment is not None else current.operating_environment
    existing_skills = update.existing_skills if update.existing_skills is not None else current.existing_skills
    budget_preference = update.budget_preference if update.budget_preference is not None else current.budget_preference
    tz = update.timezone if update.timezone is not None else current.timezone

    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            UPDATE user_profile SET
                full_name = ?,
                education = ?,
                college = ?,
                expected_graduation = ?,
                technical_interests = ?,
                career_objectives = ?,
                operating_environment = ?,
                existing_skills = ?,
                budget_preference = ?,
                timezone = ?,
                updated_at = ?
            WHERE id = 1;
            """, (
                full_name,
                education,
                college,
                expected_graduation,
                json.dumps(technical_interests),
                json.dumps(career_objectives),
                operating_environment,
                json.dumps(existing_skills),
                budget_preference,
                tz,
                updated_at
            ))
        return get_profile()
    finally:
        conn.close()
