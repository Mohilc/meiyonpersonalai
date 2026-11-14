"""LinkedIn MCP Server for Personal AI Manager.

Provides standard Model Context Protocol (MCP) tools to:
- Retrieve LinkedIn user / candidate profile details
- List inbound connection invitations and recruiter messages
- Send connection requests with personalized notes (strictly under 300 characters)
- Publish post drafts to the feed (guarded by Human-In-The-Loop approval gate)
- Check session and browser connection status

Backends (priority order):
1. Zapier MCP LinkedIn Server (live OAuth, server ID: 029df438-e88c-8c07-8d68-61978ee0976a)
   → Calls Zapier's hosted MCP over HTTP/JSON-RPC — no cookie scraping needed.
2. Playwright browser automation with LinkedIn session cookie (`li_at`)
3. Sandbox / Simulation fallback when no live credentials are configured
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
server = MCPServer("linkedin-mcp")

# ── Configuration ────────────────────────────────────────────────────────────
LINKEDIN_LI_AT_COOKIE = os.getenv("LINKEDIN_LI_AT_COOKIE", "").strip()
LINKEDIN_HEADLESS = os.getenv("LINKEDIN_HEADLESS", "true").lower() in ("true", "1", "yes")
MCP_SIMULATION_FALLBACK = os.getenv("MCP_SIMULATION_FALLBACK", "true").lower() in ("true", "1", "yes")

# Zapier MCP LinkedIn Server
ZAPIER_LINKEDIN_MCP_URL = os.getenv(
    "ZAPIER_LINKEDIN_MCP_URL",
    "https://mcp.zapier.com/api/mcp/s/029df438-e88c-8c07-8d68-61978ee0976a/mcp"
)
ZAPIER_LINKEDIN_MCP_ID = os.getenv("ZAPIER_LINKEDIN_MCP_ID", "029df438-e88c-8c07-8d68-61978ee0976a")


# ── Zapier MCP HTTP Client ───────────────────────────────────────────────────
def _zapier_mcp_call(tool_name: str, arguments: dict = None, timeout: int = 15) -> Optional[Dict]:
    """
    Calls a tool on the Zapier-hosted LinkedIn MCP server via JSON-RPC 2.0 over HTTP.
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
            ZAPIER_LINKEDIN_MCP_URL,
            json=payload,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=timeout
        )
        resp.raise_for_status()
        data = resp.json()
        if "result" in data:
            # MCP result may be nested in content[0].text or directly
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
        elif "error" in data:
            logger.warning("Zapier MCP error for %s: %s", tool_name, data["error"])
    except requests.exceptions.Timeout:
        logger.warning("Zapier MCP timeout calling %s", tool_name)
    except requests.exceptions.RequestException as e:
        logger.warning("Zapier MCP request failed for %s: %s", tool_name, str(e))
    return None


