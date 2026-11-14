"""Tasks & Important Data MCP Server for Personal AI Manager.

Provides standard Model Context Protocol (MCP) tools to:
- Create and schedule tasks with priorities (P1_URGENT down to P4_LOW)
- Mark important data, critical reminders, and key facts
- List active pending commitments
- Complete tasks and record truthful timestamps
- Synchronize seamlessly with Zapier MCP Tasks server (Google Tasks / Todoist / Notion)
"""
import os
import sys
import json
import uuid
import logging
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load local environment configuration (.env)
load_dotenv()

logger = logging.getLogger(__name__)

try:
    from mcp.server.mcpserver import MCPServer
except (ImportError, ModuleNotFoundError):
    try:
        from mcp.server import MCPServer
    except (ImportError, ModuleNotFoundError):
        try:
            from mcp.server.fastmcp import FastMCP as MCPServer
        except (ImportError, ModuleNotFoundError):
            class MCPServer:
                def __init__(self, name="mcp"):
                    self.name = name
                def tool(self, *args, **kwargs):
                    def decorator(fn):
                        return fn
                    return decorator
                def run(self, *args, **kwargs):
                    pass

# Initialize MCP Server
server = MCPServer("task-mcp")

# Zapier MCP Tasks Configuration
ZAPIER_TASKS_MCP_URL = os.getenv(
    "ZAPIER_TASKS_MCP_URL",
    "https://mcp.zapier.com/api/mcp/s/02292b48-0fbd-8ca5-88c8-021274846b43/mcp"
)
ZAPIER_TASKS_MCP_ID = os.getenv("ZAPIER_TASKS_MCP_ID", "02292b48-0fbd-8ca5-88c8-021274846b43")


