"""API Routes for Tasks."""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.task import TaskCreate, TaskUpdate, TaskResponse
from app.services import task_service, audit_service

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("", response_model=List[TaskResponse])
def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    return task_service.list_tasks(status=status, priority=priority, category=category)

@router.post("", response_model=TaskResponse, status_code=201)
def create_task(payload: TaskCreate):
    created = task_service.create_task(payload)
    audit_service.log_audit(
        action_type="TASK_CREATED",
        target_entity="task",
        details={"task_id": created.id, "title": created.title, "priority": created.priority.value},
        status="SUCCESS"
    )
    return created

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: str):
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate):
    updated = task_service.update_task(task_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    audit_service.log_audit(
        action_type="TASK_UPDATED",
        target_entity="task",
        details={"task_id": task_id, "updates": payload.model_dump(exclude_unset=True)},
        status="SUCCESS"
    )
    return updated

@router.post("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: str):
    completed = task_service.complete_task(task_id)
    if not completed:
        raise HTTPException(status_code=404, detail="Task not found")
    audit_service.log_audit(
        action_type="TASK_COMPLETED",
        target_entity="task",
        details={"task_id": task_id, "title": completed.title},
        status="SUCCESS"
    )
    return completed

@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: str):
    deleted = task_service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    audit_service.log_audit(
        action_type="TASK_DELETED",
        target_entity="task",
        details={"task_id": task_id},
        status="SUCCESS"
    )
    return None
