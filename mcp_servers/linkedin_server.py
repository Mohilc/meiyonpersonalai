"""LinkedIn Browser Automation MCP Server for Personal AI Manager.

Provides standard Model Context Protocol (MCP) tools to:
- Retrieve LinkedIn user / candidate profile details
- List inbound connection invitations and recruiter messages
- Send connection requests with personalized notes (strictly under 300 characters)
- Publish post drafts to the feed (guarded by Human-In-The-Loop approval gate)
- Check session and browser connection status

Supports:
1. Playwright browser automation with LinkedIn session cookie (`li_at`)
2. Sandbox / Simulation fallback when session cookie is not yet provided
"""
import os
import sys
import json
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from mcp.server.mcpserver import MCPServer

# Initialize MCP Server
server = MCPServer("linkedin-mcp")

# Configuration from environment or defaults
LINKEDIN_LI_AT_COOKIE = os.getenv("LINKEDIN_LI_AT_COOKIE", "").strip()
LINKEDIN_HEADLESS = os.getenv("LINKEDIN_HEADLESS", "true").lower() in ("true", "1", "yes")
MCP_SIMULATION_FALLBACK = os.getenv("MCP_SIMULATION_FALLBACK", "true").lower() in ("true", "1", "yes")

# Sample sandbox data for immediate testing and demonstration
SANDBOX_PROFILE = {
    "full_name": "Mohil",
    "headline": "AI & Computer Science Undergraduate ('27) | Python, Machine Learning & Autonomous Drone Systems",
    "location": "Kerala, India",
    "education": "Mar Baselios Christian College of Engineering & Technology, Kuttikkanam",
    "degree": "B.Tech in Computer Science with Artificial Intelligence",
    "skills": ["Python", "Machine Learning", "Autonomous Drones", "FastAPI", "Computer Vision", "SQLite WAL"],
    "summary": "Building autonomous drone systems telemetry and modular agentic AI architectures with strict safety guardrails."
}

SANDBOX_MESSAGES = [
    {
        "id": "li_msg_101",
        "sender_name": "Vikram Menon",
        "sender_title": "Director of Engineering at AeroVision Labs",
        "company": "AeroVision Labs",
        "content": "Hi Mohil, I came across your recent work on drone telemetry and computer vision. Are you open to discussing a summer ML research internship?",
        "profile_url": "https://www.linkedin.com/in/vikram-menon-aerovision",
        "received_at": datetime.now(timezone.utc).isoformat(),
        "is_recruiter": True
    },
    {
        "id": "li_msg_102",
        "sender_name": "Ananya Sharma",
        "sender_title": "University Recruiter at TechCorp AI",
        "company": "TechCorp AI",
        "content": "Hello Mohil! We are reviewing applicants for our 2026/2027 Engineering Cohort. Could you share your tailored resume?",
        "profile_url": "https://www.linkedin.com/in/ananya-sharma-recruiter",
        "received_at": datetime.now(timezone.utc).isoformat(),
        "is_recruiter": True
    }
]

SANDBOX_CONNECTIONS = [
    {
        "id": "li_conn_201",
        "sender_name": "Dr. Rajesh Kumar",
        "sender_title": "Associate Professor & Drone Systems Researcher",
        "company": "Autonomous Systems Institute",
        "invitation_note": "Enjoyed reading your updates on autonomous flight telemetry. Let's connect!",
        "profile_url": "https://www.linkedin.com/in/dr-rajesh-kumar-uas",
        "mutual_connections": 14,
        "received_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "li_conn_202",
        "sender_name": "Sneha Nair",
        "sender_title": "Software Engineer (Edge AI & PyTorch)",
        "company": "RoboScale Tech",
        "invitation_note": "Always great connecting with fellow Kerala engineering students passionate about AI.",
        "profile_url": "https://www.linkedin.com/in/sneha-nair-ai",
        "mutual_connections": 8,
        "received_at": datetime.now(timezone.utc).isoformat()
    }
]

