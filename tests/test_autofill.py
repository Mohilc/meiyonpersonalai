"""Unit tests for Autonomous Link and Form Autofill Engine."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.autofill import FormFieldType
from app.services.autofill import (
    detect_platform_from_url,
    extract_form_fields_from_html,
    generate_platform_fallback_fields,
    autofill_form,
    generate_essay_answer,
    generate_bookmarklet_code,
    generate_playwright_snippet
)
from app.services.messaging_bot_service import handle_incoming_text
from app.services.agent_service import ALL_AGENT_TOOLS

client = TestClient(app)

SAMPLE_HTML_FORM = """
<!DOCTYPE html>
<html>
<head><title>Senior AI Engineer Application - Acme Corp</title></head>
<body>
  <form id="application-form">
    <label for="first_name">First Name *</label>
    <input type="text" id="first_name" name="first_name" required>

    <label for="last_name">Last Name *</label>
    <input type="text" id="last_name" name="last_name" required>

    <label for="email">Email Address *</label>
    <input type="email" id="email" name="email" placeholder="name@domain.com" required>

    <label for="phone">Phone Number</label>
    <input type="tel" id="phone" name="phone">

    <label for="college">University / College</label>
    <input type="text" id="college" name="college">

    <label for="degree">Degree & Major</label>
    <input type="text" id="degree" name="degree">

    <label for="grad_year">Year of Graduation</label>
    <input type="text" id="grad_year" name="grad_year">

    <label for="linkedin_url">LinkedIn URL</label>
    <input type="text" id="linkedin_url" name="linkedin_url">

    <label for="github_url">GitHub Profile</label>
    <input type="text" id="github_url" name="github_url">

    <label for="work_auth">Are you legally authorized to work?</label>
    <select id="work_auth" name="work_auth">
      <option value="">Select option</option>
      <option value="Yes">Yes</option>
      <option value="No">No</option>
    </select>

    <label for="why_interested">Why do you want to join our engineering team?</label>
    <textarea id="why_interested" name="why_interested"></textarea>

    <label for="resume">Upload Resume</label>
    <input type="file" id="resume" name="resume">

    <button type="submit">Submit Application</button>
  </form>
</body>
</html>
"""


def test_detect_platform_from_url():
    """Verify platform detection across known ATS systems and web portals."""
    assert detect_platform_from_url("https://boards.greenhouse.io/spacex/jobs/12345") == "Greenhouse"
    assert detect_platform_from_url("https://jobs.lever.co/palantir/abcde") == "Lever"
    assert detect_platform_from_url("https://docs.google.com/forms/d/e/1FAIpQLSc/viewform") == "Google Forms"
    assert detect_platform_from_url("https://jobs.ashbyhq.com/openai/98765") == "Ashby"
    assert detect_platform_from_url("https://mycompany.myworkdayjobs.com/careers/job/1") == "Workday"
    assert detect_platform_from_url("https://mycompany.com/apply") == "Generic Web Form"


def test_extract_form_fields_from_html():
    """Verify HTML parsing extracts correct labels, field types, and CSS selectors."""
    title, fields = extract_form_fields_from_html(SAMPLE_HTML_FORM)
    assert "Acme Corp" in title
    assert len(fields) == 12

    # Check first name
    fn = next(f for f in fields if f.category == "first_name")
    assert fn.selector == "#first_name"
    assert fn.field_type == FormFieldType.TEXT
    assert fn.required is True

    # Check email
    em = next(f for f in fields if f.category == "email")
    assert em.selector == "#email"
    assert em.field_type == FormFieldType.EMAIL

    # Check select
    wa = next(f for f in fields if f.category == "work_authorization")
    assert wa.field_type == FormFieldType.SELECT
    assert "Yes" in wa.options

    # Check textarea essay
    essay = next(f for f in fields if f.category == "essay")
    assert essay.field_type == FormFieldType.TEXTAREA


def test_autofill_form_with_raw_html():
    """Verify autofill_form accurately populates fields from Mohil's profile and resume."""
    res = autofill_form(
        url="https://acme.com/apply",
        raw_html=SAMPLE_HTML_FORM,
        job_title="AI Robotics Engineer",
        company_name="Acme Corp"
    )

    assert res.detected_platform == "Generic Web Form"
    assert res.total_fields == 12
    assert res.filled_count >= 10
    assert res.fill_percentage >= 80.0
    assert res.staged_for_review is True

    # Check mapped values
    vals = {ff.field.category: ff.suggested_value for ff in res.filled_fields}
    assert "Mohil" in vals["first_name"] or "Mohil" in vals.get("full_name", "")
    assert "@" in vals["email"]
    assert "Mar Baselios" in vals["college"]
    assert "linkedin.com" in vals["linkedin"]
    assert "github.com" in vals["github"]
    assert "Yes" in vals["work_authorization"]
    assert "autonomous" in vals["essay"].lower() or "engineering" in vals["essay"].lower()

    # Check bookmarklet & playwright script
    assert "javascript:(function()" in res.javascript_bookmarklet
    assert "async_playwright" in res.playwright_script


