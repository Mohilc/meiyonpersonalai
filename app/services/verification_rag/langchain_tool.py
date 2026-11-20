"""LangChain Tool wrapper for EmailAI Verification RAG.

Exposes `verify_sender_security_context` as a callable LangChain Tool ready for
the autonomous ReAct / Tool-Calling Agent and NVIDIA NEMOTRON / GEMINI pipelines.
"""
import json
import logging
from typing import Optional

from app.services.verification_rag.verifier import verify_sender_context

logger = logging.getLogger(__name__)

# Lazy LangChain tool import
try:
    from langchain_core.tools import tool
    LANGCHAIN_TOOL_AVAILABLE = True
except ImportError:
    LANGCHAIN_TOOL_AVAILABLE = False
    logger.warning("LangChain Core not installed. LangChain tool decorator fallback engaged.")

    # Simple fallback decorator
    def tool(func):
        return func


@tool
def verify_sender_security_context(
    sender_email: str,
    domain: Optional[str] = None,
    message_text: Optional[str] = None,
    source_platform: str = "Email"
) -> str:
    """Verifies an incoming recruiter or email sender against the enterprise allowlist,
    talent directory, and scam/phishing signatures stored in Supabase pgvector.

    Args:
        sender_email: Email address of the sender (e.g. 'recruiter@greenhouse.io')
        domain: Optional extracted domain (e.g. 'greenhouse.io')
        message_text: Snippet or full text of the incoming message to inspect for phishing
        source_platform: Communication channel ('Email' or 'LinkedIn')

    Returns:
        JSON string containing matched_entities, domain_trust_signals, risk_flags, and confidence_score.
    """
    try:
        result = verify_sender_context(
            sender_email=sender_email,
            domain=domain,
            message_text=message_text,
            source_platform=source_platform
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error("Error executing verify_sender_security_context tool: %s", str(e))
        return json.dumps({
            "matched_entities": [],
            "domain_trust_signals": [],
            "risk_flags": [f"Verification error: {str(e)}"],
            "confidence_score": 0.0
        })
