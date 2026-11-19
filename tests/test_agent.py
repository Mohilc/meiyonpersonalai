"""Tests for LangChain Agentic AI Service and Tool Calling."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services import agent_service

client = TestClient(app)


def test_agent_tools_definitions():
    """Verifies that all 12 LangChain agent tools are properly defined with schemas."""
    assert agent_service.LANGCHAIN_AVAILABLE is True
    tools = agent_service.ALL_AGENT_TOOLS
    assert len(tools) >= 12

    tool_names = [t.name for t in tools]
    expected_tools = [
        "get_college_attendance",
        "mark_subject_attendance",
        "get_pending_assignments",
        "add_college_assignment",
        "list_scheduled_tasks",
        "add_task_commitment",
        "complete_task_commitment",
        "search_google_web",
        "get_recent_inbox_emails",
        "get_executive_briefing",
        "remember_user_rule",
        "get_learned_memories"
    ]
    for expected in expected_tools:
        assert expected in tool_names, f"Missing tool: {expected}"


def test_agent_tool_attendance_execution():
    """Tests execution of attendance retrieval and mark attendance tools."""
    att_res = agent_service.get_college_attendance.invoke({})
    assert "Overall College Attendance" in att_res or "classes" in att_res.lower()

    mark_res = agent_service.mark_subject_attendance.invoke({"subject": "AI", "status": "PRESENT", "notes": "Test class"})
    assert "Recorded AI as PRESENT" in mark_res


def test_agent_tool_assignments_execution():
    """Tests execution of assignment tools."""
    add_res = agent_service.add_college_assignment.invoke({
        "subject": "Deep Learning",
        "title": "Transformer Architecture Analysis",
        "due_date": "2026-12-01"
    })
    assert "Added assignment" in add_res
    assert "Transformer Architecture Analysis" in add_res

    list_res = agent_service.get_pending_assignments.invoke({})
    assert "Transformer Architecture Analysis" in list_res or "Found" in list_res


def test_agent_tool_tasks_execution():
    """Tests execution of task commitment tools."""
    add_res = agent_service.add_task_commitment.invoke({
        "title": "Calibrate drone IMU sensor",
        "priority": "P2_HIGH",
        "due_date": "2026-11-25"
    })
    assert "Created task" in add_res
    assert "Calibrate drone IMU sensor" in add_res

    list_res = agent_service.list_scheduled_tasks.invoke({})
    assert "Calibrate drone IMU sensor" in list_res


def test_agent_tool_memory_execution():
    """Tests execution of self-learning memory tools."""
    rem_res = agent_service.remember_user_rule.invoke({
        "preference_or_rule": "Prefer bulleted answers for study plans"
    })
    assert "Learned and saved to memory" in rem_res

    mems_res = agent_service.get_learned_memories.invoke({})
    assert "bulleted answers" in mems_res or "Found" in mems_res


def test_agent_tool_briefing_execution():
    """Tests execution of executive briefing tool."""
    brief_res = agent_service.get_executive_briefing.invoke({})
    assert "Daily Executive Briefing" in brief_res
    assert "Overdue Tasks" in brief_res


def test_agent_api_endpoint():
    """Tests the /api/communication/agent/chat REST endpoint."""
    with patch("app.services.agent_service.run_agent") as mock_run:
        mock_run.return_value = "Your attendance in AI is 82.5% and all tasks are on schedule."
        response = client.post(
            "/api/communication/agent/chat",
            json={"message": "How am I doing in AI?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["agent_available"] is True
        assert data["tools_count"] >= 12
        assert "82.5%" in data["reply"]
