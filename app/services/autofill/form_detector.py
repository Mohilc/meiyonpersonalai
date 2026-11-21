"""Form Detector & Parser for Autonomous Link & Form Autofill Engine."""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup

from app.models.autofill import FormField, FormFieldType

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Platform signature recognizers
KNOWN_PLATFORMS = {
    "greenhouse.io": "Greenhouse",
    "job-boards.greenhouse.io": "Greenhouse",
    "jobs.lever.co": "Lever",
    "docs.google.com": "Google Forms",
    "forms.gle": "Google Forms",
    "jobs.ashbyhq.com": "Ashby",
    "myworkdayjobs.com": "Workday",
    "typeform.com": "Typeform"
}


def detect_platform_from_url(url: str) -> str:
    """Detects ATS or form hosting platform from URL host."""
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    for domain, platform_name in KNOWN_PLATFORMS.items():
        if domain in netloc:
            return platform_name
    return "Generic Web Form"


def categorize_field(label: str, name: str, placeholder: str, elem_type: str = "text") -> str:
    """Classifies form field into functional semantic category."""
    text = f"{label} {name} {placeholder}".lower()

    # 1. Email check first (highest priority, prevents placeholder="name@domain.com" matching "name")
    if elem_type == "email" or any(k in text for k in ("email", "e-mail", "mail address")):
        return "email"

    # 2. Phone check
    if elem_type == "tel" or any(k in text for k in ("phone", "mobile", "cell", "telephone", "contact number")):
        return "phone"

    # 3. Names
    if any(k in text for k in ("first name", "firstname", "given name", "forename")):
        return "first_name"
    if any(k in text for k in ("last name", "lastname", "surname", "family name")):
        return "last_name"
    if any(k in text for k in ("full name", "fullname", "your name", "candidate name")) or (re.search(r"\bname\b", text) and "company" not in text and "school" not in text and "college" not in text):
        return "full_name"
    if any(k in text for k in ("linkedin", "linkedin.com", "linkedin url", "profile url")):
        return "linkedin"
    if any(k in text for k in ("github", "github.com", "github url", "git repo")):
        return "github"
    if any(k in text for k in ("portfolio", "website", "personal site", "personal url")):
        return "portfolio"
    if any(k in text for k in ("college", "university", "school", "institution", "campus")):
        return "college"
    if any(k in text for k in ("degree", "major", "field of study", "program", "department", "discipline")):
        return "degree"
    if any(k in text for k in ("graduation", "grad year", "passing year", "batch", "completion date")):
        return "graduation_year"
    if any(k in text for k in ("gpa", "cgpa", "percentage", "marks")):
        return "gpa"
    if any(k in text for k in ("work authorization", "authorized to work", "legally authorized", "sponsorship", "visa", "eligibility")):
        return "work_authorization"
    if any(k in text for k in ("why do you want", "why are you interested", "cover letter", "tell us about", "describe", "about yourself", "notes", "additional information", "essay")):
        return "essay"
    if any(k in text for k in ("resume", "cv", "attach resume", "upload cv", "curriculum vitae")):
        return "resume_upload"
    if any(k in text for k in ("city", "location", "address", "state", "country")):
        return "location"
    
    return "general"