def _zapier_tasks_call(tool_name: str, arguments: dict = None, timeout: int = 15) -> Optional[Dict]:
    """
    Calls a tool on the Zapier-hosted Tasks MCP server via JSON-RPC 2.0 over HTTP.
    Returns the parsed result dict on success, or None if the call fails.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    try:
        resp = requests.post(
            ZAPIER_TASKS_MCP_URL,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            timeout=timeout
        )
        if resp.status_code == 200:
            data = resp.json()
            if "result" in data:
                result = data["result"]
                if isinstance(result, dict) and "content" in result:
                    content = result["content"]
                    if isinstance(content, list) and content:
                        text = content[0].get("text", "")
                        try:
                            return json.loads(text)
                        except (json.JSONDecodeError, TypeError):
                            return {"raw": text}
                return result
    except Exception as e:
        logger.debug("Zapier Tasks MCP call note: %s", str(e))
    return None


def _is_zapier_tasks_available() -> bool:
    """Quick probe for Zapier Tasks MCP server."""
    try:
        payload = {"jsonrpc": "2.0", "id": "ping", "method": "tools/list", "params": {}}
        resp = requests.post(
            ZAPIER_TASKS_MCP_URL,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            timeout=5
        )
        return resp.status_code == 200
    except Exception:
        return False


@server.tool()
def create_task(
    title: str,
    description: str = "",
    due_date: str = "",
    priority: str = "P2_HIGH",
    category: str = "PERSONAL",
    is_important: bool = False
) -> str:
    """
    Creates a new persistent task in the executive task management system.
    Optionally syncs out to Zapier Tasks (Google Tasks, Todoist, Notion).
    """
    from app.services import task_service
    from app.models.task import TaskCreate, PriorityEnum, CategoryEnum

    clean_title = title.strip()
    if not clean_title:
        return json.dumps({"status": "ERROR", "error": "Task title cannot be empty."})

    # If marked important, escalate priority
    pri_enum = PriorityEnum.P1_URGENT if is_important else PriorityEnum(priority) if priority in PriorityEnum._value2member_map_ else PriorityEnum.P2_HIGH
    cat_enum = CategoryEnum(category) if category in CategoryEnum._value2member_map_ else CategoryEnum.PERSONAL

    task_payload = TaskCreate(
        title=clean_title,
        description=description.strip() or None,
        due_date=due_date.strip() or None,
        priority=pri_enum,
        category=cat_enum,
        is_confirmed=True
    )
    created = task_service.create_task(task_payload)

    # Sync to Zapier Tasks if available
    zapier_res = None
    if _is_zapier_tasks_available():
        zapier_res = _zapier_tasks_call("create_task", {
            "title": clean_title,
            "notes": description,
            "due": due_date,
            "priority": pri_enum.value
        })

    return json.dumps({
        "status": "SUCCESS",
        "task_id": created.id,
        "title": created.title,
        "priority": created.priority.value,
        "due_date": created.due_date,
        "zapier_synced": bool(zapier_res),
        "created_at": created.created_at
    })


@server.tool()
def mark_important_data(
    title: str,
    content: str,
    category: str = "IMPORTANT_FACT"
) -> str:
    """
    Marks and stores critical executive data, facts, or instructions.
    Saves to persistent AI memory and creates an urgent priority task.
    """
    from app.services import task_service, learning_service
    from app.models.task import TaskCreate, PriorityEnum, CategoryEnum

    clean_title = title.strip()
    clean_content = content.strip()

    # 1. Store in active learning memory
    mem = learning_service.add_or_update_memory(
        category="FACTUAL_KNOWLEDGE",
        key=f"important_{clean_title[:30].lower().replace(' ', '_')}",
        content=f"{clean_title}: {clean_content}",
        source="EXPLICIT_USER_COMMAND"
    )

    # 2. Record as P1_URGENT task so it appears in Daily Briefings
    task_payload = TaskCreate(
        title=f"⭐ IMPORTANT: {clean_title}",
        description=clean_content,
        priority=PriorityEnum.P1_URGENT,
        category=CategoryEnum.PERSONAL,
        is_confirmed=True
    )
    created = task_service.create_task(task_payload)

    # 3. Push to Zapier Tasks if active
    zapier_res = None
    if _is_zapier_tasks_available():
        zapier_res = _zapier_tasks_call("create_task", {
            "title": f"⭐ IMPORTANT: {clean_title}",
            "notes": clean_content,
            "priority": "P1_URGENT"
        })

    return json.dumps({
        "status": "SUCCESS",
        "mode": "SAVED_TO_MEMORY_AND_TASKS",
        "memory_id": mem.id,
        "task_id": created.id,
        "title": clean_title,
        "content": clean_content,
        "zapier_synced": bool(zapier_res)
    })


@server.tool()
def list_active_tasks(limit: int = 10) -> str:
    """
    Lists active pending tasks, ordered by priority.
    """
    from app.services import task_service
    tasks = task_service.list_tasks(status="PENDING")
    items = [
        {
            "id": t.id[:8],
            "title": t.title,
            "priority": t.priority.value,
            "due_date": t.due_date,
            "category": t.category.value
        }
        for t in tasks[:limit]
    ]
    return json.dumps({
        "status": "SUCCESS",
        "count": len(items),
        "tasks": items
    })


@server.tool()
def complete_task(task_id: str) -> str:
    """
    Marks a task as completed by ID or short prefix.
    """
    from app.services import task_service
    tasks = task_service.list_tasks()
    matched = next((t for t in tasks if t.id.startswith(task_id)), None)
    if not matched:
        return json.dumps({"status": "ERROR", "error": f"No task found matching '{task_id}'."})

    updated = task_service.complete_task(matched.id)
    return json.dumps({
        "status": "SUCCESS",
        "task_id": updated.id,
        "title": updated.title,
        "task_status": updated.status.value,
        "completed_at": updated.completed_at
    })


@server.tool()
def get_task_server_status() -> str:
    """
    Returns task manager and Zapier MCP connection health.
    """
    zapier_ok = _is_zapier_tasks_available()
    return json.dumps({
        "connected": True,
        "mode": "ZAPIER_TASKS_MCP" if zapier_ok else "LOCAL_SQLITE_PERSISTENCE",
        "zapier_tasks_active": zapier_ok,
        "zapier_tasks_id": ZAPIER_TASKS_MCP_ID,
        "checked_at": datetime.now(timezone.utc).isoformat()
    })


if __name__ == "__main__":
    server.run(transport="stdio")
