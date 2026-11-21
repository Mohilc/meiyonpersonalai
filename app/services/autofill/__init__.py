"""Autonomous Link and Form Autofill Engine for Meiyon Personal AI Manager."""
from app.services.autofill.form_detector import (
    detect_platform_from_url,
    fetch_and_parse_form,
    extract_form_fields_from_html,
    generate_platform_fallback_fields,
    KNOWN_PLATFORMS
)
from app.services.autofill.form_filler import (
    autofill_form,
    generate_essay_answer,
    generate_bookmarklet_code,
    generate_playwright_snippet
)
from app.services.autofill.playwright_executor import execute_headless_autofill

__all__ = [
    "detect_platform_from_url",
    "fetch_and_parse_form",
    "extract_form_fields_from_html",
    "generate_platform_fallback_fields",
    "KNOWN_PLATFORMS",
    "autofill_form",
    "generate_essay_answer",
    "generate_bookmarklet_code",
    "generate_playwright_snippet",
    "execute_headless_autofill"
]