def extract_form_fields_from_html(html_content: str, base_url: str = "") -> Tuple[str, List[FormField]]:
    """Parses raw HTML and extracts all interactive input fields with clean CSS selectors."""
    soup = BeautifulSoup(html_content, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "Online Application Form"
    fields: List[FormField] = []

    # Map label for="..." targets
    label_map: Dict[str, str] = {}
    for label in soup.find_all("label"):
        for_id = label.get("for")
        label_text = label.get_text(strip=True)
        if for_id and label_text:
            label_map[for_id] = label_text

    # Locate inputs, textareas, and selects
    elements = soup.find_all(["input", "textarea", "select"])

    for elem in elements:
        tag_name = elem.name.lower()
        elem_type = elem.get("type", "text").lower() if tag_name == "input" else tag_name
        
        # Skip non-data interactive elements
        if elem_type in ("hidden", "submit", "reset", "button", "image"):
            continue

        elem_id = elem.get("id")
        elem_name = elem.get("name")
        placeholder = elem.get("placeholder", "")
        aria_label = elem.get("aria-label", "")
        required = elem.has_attr("required") or elem.get("aria-required") == "true"

        # Determine best human-readable label
        label = ""
        if elem_id and elem_id in label_map:
            label = label_map[elem_id]
        elif aria_label:
            label = aria_label
        elif elem.parent and elem.parent.name == "label":
            label = elem.parent.get_text(strip=True)
        elif placeholder:
            label = placeholder
        elif elem_name:
            label = elem_name.replace("_", " ").replace("-", " ").title()
        elif elem_id:
            label = elem_id.replace("_", " ").replace("-", " ").title()
        else:
            label = "Form Field"

        # Map FormFieldType enum
        if tag_name == "textarea":
            field_type = FormFieldType.TEXTAREA
        elif tag_name == "select":
            field_type = FormFieldType.SELECT
        elif elem_type == "email":
            field_type = FormFieldType.EMAIL
        elif elem_type == "tel":
            field_type = FormFieldType.TEL
        elif elem_type == "file":
            field_type = FormFieldType.FILE
        elif elem_type == "radio":
            field_type = FormFieldType.RADIO
        elif elem_type == "checkbox":
            field_type = FormFieldType.CHECKBOX
        elif elem_type == "date":
            field_type = FormFieldType.DATE
        elif elem_type == "number":
            field_type = FormFieldType.NUMBER
        else:
            field_type = FormFieldType.TEXT

        # Extract options for select elements
        options = []
        if tag_name == "select":
            for opt in elem.find_all("option"):
                opt_text = opt.get_text(strip=True)
                opt_val = opt.get("value", opt_text)
                if opt_val and opt_val != "":
                    options.append(opt_text or opt_val)

        category = categorize_field(label, elem_name or "", placeholder, elem_type=elem_type)

        # Build clean CSS selector
        if elem_id:
            selector = f"#{elem_id}"
        elif elem_name:
            selector = f"{tag_name}[name=\"{elem_name}\"]"
        elif placeholder:
            selector = f"{tag_name}[placeholder=\"{placeholder}\"]"
        else:
            selector = tag_name

        fields.append(FormField(
            field_id=elem_id,
            name=elem_name,
            label=label,
            placeholder=placeholder,
            field_type=field_type,
            options=options,
            required=required,
            category=category,
            selector=selector
        ))

    return title, fields


def generate_platform_fallback_fields(platform: str) -> List[FormField]:
    """Provides high-fidelity template fields when live network scraping is restricted."""
    if platform == "Greenhouse":
        return [
            FormField(field_id="first_name", name="first_name", label="First Name", field_type=FormFieldType.TEXT, required=True, category="first_name", selector="#first_name"),
            FormField(field_id="last_name", name="last_name", label="Last Name", field_type=FormFieldType.TEXT, required=True, category="last_name", selector="#last_name"),
            FormField(field_id="email", name="email", label="Email", field_type=FormFieldType.EMAIL, required=True, category="email", selector="#email"),
            FormField(field_id="phone", name="phone", label="Phone", field_type=FormFieldType.TEL, required=True, category="phone", selector="#phone"),
            FormField(field_id="resume", name="resume", label="Resume/CV", field_type=FormFieldType.FILE, required=True, category="resume_upload", selector="#resume"),
            FormField(field_id="job_application_answers_attributes_0_text_value", name="linkedin_url", label="LinkedIn Profile", field_type=FormFieldType.TEXT, category="linkedin", selector="input[name*='linkedin']"),
            FormField(field_id="job_application_answers_attributes_1_text_value", name="github_url", label="GitHub / Portfolio URL", field_type=FormFieldType.TEXT, category="github", selector="input[name*='github']"),
            FormField(field_id="cover_letter_text", name="cover_letter_text", label="Cover Letter / Notes", field_type=FormFieldType.TEXTAREA, category="essay", selector="textarea[name*='cover_letter']"),
            FormField(field_id="work_authorization", name="work_authorization", label="Are you legally authorized to work in this location?", field_type=FormFieldType.SELECT, options=["Yes", "No"], required=True, category="work_authorization", selector="select[name*='authorized']")
        ]
    elif platform == "Lever":
        return [
            FormField(field_id="name", name="name", label="Full Name", field_type=FormFieldType.TEXT, required=True, category="full_name", selector="input[name='name']"),
            FormField(field_id="email", name="email", label="Email", field_type=FormFieldType.EMAIL, required=True, category="email", selector="input[name='email']"),
            FormField(field_id="phone", name="phone", label="Phone", field_type=FormFieldType.TEL, required=True, category="phone", selector="input[name='phone']"),
            FormField(field_id="org", name="org", label="Current Company / University", field_type=FormFieldType.TEXT, category="college", selector="input[name='org']"),
            FormField(field_id="urls_linkedin", name="urls[LinkedIn]", label="LinkedIn URL", field_type=FormFieldType.TEXT, category="linkedin", selector="input[name*='LinkedIn']"),
            FormField(field_id="urls_github", name="urls[GitHub]", label="GitHub URL", field_type=FormFieldType.TEXT, category="github", selector="input[name*='GitHub']"),
            FormField(field_id="urls_portfolio", name="urls[Portfolio]", label="Portfolio URL", field_type=FormFieldType.TEXT, category="portfolio", selector="input[name*='Portfolio']"),
            FormField(field_id="comments", name="comments", label="Additional Information", field_type=FormFieldType.TEXTAREA, category="essay", selector="textarea[name='comments']")
        ]
    elif platform == "Google Forms":
        return [
            FormField(field_id="entry_name", name="entry.1000", label="Full Name", field_type=FormFieldType.TEXT, required=True, category="full_name", selector="input[aria-label*='Name']"),
            FormField(field_id="entry_email", name="entry.1001", label="Email Address", field_type=FormFieldType.EMAIL, required=True, category="email", selector="input[aria-label*='Email']"),
            FormField(field_id="entry_college", name="entry.1002", label="College / University Name", field_type=FormFieldType.TEXT, required=True, category="college", selector="input[aria-label*='College']"),
            FormField(field_id="entry_degree", name="entry.1003", label="Branch / Degree", field_type=FormFieldType.TEXT, required=True, category="degree", selector="input[aria-label*='Degree']"),
            FormField(field_id="entry_grad", name="entry.1004", label="Year of Graduation", field_type=FormFieldType.TEXT, required=True, category="graduation_year", selector="input[aria-label*='Graduation']"),
            FormField(field_id="entry_projects", name="entry.1005", label="Briefly describe your key technical project", field_type=FormFieldType.TEXTAREA, required=True, category="essay", selector="textarea[aria-label*='project']")
        ]
    else:
        # Standard generic job application template
        return [
            FormField(field_id="full_name", name="name", label="Full Name", field_type=FormFieldType.TEXT, required=True, category="full_name", selector="input[name*='name']"),
            FormField(field_id="email", name="email", label="Email", field_type=FormFieldType.EMAIL, required=True, category="email", selector="input[type='email']"),
            FormField(field_id="phone", name="phone", label="Phone", field_type=FormFieldType.TEL, required=True, category="phone", selector="input[type='tel']"),
            FormField(field_id="college", name="college", label="College / University", field_type=FormFieldType.TEXT, category="college", selector="input[name*='college']"),
            FormField(field_id="degree", name="degree", label="Degree / Major", field_type=FormFieldType.TEXT, category="degree", selector="input[name*='degree']"),
            FormField(field_id="linkedin", name="linkedin", label="LinkedIn Profile", field_type=FormFieldType.TEXT, category="linkedin", selector="input[name*='linkedin']"),
            FormField(field_id="github", name="github", label="GitHub Profile", field_type=FormFieldType.TEXT, category="github", selector="input[name*='github']")
        ]


def fetch_and_parse_form(url: str, raw_html: Optional[str] = None) -> Tuple[str, str, List[FormField]]:
    """
    Fetches HTML from URL or uses raw_html to extract form fields.
    Falls back gracefully to platform-specific schemas if network fetch is blocked.
    """
    platform = detect_platform_from_url(url)
    
    if raw_html and raw_html.strip():
        title, fields = extract_form_fields_from_html(raw_html, base_url=url)
        if fields:
            return title, platform, fields

    # Attempt live HTTP fetch
    try:
        with httpx.Client(timeout=8.0, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                title, fields = extract_form_fields_from_html(resp.text, base_url=url)
                has_app_fields = any(f.category in ("email", "first_name", "full_name", "resume_upload") for f in fields)
                if fields and has_app_fields:
                    return title, platform, fields
    except Exception as e:
        logger.debug("Live fetch notice for %s: %s (using platform fallback)", url, str(e))

    # Fallback to high-fidelity platform template
    fallback_fields = generate_platform_fallback_fields(platform)
    title = f"{platform} Application Form"
    return title, platform, fallback_fields
