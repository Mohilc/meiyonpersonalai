"""Unit tests for the Self-Learning Persona and Adaptive Memory Engine."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db
from app.services import learning_service, messaging_bot_service
from app.models.learning import MemoryCategoryEnum, MemorySourceEnum, LearnedMemoryCreate

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_baseline_memories_seeded():
    """Verify that init_db seeds baseline human-friendly tone and persona rules."""
    memories = learning_service.list_active_memories()
    keys = [m.key for m in memories]
    assert "human_friendly_tone" in keys
    assert "identity_and_passion" in keys
    assert "two_way_dialogue" in keys

def test_add_and_update_memory():
    """Verify adding, updating, and deactivating custom memory entries."""
    created = learning_service.add_or_update_memory(
        category=MemoryCategoryEnum.COMMUNICATION_STYLE.value,
        key="test_greeting_style",
        content="Always open with 'Hey Mohil, hope building drones is going awesome today!'",
        source=MemorySourceEnum.EXPLICIT_USER_COMMAND.value,
        confidence_score=1.0
    )
    assert created.key == "test_greeting_style"
    assert "drones" in created.content

    # Retrieve memory by key
    retrieved = learning_service.get_memory_by_key("test_greeting_style")
    assert retrieved is not None
    assert retrieved.is_active is True

    # Deactivate memory
    deactivated = learning_service.deactivate_memory("test_greeting_style")
    assert deactivated is True
    assert learning_service.get_memory_by_key("test_greeting_style") is None

def test_extract_learnings_from_user_text():
    """Verify conversational text triggers self-learning extractions."""
    # Explicit remember trigger
    mem1 = learning_service.extract_learnings_from_user_text("Remember that my main lab drone project uses YOLOv8 for obstacle detection")
    assert mem1 is not None
    assert mem1["type"] == "EXPLICIT_MEMORY"
    assert "YOLOv8" in mem1["content"]
    assert "Memory Learned" in mem1["acknowledgment"]

    # Conversational tone / style adaptation trigger
    mem2 = learning_service.extract_learnings_from_user_text("Please be more friendly and casual when speaking to me")
    assert mem2 is not None
    assert mem2["type"] == "TONE_ADAPTATION"
    assert "warm_and_casual" in mem2["key"]
    assert "Style Adapted" in mem2["acknowledgment"]

    # Non-learning regular query returns None
    mem3 = learning_service.extract_learnings_from_user_text("What is 2 + 2?")
    assert mem3 is None

def test_compile_learned_prompt_instructions():
    """Verify that compiled prompt context organizes instructions into actionable persona sections."""
    learning_service.add_or_update_memory(
        category=MemoryCategoryEnum.PREFERENCE.value,
        key="test_brevity_pref",
        content="Keep bullet points short and punchy.",
        source=MemorySourceEnum.EXPLICIT_USER_COMMAND.value
    )
    context = learning_service.compile_learned_prompt_instructions()
    assert "=== SELF-LEARNED ADAPTIVE USER PREFERENCES & PERSONA ===" in context
    assert "Keep bullet points short and punchy." in context

def test_learning_api_endpoints():
    """Verify REST API routes for memories, feedback, and prompt context."""
    # Create memory via API
    resp = client.post("/api/learning/memories", json={
        "category": "FACTUAL_KNOWLEDGE",
        "key": "api_test_project",
        "content": "Building autonomous delivery copter.",
        "confidence_score": 0.95
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["key"] == "api_test_project"

    # List active memories
    resp_list = client.get("/api/learning/memories")
    assert resp_list.status_code == 200
    items = resp_list.json()
    assert any(item["key"] == "api_test_project" for item in items)

    # Prompt context endpoint
    resp_prompt = client.get("/api/learning/prompt-context")
    assert resp_prompt.status_code == 200
    assert "autonomous delivery copter" in resp_prompt.json()["prompt_instructions"]

    # Submit feedback endpoint
    resp_fb = client.post("/api/learning/feedback", json={
        "user_feedback": "Great warm response, loved the enthusiasm!",
        "desired_tone": "Warm and excited",
        "rating": 5
    })
    assert resp_fb.status_code == 200
    assert "Feedback recorded" in resp_fb.json()["message"]

def test_bot_messaging_learning_commands():
    """Verify Telegram commands /remember, /memory, and /forget."""
    # /remember command
    msg1 = messaging_bot_service.handle_incoming_text(
        sender_id="test_user_telegram",
        platform="telegram",
        text="/remember I love developing PX4 autopilot firmware"
    )
    assert "Learned & Saved to Memory" in msg1
    assert "PX4 autopilot firmware" in msg1

    # /memory command (inspect memories)
    msg2 = messaging_bot_service.handle_incoming_text(
        sender_id="test_user_telegram",
        platform="telegram",
        text="/memory"
    )
    assert "LEARNED MEMORY & ADAPTIVE PERSONA" in msg2

    # /forget command
    msg3 = messaging_bot_service.handle_incoming_text(
        sender_id="test_user_telegram",
        platform="telegram",
        text="/forget PX4 autopilot firmware"
    )
    assert "Memory Removed" in msg3 or "forgotten" in msg3
