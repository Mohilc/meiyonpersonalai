"""Unit tests for SerpApi Google Search and Real-Time Web Intelligence."""
import pytest
from unittest.mock import patch, MagicMock

from app.services import search_service, messaging_bot_service, learning_service


def test_is_search_available():
    """Validates availability flag matches configured API key."""
    assert search_service.is_search_available() is True


def test_search_and_summarize_mocked():
    """Tests markdown formatting of search results with answer box and knowledge graph."""
    mock_data = {
        "answer_box": {"answer": "Austin, Texas is a vibrant tech hub."},
        "knowledge_graph": {
            "title": "Coffee",
            "description": "Coffee is a beverage prepared from roasted coffee beans."
        },
        "organic_results": [
            {
                "title": "Best Coffee in Austin",
                "link": "https://example.com/coffee-austin",
                "snippet": "Discover the top roasted coffee in Austin."
            },
            {
                "title": "Coffee Culture",
                "link": "https://example.com/culture",
                "snippet": "History and techniques of specialty coffee."
            }
        ]
    }

    with patch("app.services.search_service.search_google", return_value=mock_data):
        summary = search_service.search_and_summarize("Coffee in Austin", max_results=2)
        assert "Google Search Results for:" in summary
        assert "Direct Answer" in summary
        assert "Coffee:" in summary
        assert "Best Coffee in Austin" in summary
        assert "https://example.com/coffee-austin" in summary


def test_search_jobs_online():
    """Validates structured job search extraction."""
    mock_data = {
        "organic_results": [
            {
                "title": "Computer Vision & AI Intern",
                "link": "https://careers.example.com/ai-intern",
                "snippet": "Exciting internship working on YOLOv8 edge models.",
                "displayed_link": "careers.example.com"
            }
        ]
    }
    with patch("app.services.search_service.search_google", return_value=mock_data):
        jobs = search_service.search_jobs_online("Edge AI Intern", location="India", max_results=1)
        assert len(jobs) == 1
        assert jobs[0]["title"] == "Computer Vision & AI Intern"
        assert "careers.example.com" in jobs[0]["link"]


def test_verify_company_reputation():
    """Tests scam detection heuristics on search snippets."""
    mock_scam_data = {
        "organic_results": [
            {
                "title": "Fake Tech Corp Scam Complaints",
                "link": "https://complaints.org/fake-tech",
                "snippet": "Warning: Fake Tech Corp is a fraudulent job offer scam charging training fee."
            }
        ]
    }
    with patch("app.services.search_service.search_google", return_value=mock_scam_data):
        rep = search_service.verify_company_reputation("Fake Tech Corp")
        assert rep["is_safe"] is False
        assert len(rep["suspicious_hits"]) == 1

    mock_clean_data = {
        "organic_results": [
            {
                "title": "Tech Innovations Official Careers",
                "link": "https://techinnovations.com/careers",
                "snippet": "Explore verified engineering opportunities at Tech Innovations."
            }
        ]
    }
    with patch("app.services.search_service.search_google", return_value=mock_clean_data):
        clean_rep = search_service.verify_company_reputation("Tech Innovations")
        assert clean_rep["is_safe"] is True


def test_search_and_learn_topic():
    """Tests researching a topic and persisting to self-learning memory bank."""
    mock_data = {
        "organic_results": [
            {
                "title": "Edge TPU Optimization Guide",
                "link": "https://edgetpu.example.com",
                "snippet": "Optimizing neural networks for sub-10ms inference."
            }
        ]
    }
    with patch("app.services.search_service.search_google", return_value=mock_data):
        res = search_service.search_and_learn_topic("Edge TPU Optimization")
        assert "Learned & Saved to Memory" in res

        mem = learning_service.get_memory_by_key("web_edge_tpu_optimization")
        assert mem is not None
        assert "Edge TPU" in mem.content


def test_messaging_bot_search_commands():
    """Tests /search and /learnweb commands in messaging bot."""
    with patch("app.services.search_service.search_and_summarize", return_value="Mocked Google Results"):
        res = messaging_bot_service.handle_incoming_text("test_user", "telegram", "/search autonomous drones")
        assert res == "Mocked Google Results"

    with patch("app.services.search_service.search_and_learn_topic", return_value="Mocked Learned Topic"):
        res = messaging_bot_service.handle_incoming_text("test_user", "telegram", "/learnweb drone swarm telemetry")
        assert res == "Mocked Learned Topic"

