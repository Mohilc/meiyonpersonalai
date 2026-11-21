"""FastAPI endpoints for Autonomous Link and Form Autofill Engine."""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body

from app.models.autofill import (
    AutofillRequest,
    FormAutofillResult,
    AutofillExecuteRequest
)
from app.services.autofill import (
    autofill_form,
    fetch_and_parse_form,
    detect_platform_from_url,
    execute_headless_autofill,
    KNOWN_PLATFORMS
)

router = APIRouter(prefix="/api/autofill", tags=["autofill"])


@router.get("/supported-platforms")
def get_supported_platforms():
    """Returns the list of recognized ATS portals, form platforms, and supported categories."""
    return {
        "supported_platforms": KNOWN_PLATFORMS,
        "supported_categories": [
            "first_name", "last_name", "full_name", "email", "phone",
            "linkedin", "github", "portfolio", "college", "degree",
            "graduation_year", "gpa", "location", "work_authorization",
            "essay", "resume_upload"
        ],
        "delivery_methods": [
            "1-Click JavaScript Bookmarklet (Instant browser DOM population)",
            "Automated Headless Playwright Script (Background execution + screenshot preview)",
            "Structured Field Mapping JSON (For API/extension integration)"
        ]
    }


@router.post("/parse")
def parse_form_fields(payload: AutofillRequest):
    """Inspects a form link or raw HTML and extracts all interactive input fields."""
    try:
        title, platform, fields = fetch_and_parse_form(payload.url, raw_html=payload.raw_html)
        return {
            "url": payload.url,
            "title": title,
            "detected_platform": platform,
            "total_fields": len(fields),
            "fields": [f.model_dump() for f in fields]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to inspect form fields: {str(e)}")


@router.post("/fill", response_model=FormAutofillResult)
def autofill_link(payload: AutofillRequest):
    """
    End-to-end form autofill pipeline:
    Parses form fields, matches them with Mohil's profile and master resume,
    synthesizes answers for custom questions, and produces automation scripts.
    """
    try:
        result = autofill_form(
            url=payload.url,
            raw_html=payload.raw_html,
            job_title=payload.job_title,
            company_name=payload.company_name,
            custom_notes=payload.custom_notes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate autofill answers: {str(e)}")


@router.post("/execute")
async def execute_browser_fill(payload: AutofillExecuteRequest):
    """Executes headless Playwright browser to populate the live web form and capture screenshot."""
    try:
        res = await execute_headless_autofill(
            url=payload.url,
            field_values=payload.field_values,
            take_screenshot=payload.take_screenshot
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute headless form filling: {str(e)}")
