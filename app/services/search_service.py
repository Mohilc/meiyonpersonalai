"""Google Search and Real-Time Web Intelligence Service via SerpApi.

Provides live web search, company reputation verification, online job discovery,
and automatic grounding for Meiyon's AI reasoning and self-learning memory.
"""
import logging
from typing import Dict, Any, List, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SERPAPI_BASE_URL = "https://serpapi.com/search.json"


def is_search_available() -> bool:
    """Checks whether a valid SerpApi API key is configured."""
    return bool(settings.SERPAPI_API_KEY and settings.SERPAPI_API_KEY.strip())


def search_google(
    query: str,
    num: int = 5,
    location: Optional[str] = None,
    gl: Optional[str] = None,
    hl: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes a Google Search using SerpApi.
    Supports official `serpapi` library with transparent `httpx` fallback.
    """
    if not is_search_available():
        logger.warning("SerpApi API key not configured. Returning empty search results.")
        return {"error": "SerpApi API key not configured", "organic_results": []}

    api_key = settings.SERPAPI_API_KEY.strip()
    loc = location or getattr(settings, "SERPAPI_DEFAULT_LOCATION", "India")
    gl_code = gl or getattr(settings, "SERPAPI_DEFAULT_GL", "in")
    hl_code = hl or getattr(settings, "SERPAPI_DEFAULT_HL", "en")

    # 1. Try official serpapi client
    try:
        import serpapi
        client = serpapi.Client(api_key=api_key)
        params = {
            "engine": "google",
            "q": query,
            "num": num,
            "hl": hl_code,
            "gl": gl_code
        }
        if loc:
            params["location"] = loc
        results = client.search(params)
        return dict(results)
    except Exception as e:
        logger.debug("serpapi client search failed or not installed (%s), using direct HTTP fallback", str(e))

    # 2. Resilient direct HTTP fallback
    try:
        params = {
            "engine": "google",
            "q": query,
            "num": num,
            "hl": hl_code,
            "gl": gl_code,
            "api_key": api_key
        }
        if loc:
            params["location"] = loc
        with httpx.Client(timeout=10.0) as http_client:
            resp = http_client.get(SERPAPI_BASE_URL, params=params)
            if resp.status_code == 200:
                return resp.json()
            logger.error("SerpApi HTTP request failed: %d - %s", resp.status_code, resp.text)
            return {"error": f"HTTP {resp.status_code}", "organic_results": []}
    except Exception as e:
        logger.error("SerpApi query failed: %s", str(e))
        return {"error": str(e), "organic_results": []}


def search_and_summarize(query: str, max_results: int = 4) -> str:
    """
    Performs a Google Search and returns a concise, formatted markdown briefing.
    Includes Answer Box / Knowledge Graph when available.
    """
    data = search_google(query=query, num=max_results)
    if "error" in data and not data.get("organic_results"):
        return f"🔍 *Google Search:* Could not retrieve results for '{query}' ({data.get('error')})."

    lines: List[str] = [f"🔍 *Google Search Results for:* `{query}`\n"]

    # 1. Answer Box / Direct Answer
    answer_box = data.get("answer_box", {})
    if answer_box:
        ans = answer_box.get("answer") or answer_box.get("snippet") or answer_box.get("result")
        if ans:
            lines.append(f"💡 *Direct Answer:* {ans}\n")

    # 2. Knowledge Graph
    kg = data.get("knowledge_graph", {})
    if kg:
        kg_title = kg.get("title")
        kg_desc = kg.get("description")
        if kg_title and kg_desc:
            lines.append(f"📌 *{kg_title}:* {kg_desc}\n")

    # 3. Organic Results
    organic = data.get("organic_results", [])
    if not organic:
        lines.append("No organic results found.")
        return "\n".join(lines)

    for i, res in enumerate(organic[:max_results], 1):
        title = res.get("title", "Untitled")
        link = res.get("link", "")
        snippet = res.get("snippet", "").replace("\n", " ").strip()
        lines.append(f"*{i}. [{title}]({link})*")
        if snippet:
            lines.append(f"   _{snippet}_")

    return "\n".join(lines)


def search_jobs_online(role: str, location: str = "India", max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Searches Google for real-time job and internship postings.
    Returns structured listings with title, company, link, and snippet.
    """
    query = f"{role} jobs internships {location}"
    data = search_google(query=query, num=max_results, location=location)
    organic = data.get("organic_results", [])
    jobs = []
    for res in organic[:max_results]:
        jobs.append({
            "title": res.get("title", "Role"),
            "link": res.get("link", ""),
            "snippet": res.get("snippet", ""),
            "source": res.get("displayed_link", "Google Search")
        })
    return jobs


def verify_company_reputation(company_name: str) -> Dict[str, Any]:
    """
    Conducts live web reconnaissance on a company name to detect scam reports,
    negative reviews, and official presence.
    """
    if not company_name or len(company_name.strip()) < 2:
        return {"risk": "UNKNOWN", "details": "Company name too short to evaluate."}

    query = f"{company_name} company reviews scam fraud complaints"
    data = search_google(query=query, num=4)
    organic = data.get("organic_results", [])

    scam_keywords = ["scam", "fraud", "fake offer", "stolen identity", "lawsuit", "complaint", "warning"]
    suspicious_hits = []

    for res in organic:
        snippet = res.get("snippet", "").lower()
        title = res.get("title", "").lower()
        matched = [k for k in scam_keywords if k in snippet or k in title]
        if matched:
            suspicious_hits.append({
                "source": res.get("title"),
                "link": res.get("link"),
                "flags": matched
            })

    return {
        "company": company_name,
        "is_safe": len(suspicious_hits) == 0,
        "suspicious_hits": suspicious_hits,
        "top_links": [r.get("link") for r in organic[:3] if r.get("link")]
    }


def search_and_learn_topic(topic: str) -> str:
    """
    Searches Google for key facts about a topic and updates Meiyon's
    self-learning memory bank with the synthesized findings.
    """
    from app.services import learning_service

    summary = search_and_summarize(topic, max_results=3)
    slug = "".join(c if c.isalnum() else "_" for c in topic.lower())[:25].strip("_")
    key = f"web_{slug}"

    learning_service.add_or_update_memory(
        category="FACTUAL_KNOWLEDGE",
        key=key,
        content=f"Knowledge on '{topic}': {summary[:400]}...",
        source="AUTOMATIC_EXTRACTION",
        confidence_score=0.95
    )

    return f"🧠 *Learned & Saved to Memory:* Researched '{topic}' via Google Search and recorded findings under `{key}`."