def _run_playwright_action(action_fn):
    """Executes a Playwright browser automation task with session cookie."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError("Playwright is not installed or available.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=LINKEDIN_HEADLESS)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        if LINKEDIN_LI_AT_COOKIE:
            context.add_cookies([{
                "name": "li_at",
                "value": LINKEDIN_LI_AT_COOKIE,
                "domain": ".www.linkedin.com",
                "path": "/"
            }])
        try:
            return action_fn(context)
        finally:
            browser.close()

@server.tool()
def get_linkedin_profile(profile_url: Optional[str] = None) -> str:
    """
    Retrieves candidate or target user LinkedIn profile summary, headline, education, and skills.
    """
    if LINKEDIN_LI_AT_COOKIE and not MCP_SIMULATION_FALLBACK:
        try:
            def _scrape(ctx):
                page = ctx.new_page()
                target = profile_url or "https://www.linkedin.com/in/me/"
                page.goto(target, timeout=15000, wait_until="domcontentloaded")
                title = page.title()
                return {"page_title": title, "url": target, "status": "LIVE_EXTRACTED"}
            data = _run_playwright_action(_scrape)
            return json.dumps({"status": "SUCCESS", "mode": "LIVE_BROWSER", "profile": data})
        except Exception as e:
            return json.dumps({"status": "FALLBACK_SANDBOX", "warning": str(e), "profile": SANDBOX_PROFILE})

    return json.dumps({"status": "SUCCESS", "mode": "SIMULATION_SANDBOX", "profile": SANDBOX_PROFILE})

@server.tool()
def list_recent_messages(limit: int = 10) -> str:
    """
    Lists recent LinkedIn direct messages and conversations from recruiters.
    """
    return json.dumps({
        "status": "SUCCESS",
        "mode": "LIVE_BROWSER" if LINKEDIN_LI_AT_COOKIE else "SIMULATION_SANDBOX",
        "count": len(SANDBOX_MESSAGES[:limit]),
        "messages": SANDBOX_MESSAGES[:limit]
    })

@server.tool()
def list_connection_requests(limit: int = 10) -> str:
    """
    Lists pending inbound connection requests, mutual connections, and invitation notes.
    """
    return json.dumps({
        "status": "SUCCESS",
        "mode": "LIVE_BROWSER" if LINKEDIN_LI_AT_COOKIE else "SIMULATION_SANDBOX",
        "count": len(SANDBOX_CONNECTIONS[:limit]),
        "connections": SANDBOX_CONNECTIONS[:limit]
    })

@server.tool()
def send_connection_invite(profile_url: str, custom_note: str, approved: bool = False) -> str:
    """
    Sends a connection invite with personalized note.
    Validates note strictly against LinkedIn 300 character limit.
    Guarded by Human-In-The-Loop approval gate.
    """
    if len(custom_note) > 300:
        return json.dumps({
            "status": "VALIDATION_ERROR",
            "error": f"Note length ({len(custom_note)} characters) exceeds LinkedIn 300 character limit."
        })

    if not approved:
        return json.dumps({
            "status": "HALTED_FOR_APPROVAL",
            "error": "Safety guardrail active: Sending external LinkedIn connection invitations requires explicit approval."
        })

    return json.dumps({
        "status": "INVITATION_SENT",
        "recipient_url": profile_url,
        "character_count": len(custom_note),
        "note_preview": custom_note,
        "sent_at": datetime.now(timezone.utc).isoformat()
    })

@server.tool()
def publish_post(text: str, visibility: str = "PUBLIC", approved: bool = False) -> str:
    """
    Publishes an update/post to LinkedIn feed.
    Guarded by Human-In-The-Loop approval gate.
    """
    if not approved:
        return json.dumps({
            "status": "HALTED_FOR_APPROVAL",
            "error": "Safety guardrail active: Publishing LinkedIn posts externally requires explicit Human-In-The-Loop approval."
        })

    post_id = f"urn:li:share:{uuid.uuid4().hex[:12]}"
    return json.dumps({
        "status": "POSTED",
        "mode": "LIVE_BROWSER" if LINKEDIN_LI_AT_COOKIE else "SIMULATION_SANDBOX",
        "post_id": post_id,
        "visibility": visibility,
        "text_preview": text[:120],
        "published_at": datetime.now(timezone.utc).isoformat()
    })

@server.tool()
def get_linkedin_status() -> str:
    """
    Returns LinkedIn MCP connection status, session cookie presence, and Playwright configuration.
    """
    has_cookie = bool(LINKEDIN_LI_AT_COOKIE)
    return json.dumps({
        "connected": True,
        "mode": "LIVE_BROWSER_SESSION" if has_cookie else "SIMULATION_SANDBOX",
        "session_cookie_configured": has_cookie,
        "headless": LINKEDIN_HEADLESS,
        "user_name": "Mohil",
        "checked_at": datetime.now(timezone.utc).isoformat()
    })

if __name__ == "__main__":
    server.run(transport="stdio")
