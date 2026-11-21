"""Intelligent Form Filler, Answer Synthesizer, and Automation Script Generator."""
import re
import json
import logging
from typing import List, Dict, Any, Optional

from app.models.autofill import FormField, FilledFormField, FormAutofillResult, FormFieldType
from app.services.autofill.form_detector import fetch_and_parse_form
from app.services.profile_service import get_profile
from app.services.resume_service import get_active_master_resume
from app.services import llm_service

logger = logging.getLogger(__name__)


def generate_essay_answer(prompt_label: str, company: Optional[str] = None, role: Optional[str] = None) -> str:
    """
    Generates a factually grounded, high-impact answer for custom application questions
    citing Mohil's actual engineering projects (Drone Robotics, Vision, FastAPI AI Assistant).
    """
    comp_str = f"at {company}" if company else ""
    role_str = f"for the {role} position" if role else ""
    
    clean_p = prompt_label.lower()

    # Why interested / Motivation
    if any(k in clean_p for k in ("why do you want", "why are you interested", "motivation", "why this role", "why join")):
        return (
            f"I am deeply excited to apply {role_str} {comp_str}. "
            "As an AI & Computer Science undergraduate specializing in autonomous systems and backend engineering, "
            "I thrive on solving complex technical challenges at the intersection of machine learning, low-latency API design, "
            "and edge computation. My work building autonomous drone telemetry pipelines and architecting agentic AI assistants "
            "has taught me the value of rigorous engineering, clean modular architecture, and rapid execution. "
            "I want to bring this proactive problem-solving mindset to contribute directly to your team's mission."
        )

    # Technical Project / Accomplishment
    if any(k in clean_p for k in ("project", "achievement", "technical challenge", "accomplishment", "built")):
        return (
            "One of my flagship engineering achievements is designing an Autonomous Aerial Perception & Telemetry pipeline. "
            "Running real-time object detection on embedded companion computers is heavily constrained by thermal envelopes and compute limits. "
            "By optimizing our custom YOLO pipeline with TensorRT FP16 quantization and zero-copy NVMM streaming, "
            "I achieved 45+ FPS at sub-22ms latency on edge hardware without frame degradation. "
            "Additionally, I architected Meiyon, an autonomous executive assistant utilizing FastAPI, SQLite in WAL mode, "
            "and multi-agent LangChain orchestration with strict human-in-the-loop security gates."
        )

    # Cover Letter / Additional Information
    if any(k in clean_p for k in ("cover letter", "additional", "anything else", "comments", "notes")):
        return (
            "Thank you for considering my application. I am an undergraduate engineer in Computer Science with Artificial Intelligence "
            "at Mar Baselios Christian College of Engineering & Technology (Class of 2027). "
            "My technical toolkit centers on Python, FastAPI, Machine Learning, autonomous systems, and agentic workflows. "
            "I take pride in writing robust, production-tested code, learning rapidly, and executing with high ownership. "
            "I look forward to discussing how my background aligns with your engineering goals."
        )

    # General fallback
    return (
        "I am an AI & Computer Science undergraduate passionate about building reliable software, "
        "autonomous robotics, and intelligent systems. I bring strong skills in Python, FastAPI, and Machine Learning, "
        "along with hands-on project experience in edge computer vision and production agentic architectures."
    )


def generate_bookmarklet_code(filled_fields: List[FilledFormField]) -> str:
    """
    Generates a 1-click JavaScript bookmarklet that populates the web form in modern browsers.
    Triggers 'input' and 'change' events so React, Vue, and Angular frameworks register updates.
    """
    actions = []
    for ff in filled_fields:
        if ff.field.field_type == FormFieldType.FILE:
            continue  # Browser security prevents programmatic file path setting
        
        # Escape single quotes and newlines for JavaScript literal
        val_escaped = ff.suggested_value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "")
        sel_escaped = ff.selector.replace("'", "\\'")

        code = (
            f"(function(){{"
            f"const el = document.querySelector('{sel_escaped}');"
            f"if (el) {{"
            f"el.focus();"
            f"el.value = '{val_escaped}';"
            f"el.dispatchEvent(new Event('input', {{ bubbles: true }}));"
            f"el.dispatchEvent(new Event('change', {{ bubbles: true }}));"
            f"el.blur();"
            f"}}"
            f"}})();"
        )
        actions.append(code)

    all_js = "".join(actions)
    notification = "alert('✅ Meiyon AI: Autofilled " + str(len(actions)) + " fields successfully! Please review before submitting.');"
    bookmarklet = f"javascript:(function(){{{all_js}{notification}}})();"
    return bookmarklet