def test_autofill_form_greenhouse_fallback():
    """Verify Greenhouse platform template fallback when network is unavailable."""
    res = autofill_form(url="https://boards.greenhouse.io/scaleai/jobs/4001")
    assert res.detected_platform == "Greenhouse"
    assert res.total_fields >= 8
    assert res.filled_count >= 7
    assert res.fill_percentage >= 75.0


def test_autofill_form_lever_fallback():
    """Verify Lever platform template fallback."""
    res = autofill_form(url="https://jobs.lever.co/anthropic/5002")
    assert res.detected_platform == "Lever"
    assert res.total_fields >= 7
    assert res.filled_count >= 6


def test_autofill_form_google_forms_fallback():
    """Verify Google Forms platform template fallback."""
    res = autofill_form(url="https://docs.google.com/forms/d/e/1FAIpQLSdDemo/viewform")
    assert res.detected_platform == "Google Forms"
    assert res.total_fields >= 5
    assert res.filled_count >= 5


def test_generate_essay_answers():
    """Verify essay answer generator creates grounded responses for key application prompts."""
    ans_why = generate_essay_answer("Why do you want to join our company?", company="NVIDIA", role="Deep Learning Intern")
    assert "NVIDIA" in ans_why
    assert "autonomous" in ans_why.lower() or "machine learning" in ans_why.lower()

    ans_proj = generate_essay_answer("Describe a technical project or achievement.")
    assert "YOLO" in ans_proj or "Autonomous" in ans_proj or "Meiyon" in ans_proj

    ans_cover = generate_essay_answer("Cover Letter / Additional Notes")
    assert "Mar Baselios" in ans_cover


def test_routes_autofill_supported_platforms():
    """Verify GET /api/autofill/supported-platforms endpoint."""
    resp = client.get("/api/autofill/supported-platforms")
    assert resp.status_code == 200
    data = resp.json()
    assert "Greenhouse" in str(data["supported_platforms"])
    assert "Lever" in str(data["supported_platforms"])
    assert "first_name" in data["supported_categories"]


def test_routes_autofill_parse():
    """Verify POST /api/autofill/parse endpoint."""
    payload = {
        "url": "https://test.com/form",
        "raw_html": SAMPLE_HTML_FORM
    }
    resp = client.post("/api/autofill/parse", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_fields"] == 12
    assert len(data["fields"]) == 12


def test_routes_autofill_fill():
    """Verify POST /api/autofill/fill endpoint."""
    payload = {
        "url": "https://boards.greenhouse.io/demo/jobs/123",
        "job_title": "AI Engineer",
        "company_name": "Demo Tech"
    }
    resp = client.post("/api/autofill/fill", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["detected_platform"] == "Greenhouse"
    assert data["filled_count"] > 0
    assert "javascript:" in data["javascript_bookmarklet"]


def test_bot_autofill_command():
    """Verify /autofill command in messaging bot service."""
    response = handle_incoming_text(sender_id="test_user", platform="telegram", text="/autofill https://boards.greenhouse.io/test/jobs/99")
    assert "MEIYON AUTOFILL ENGINE" in response
    assert "Greenhouse" in response
    assert "Coverage:" in response


def test_agent_autofill_tool_present():
    """Verify autofill_link_or_form tool is registered in LangChain agent suite."""
    tool_names = [getattr(t, "name", str(t)) for t in ALL_AGENT_TOOLS]
    assert "autofill_link_or_form" in tool_names

    # Test tool execution
    tool = next(t for t in ALL_AGENT_TOOLS if getattr(t, "name", "") == "autofill_link_or_form")
    output = tool.invoke({"url": "https://jobs.lever.co/demo/777"})
    assert "Form Autofill Ready" in output
    assert "Lever" in output
