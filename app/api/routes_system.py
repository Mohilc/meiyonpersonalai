"""System administration, backup/restore, and health endpoints."""
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.config import settings
from app.database import backup_database, restore_database
from app.services import audit_service

router = APIRouter(prefix="/api/system", tags=["System & Maintenance"])

class ModeUpdateRequest(BaseModel):
    mode: str  # ASSISTED, SUPERVISED, RESTRICTED_AUTONOMY

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "autonomy_mode": settings.AUTONOMY_MODE,
        "timezone": settings.TIMEZONE
    }

@router.post("/mode")
def update_autonomy_mode(payload: ModeUpdateRequest):
    allowed = ["ASSISTED", "SUPERVISED", "RESTRICTED_AUTONOMY"]
    mode_upper = payload.mode.upper()
    if mode_upper not in allowed:
        raise HTTPException(status_code=400, detail=f"Mode must be one of {allowed}")
    old_mode = settings.AUTONOMY_MODE
    settings.AUTONOMY_MODE = mode_upper
    audit_service.log_audit(
        action_type="AUTONOMY_MODE_CHANGED",
        target_entity="system",
        details={"old_mode": old_mode, "new_mode": mode_upper},
        status="SUCCESS",
        mode=mode_upper
    )
    return {"message": f"Autonomy mode updated to {mode_upper}", "current_mode": mode_upper}

@router.post("/backup")
def create_backup():
    """Triggers an online, point-in-time SQLite backup."""
    backup_path = backup_database()
    audit_service.log_audit(
        action_type="DATABASE_BACKUP_CREATED",
        target_entity="database",
        details={"backup_file": str(backup_path.name)},
        status="SUCCESS"
    )
    return {
        "message": "Backup created successfully",
        "backup_filename": backup_path.name,
        "path": str(backup_path)
    }

@router.get("/backups")
def list_backups():
    """Lists available database backups."""
    files = list(settings.BACKUP_DIR.glob("manager_backup_*.db"))
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return [
        {
            "filename": f.name,
            "size_bytes": f.stat().st_size,
            "created_at": f.stat().st_mtime
        }
        for f in files
    ]

@router.post("/restore")
def restore_from_backup(filename: str = Query(...)):
    """Restores database from specified backup filename."""
    backup_file = settings.BACKUP_DIR / filename
    if not backup_file.exists():
        raise HTTPException(status_code=404, detail="Specified backup file not found")
        
    try:
        restore_database(backup_file)
        audit_service.log_audit(
            action_type="DATABASE_RESTORED",
            target_entity="database",
            details={"restored_from": filename},
            status="SUCCESS"
        )
        return {"message": f"Database successfully restored from {filename}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Restore failed: {str(e)}")