def generate_playwright_snippet(url: str, filled_fields: List[FilledFormField]) -> str:
    """Generates a standalone Python Playwright script to automate form filling headlessly."""
    lines = [
        "import asyncio",
        "from playwright.async_api import async_playwright",
        "",
        "async def run_autofill():",
        "    async with async_playwright() as p:",
        "        browser = await p.chromium.launch(headless=False)",
        "        page = await browser.new_page()",
        f"        await page.goto('{url}', wait_until='networkidle')",
        ""
    ]

    for ff in filled_fields:
        if ff.field.field_type == FormFieldType.FILE:
            continue
        val = ff.suggested_value.replace("'", "\\'").replace("\n", "\\n")
        lines.append(f"        try:")
        lines.append(f"            await page.fill('{ff.selector}', '{val}')")
        lines.append(f"        except Exception:")
        lines.append(f"            pass")

    lines.append("")
    lines.append("        print('Form filled! Take screenshot for verification.')")
    lines.append("        await page.screenshot(path='autofill_preview.png')")
    lines.append("        # Kept open for human review before manual submission")
    lines.append("        await asyncio.sleep(10)")
    lines.append("        await browser.close()")
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    asyncio.run(run_autofill())")

    return "\n".join(lines)


def autofill_form(
    url: str,
    raw_html: Optional[str] = None,
    job_title: Optional[str] = None,
    company_name: Optional[str] = None,
    custom_notes: Optional[str] = None
) -> FormAutofillResult:
    """
    Autonomous form parsing and answer generation pipeline:
    1. Extracts fields from URL or HTML.
    2. Matches fields against Mohil's profile & master resume.
    3. Synthesizes answers for custom essay questions.
    4. Generates 1-click JavaScript bookmarklet and Playwright automation code.
    """
    title, platform, fields = fetch_and_parse_form(url, raw_html=raw_html)

    # Load verified profile & master resume
    profile = get_profile()
    resume = get_active_master_resume()

    full_name = resume.full_name or profile.full_name or "Mohil"
    name_parts = full_name.split()
    first_name = name_parts[0] if name_parts else "Mohil"
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "C"

    email = resume.contact_email or "mohil@example.com"
    phone = resume.phone or "+91-8590144798"
    linkedin = resume.linkedin_url or "https://linkedin.com/in/mohil"
    github = resume.github_url or "https://github.com/mohil"
    college = profile.college or "Mar Baselios Christian College of Engineering & Technology, Kuttikkanam"
    degree = profile.education or "B.Tech in Computer Science with Artificial Intelligence"
    grad_year = profile.expected_graduation or "2027"

    filled_fields: List[FilledFormField] = []
    unfilled_fields: List[FormField] = []

    for f in fields:
        cat = f.category
        val: Optional[str] = None
        source = "profile"
        conf = 1.0

        if cat == "first_name":
            val = first_name
        elif cat == "last_name":
            val = last_name
        elif cat == "full_name":
            val = full_name
        elif cat == "email":
            val = email
        elif cat == "phone":
            val = phone
        elif cat == "linkedin":
            val = linkedin
            source = "resume"
        elif cat == "github":
            val = github
            source = "resume"
        elif cat == "portfolio":
            val = github
            source = "resume"
        elif cat == "college":
            val = college
        elif cat == "degree":
            val = degree
        elif cat == "graduation_year":
            val = grad_year
        elif cat == "gpa":
            val = "8.8"
            conf = 0.9
        elif cat == "location":
            val = "Kerala, India"
        elif cat == "work_authorization":
            # If select field with options, choose best matching option
            if f.options:
                yes_opt = next((opt for opt in f.options if "yes" in opt.lower()), f.options[0])
                val = yes_opt
            else:
                val = "Yes, legally authorized to work without sponsorship"
            conf = 0.95
        elif cat == "essay":
            val = generate_essay_answer(f.label, company=company_name, role=job_title)
            source = "ai_generated"
            conf = 0.92
        elif cat == "resume_upload":
            val = "[Resume Document: Mohil_AI_Engineer_Resume.pdf]"
            source = "resume"
            conf = 0.85
        else:
            # Fallback heuristic for unclassified text fields
            lbl_lower = f.label.lower()
            if "name" in lbl_lower:
                val = full_name
            elif "mail" in lbl_lower:
                val = email
            elif "college" in lbl_lower or "school" in lbl_lower:
                val = college
            elif "link" in lbl_lower:
                val = linkedin

        if val:
            filled_fields.append(FilledFormField(
                field=f,
                suggested_value=val,
                confidence=conf,
                source=source,
                selector=f.selector
            ))
        else:
            unfilled_fields.append(f)

    total = len(fields)
    filled_cnt = len(filled_fields)
    percentage = round((filled_cnt / total * 100.0), 1) if total > 0 else 0.0

    bookmarklet = generate_bookmarklet_code(filled_fields)
    playwright_code = generate_playwright_snippet(url, filled_fields)

    summary = (
        f"Detected {platform} form at {url}. "
        f"Successfully mapped {filled_cnt}/{total} fields ({percentage}%). "
        f"1-click JavaScript bookmarklet and Playwright automation script generated. "
        "Staged for human review."
    )

    return FormAutofillResult(
        url=url,
        title=title,
        detected_platform=platform,
        total_fields=total,
        filled_count=filled_cnt,
        fill_percentage=percentage,
        filled_fields=filled_fields,
        unfilled_fields=unfilled_fields,
        javascript_bookmarklet=bookmarklet,
        playwright_script=playwright_code,
        staged_for_review=True,
        summary=summary
    )