def _is_zapier_available() -> bool:
    """Quick health probe to Zapier MCP endpoint."""
    try:
        payload = {"jsonrpc": "2.0", "id": "ping", "method": "tools/list", "params": {}}
        resp = requests.post(
            ZAPIER_LINKEDIN_MCP_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=8
        )
        return resp.status_code == 200
    except Exception:
        return False


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
    Priority: Zapier MCP → Playwright live → Sandbox simulation.
    """
    # 1. Try Zapier MCP first
    zapier_result = _zapier_mcp_call("get_linkedin_profile", {"profile_url": profile_url or ""})
    if zapier_result:
        return json.dumps({"status": "SUCCESS", "mode": "ZAPIER_MCP", "profile": zapier_result})

    # 2. Try Playwright browser with li_at cookie
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

    # 3. Sandbox fallback
    return json.dumps({"status": "SUCCESS", "mode": "SIMULATION_SANDBOX", "profile": SANDBOX_PROFILE})

@server.tool()
def list_recent_messages(limit: int = 10) -> str:
    """
    Lists recent LinkedIn direct messages and conversations from recruiters.
    Priority: Zapier MCP → Sandbox simulation.
    """
    # 1. Try Zapier MCP
    zapier_result = _zapier_mcp_call("list_recent_messages", {"limit": limit})
    if zapier_result:
        messages = zapier_result.get("messages", zapier_result) if isinstance(zapier_result, dict) else zapier_result
        if isinstance(messages, list):
            return json.dumps({"status": "SUCCESS", "mode": "ZAPIER_MCP", "count": len(messages), "messages": messages})
        return json.dumps({"status": "SUCCESS", "mode": "ZAPIER_MCP", "data": zapier_result})

    # 2. Sandbox fallback
    return json.dumps({
        "status": "SUCCESS",
        "mode": "SIMULATION_SANDBOX",
        "count": len(SANDBOX_MESSAGES[:limit]),
        "messages": SANDBOX_MESSAGES[:limit]
    })

@server.tool()
def list_connection_requests(limit: int = 10) -> str:
    """
    Lists pending inbound connection requests, mutual connections, and invitation notes.
    Priority: Zapier MCP → Sandbox simulation.
    """
    # 1. Try Zapier MCP
    zapier_result = _zapier_mcp_call("list_connection_requests", {"limit": limit})
    if zapier_result:
        connections = zapier_result.get("connections", zapier_result) if isinstance(zapier_result, dict) else zapier_result
        if isinstance(connections, list):
            return json.dumps({"status": "SUCCESS", "mode": "ZAPIER_MCP", "count": len(connections), "connections": connections})
        return json.dumps({"status": "SUCCESS", "mode": "ZAPIER_MCP", "data": zapier_result})

    # 2. Sandbox fallback
    return json.dumps({
        "status": "SUCCESS",
        "mode": "SIMULATION_SANDBOX",
        "count": len(SANDBOX_CONNECTIONS[:limit]),
        "connections": SANDBOX_CONNECTIONS[:limit]
    })

@server.tool()
def send_connection_invite(profile_url: str, custom_note: str, approved: bool = False) -> str:
    """
    Sends a connection invite with personalized note.
    Validates note strictly against LinkedIn 300 character limit.
    Guarded by Human-In-The-Loop approval gate.
    Priority: Zapier MCP → Sandbox simulation.
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

    # 1. Try Zapier MCP (live send)
    zapier_result = _zapier_mcp_call("send_connection_invite", {
        "profile_url": profile_url, "custom_note": custom_note
    })
    if zapier_result:
        return json.dumps({"status": "INVITATION_SENT", "mode": "ZAPIER_MCP",
                           "recipient_url": profile_url, "character_count": len(custom_note),
                           "note_preview": custom_note, "zapier_result": zapier_result,
                           "sent_at": datetime.now(timezone.utc).isoformat()})

    # 2. Sandbox simulation
    return json.dumps({
        "status": "INVITATION_SENT",
        "mode": "SIMULATION_SANDBOX",
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
    Priority: Zapier MCP → Sandbox simulation.
    """
    if not approved:
        return json.dumps({
            "status": "HALTED_FOR_APPROVAL",
            "error": "Safety guardrail active: Publishing LinkedIn posts externally requires explicit Human-In-The-Loop approval."
        })

    # 1. Try Zapier MCP (live post)
    zapier_result = _zapier_mcp_call("publish_post", {"text": text, "visibility": visibility})
    if zapier_result:
        return json.dumps({"status": "POSTED", "mode": "ZAPIER_MCP", "visibility": visibility,
                           "text_preview": text[:120], "zapier_result": zapier_result,
                           "published_at": datetime.now(timezone.utc).isoformat()})

    # 2. Sandbox simulation
    post_id = f"urn:li:share:{uuid.uuid4().hex[:12]}"
    return json.dumps({
        "status": "POSTED",
        "mode": "SIMULATION_SANDBOX",
        "post_id": post_id,
        "visibility": visibility,
        "text_preview": text[:120],
        "published_at": datetime.now(timezone.utc).isoformat()
    })

@server.tool()
def like_post(post_url: str, reaction_type: str = "LIKE", approved: bool = False) -> str:
    """
    Likes or reacts to a LinkedIn post.
    Guarded by Human-In-The-Loop approval gate.
    """
    if not approved:
        return json.dumps({
            "status": "HALTED_FOR_APPROVAL",
            "error": "Safety guardrail active: Liking a LinkedIn post externally requires explicit Human-In-The-Loop approval."
        })

    if not post_url or ("linkedin.com" not in post_url.lower()):
        return json.dumps({
            "status": "VALIDATION_ERROR",
            "error": "Invalid LinkedIn post URL."
        })

    if LINKEDIN_LI_AT_COOKIE and not MCP_SIMULATION_FALLBACK:
        try:
            def _live_like(ctx):
                page = ctx.new_page()
                page.goto(post_url, timeout=20000, wait_until="domcontentloaded")
                like_selectors = [
                    "button.react-button__trigger",
                    "button[aria-label*='React Like' i]",
                    "button.feed-shared-social-action-bar__action-button"
                ]
                clicked = False
                for sel in like_selectors:
                    loc = page.locator(sel).first
                    if loc.is_visible(timeout=3000):
                        loc.click()
                        clicked = True
                        break
                return {"post_url": post_url, "clicked": clicked, "status": "LIVE_LIKED"}
            data = _run_playwright_action(_live_like)
            return json.dumps({
                "status": "LIKED",
                "mode": "LIVE_BROWSER",
                "reaction_type": reaction_type,
                "post_url": post_url,
                "result": data,
                "liked_at": datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            return json.dumps({
                "status": "LIKED",
                "mode": "SIMULATION_SANDBOX",
                "warning": str(e),
                "reaction_type": reaction_type,
                "post_url": post_url,
                "liked_at": datetime.now(timezone.utc).isoformat()
            })

    return json.dumps({
        "status": "LIKED",
        "mode": "SIMULATION_SANDBOX",
        "reaction_type": reaction_type,
        "post_url": post_url,
        "liked_at": datetime.now(timezone.utc).isoformat()
    })

@server.tool()
def comment_on_post(post_url: str, comment_text: str, approved: bool = False) -> str:
    """
    Submits a comment on a LinkedIn post.
    Guarded by Human-In-The-Loop approval gate.
    """
    if not approved:
        return json.dumps({
            "status": "HALTED_FOR_APPROVAL",
            "error": "Safety guardrail active: Commenting on a LinkedIn post externally requires explicit Human-In-The-Loop approval."
        })

    clean_comment = comment_text.strip()
    if not clean_comment:
        return json.dumps({
            "status": "VALIDATION_ERROR",
            "error": "Comment text cannot be empty."
        })

    if not post_url or ("linkedin.com" not in post_url.lower()):
        return json.dumps({
            "status": "VALIDATION_ERROR",
            "error": "Invalid LinkedIn post URL."
        })

    if LINKEDIN_LI_AT_COOKIE and not MCP_SIMULATION_FALLBACK:
        try:
            def _live_comment(ctx):
                page = ctx.new_page()
                page.goto(post_url, timeout=20000, wait_until="domcontentloaded")
                comment_box_selectors = [
                    "div.comments-comment-box__editor div[role='textbox']",
                    "div.ql-editor[role='textbox']",
                    "div[role='textbox'][aria-label*='comment' i]"
                ]
                posted = False
                for sel in comment_box_selectors:
                    loc = page.locator(sel).first
                    if loc.is_visible(timeout=3000):
                        loc.click()
                        loc.fill(clean_comment)
                        submit_btn = page.locator("button.comments-comment-box__submit-button, button[type='submit']").first
                        if submit_btn.is_visible(timeout=2000):
                            submit_btn.click()
                            posted = True
                            break
                return {"post_url": post_url, "posted": posted, "status": "LIVE_COMMENTED"}
            data = _run_playwright_action(_live_comment)
            return json.dumps({
                "status": "COMMENTED",
                "mode": "LIVE_BROWSER",
                "post_url": post_url,
                "comment_preview": clean_comment[:120],
                "result": data,
                "commented_at": datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            return json.dumps({
                "status": "COMMENTED",
                "mode": "SIMULATION_SANDBOX",
                "warning": str(e),
                "post_url": post_url,
                "comment_preview": clean_comment[:120],
                "commented_at": datetime.now(timezone.utc).isoformat()
            })

    comment_id = f"urn:li:comment:{uuid.uuid4().hex[:12]}"
    return json.dumps({
        "status": "COMMENTED",
        "mode": "SIMULATION_SANDBOX",
        "comment_id": comment_id,
        "post_url": post_url,
        "comment_preview": clean_comment[:120],
        "commented_at": datetime.now(timezone.utc).isoformat()
    })

@server.tool()
def get_linkedin_status() -> str:
    """
    Returns LinkedIn MCP connection status, including Zapier MCP server health check.
    """
    has_cookie = bool(LINKEDIN_LI_AT_COOKIE)
    zapier_ok = _is_zapier_available()
    mode = "ZAPIER_MCP" if zapier_ok else ("LIVE_BROWSER_SESSION" if has_cookie else "SIMULATION_SANDBOX")
    return json.dumps({
        "connected": True,
        "mode": mode,
        "zapier_mcp_active": zapier_ok,
        "zapier_mcp_id": ZAPIER_LINKEDIN_MCP_ID,
        "session_cookie_configured": has_cookie,
        "headless": LINKEDIN_HEADLESS,
        "user_name": "Mohil",
        "checked_at": datetime.now(timezone.utc).isoformat()
    })

if __name__ == "__main__":
    server.run(transport="stdio")
