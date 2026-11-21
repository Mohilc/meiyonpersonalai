"""Pydantic models for Autonomous Form and Link Autofill Engine."""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FormFieldType(str, Enum):
    TEXT = "TEXT"
    EMAIL = "EMAIL"
    TEL = "TEL"
    TEXTAREA = "TEXTAREA"
    SELECT = "SELECT"
    RADIO = "RADIO"
    CHECKBOX = "CHECKBOX"
    FILE = "FILE"
    DATE = "DATE"
    NUMBER = "NUMBER"
    UNKNOWN = "UNKNOWN"


class FormField(BaseModel):
    """Represents an extracted input field from a web form."""
    field_id: Optional[str] = None
    name: Optional[str] = None
    label: str
    placeholder: Optional[str] = None
    field_type: FormFieldType = FormFieldType.TEXT
    options: List[str] = Field(default_factory=list)
    required: bool = False
    category: str = "general"  # contact, education, links, essay, work_auth, general
    selector: str = ""


class FilledFormField(BaseModel):
    """Represents a matched and populated form field with trust telemetry."""
    field: FormField
    suggested_value: str
    confidence: float = 1.0  # 0.0 to 1.0
    source: str = "profile"  # profile, resume, ai_generated, default
    selector: str


class AutofillRequest(BaseModel):
    """Payload to request automated form parsing and answer generation."""
    url: str
    raw_html: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    custom_notes: Optional[str] = None


class FormAutofillResult(BaseModel):
    """Comprehensive autofill package including field mappings, bookmarklet, and automation script."""
    url: str
    title: str
    detected_platform: str  # Greenhouse, Lever, Google Forms, Ashby, Workday, Generic
    total_fields: int
    filled_count: int
    fill_percentage: float
    filled_fields: List[FilledFormField]
    unfilled_fields: List[FormField] = Field(default_factory=list)
    javascript_bookmarklet: str
    playwright_script: str
    staged_for_review: bool = True
    summary: str


class AutofillExecuteRequest(BaseModel):
    """Request to execute headless browser form filling via Playwright."""
    url: str
    field_values: Dict[str, str] = Field(default_factory=dict)
    take_screenshot: bool = True
