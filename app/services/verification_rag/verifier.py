"""Fast Live Verification Engine for EmailAI Verification RAG.

Queries ONLY the Supabase pgvector index (never Google Drive live) to evaluate:
- Sender trust signals & verified company allowlists
- Recruiter partner directory verification
- Scam & phishing pattern detection
- Overall confidence score

Returns strict JSON schema:
{
  "matched_entities": [],
  "domain_trust_signals": [],
  "risk_flags": [],
  "confidence_score": 0.0
}
"""
import re
import time
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.services.verification_rag import vector_index

logger = logging.getLogger(__name__)

# Fast in-memory TTL query cache (5 minute expiry) to guarantee sub-millisecond repeated checks
_VERIFICATION_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 300


def _extract_domain(email_or_domain: str) -> str:
    """Extracts clean lowercase domain from email address or URL."""
    if not email_or_domain:
        return ""
    text = email_or_domain.lower().strip()
    if "@" in text:
        return text.split("@")[-1].strip()
    # Strip protocol if URL
    clean = re.sub(r"^https?://", "", text)
    return clean.split("/")[0].strip()


def verify_sender_context(
    sender_email: str,
    domain: Optional[str] = None,
    message_text: Optional[str] = None,
    source_platform: str = "Email"
) -> Dict[str, Any]:
    """
    Performs fast, live message verification against the Supabase pgvector index.
    
    CRITICAL INVARIANT:
    This function NEVER touches Google Drive. It queries exclusively the cached
    and pre-indexed Supabase pgvector index.
    """
    start_time = time.time()
    clean_sender = (sender_email or "").strip().lower()
    clean_domain = (domain or "").strip().lower() or _extract_domain(clean_sender)
    clean_msg = (message_text or "").strip()
    platform = source_platform if source_platform in ("Email", "LinkedIn") else "Email"

    cache_key = f"{clean_sender}:{clean_domain}:{platform}:{hash(clean_msg[:120])}"

    # 1. Check TTL cache
    cached = _VERIFICATION_CACHE.get(cache_key)
    if cached:
        cached_ts = cached.get("_cached_at", 0)
        if (time.time() - cached_ts) < CACHE_TTL_SECONDS:
            logger.debug("Verification RAG cache hit for %s (< 1ms)", clean_sender)
            result_copy = dict(cached["data"])
            return result_copy

    matched_entities: List[str] = []
    domain_trust_signals: List[str] = []
    risk_flags: List[str] = []
    confidence_score: float = 0.50

    try:
        # 2. Query 1: Allowlist & Enterprise ATS Matching
        allowlist_results = vector_index.query_verification_index(
            query_text=f"domain {clean_domain} recruiter {clean_sender}",
            category="ALLOWLIST",
            top_k=3,
            match_threshold=0.35
        )

        for match in allowlist_results:
            text = match.get("text", "").lower()
            if clean_domain and clean_domain in text:
                matched_entities.append(f"Verified ATS Domain: {clean_domain}")
                domain_trust_signals.append(f"Domain '{clean_domain}' matches verified enterprise talent infrastructure.")
                confidence_score = max(confidence_score, 0.95)

        # 3. Query 2: Recruiter Directory Search
        recruiter_results = vector_index.query_verification_index(
            query_text=f"{clean_sender} {clean_domain} recruiter coordinator talent",
            category="RECRUITER_DIRECTORY",
            top_k=3,
            match_threshold=0.35
        )

        for match in recruiter_results:
            text = match.get("text", "")
            if clean_domain and clean_domain in text.lower():
                matched_entities.append(f"Recruiter Directory Match: {clean_domain}")
                domain_trust_signals.append("Matches verified technical talent partners directory.")
                confidence_score = max(confidence_score, 0.90)

        # 4. Query 3: Scam & Phishing Signature Analysis
        if clean_msg:
            scam_results = vector_index.query_verification_index(
                query_text=clean_msg[:500],
                category="SCAM_PATTERN",
                top_k=3,
                match_threshold=0.30
            )

            # Heuristic and semantic flags
            msg_lower = clean_msg.lower()
            scam_triggers = [
                ("cashier's check", "Advance fee or equipment check scam signature"),
                ("check deposit", "Equipment purchase check scam pattern"),
                ("telegram", "Redirection to unverified Telegram channel"),
                ("whatsapp", "Directing business communication off official email"),
                ("crypto", "Cryptocurrency or task escrow requirement"),
                ("usdt", "Crypto payment demand"),
                ("wire transfer", "High-risk banking request"),
                ("equipment fee", "Upfront equipment fee request")
            ]

            for phrase, desc in scam_triggers:
                if phrase in msg_lower:
                    risk_flags.append(f"Flagged Trigger '{phrase}': {desc}")
                    confidence_score = min(confidence_score, 0.20)

            # Free webmail check for recruiting or scam patterns
            if clean_domain in ("gmail.com", "outlook.com", "yahoo.com", "hotmail.com", "protonmail.com"):
                recruiting_cues = ("job", "offer", "interview", "hiring", "position", "recruiter", "equipment", "cashier", "congratulations", "work")
                if any(w in msg_lower for w in recruiting_cues) or risk_flags:
                    risk_flags.append(f"Free webmail domain '{clean_domain}' used for recruiter communication.")
                    confidence_score = min(confidence_score, 0.35)
                    risk_flags.append(f"Free webmail domain '{clean_domain}' used for recruiter communication.")
                    confidence_score = min(confidence_score, 0.35)

        # Baseline adjustments if no risks found and domain looks legitimate
        if not risk_flags and clean_domain:
            if clean_domain not in ("gmail.com", "yahoo.com", "outlook.com"):
                domain_trust_signals.append(f"Corporate email domain: {clean_domain}")
                confidence_score = max(confidence_score, 0.75)

    except Exception as e:
        logger.warning("Verification RAG query exception: %s. Using safe fallback.", str(e))
        risk_flags.append("Verification service fallback engaged.")
        confidence_score = 0.50

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    final_result = {
        "matched_entities": list(dict.fromkeys(matched_entities)),
        "domain_trust_signals": list(dict.fromkeys(domain_trust_signals)),
        "risk_flags": list(dict.fromkeys(risk_flags)),
        "confidence_score": round(confidence_score, 2),
        "source_platform": platform,
        "elapsed_ms": elapsed_ms
    }

    # Cache result
    _VERIFICATION_CACHE[cache_key] = {
        "data": final_result,
        "_cached_at": time.time()
    }

    return final_result
