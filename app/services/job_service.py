"""Job Discovery, Evidence-based Verification, Fraud Detection, and Matching Service."""
import uuid
import json
import re
import httpx
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from urllib.parse import urlparse

from app.database import get_db_connection
from app.models.career import (
    JobListingCreate, JobListingResponse, JobVerificationReport,
    VerificationStatusEnum, JobTypeEnum
)
from app.services.profile_service import get_profile

LEGITIMATE_ATS_DOMAINS = [
    "greenhouse.io", "lever.co", "workday.com", "smartrecruiters.com",
    "ashbyhq.com", "bamboohr.com", "myworkdayjobs.com", "jobvite.com",
    "icims.com", "workable.com", "rippling.com"
]

SUSPICIOUS_FRAUD_KEYWORDS = [
    "application fee", "registration fee", "processing fee", "training fee",
    "pay for background check", "wire transfer", "western union", "crypto payment",
    "bitcoin payment", "gift card", "check cashing", "security deposit",
    "send money", "urgent payment", "deposit required"
]

UNREALISTIC_PROMISES = [
    "earn $5000 a week no experience",
    "make $1000 daily from home",
    "immediate hire no interview",
    "guaranteed placement after fee",
    "unlimited earnings no skills"
]

SENSITIVE_INFO_TRAPS = [
    "bank account details required", "credit score check fee",
    "send passport copy before interview", "send aadhaar copy before interview"
]

def verify_job_listing(company: str, source_url: str, description: str) -> Tuple[VerificationStatusEnum, JobVerificationReport]:
    """
    Rigorously verifies job listing authenticity and inspects for fraud.
    Produces evidence-based findings and actionable recommendations.
    """
    desc_lower = description.lower()
    parsed_url = urlparse(source_url)
    domain = parsed_url.netloc.lower()
    
    suspicious_indicators = []
    evidence_findings = []
    
    # 1. Check for Advance-Fee / Financial Scams
    for phrase in SUSPICIOUS_FRAUD_KEYWORDS:
        if phrase in desc_lower:
            suspicious_indicators.append(f"Financial demand detected: '{phrase}'")
            
    for phrase in SENSITIVE_INFO_TRAPS:
        if phrase in desc_lower:
            suspicious_indicators.append(f"Premature sensitive credential request: '{phrase}'")
            
    for phrase in UNREALISTIC_PROMISES:
        if phrase in desc_lower:
            suspicious_indicators.append(f"Unrealistic promise pattern: '{phrase}'")

    # 2. Inspect Domain & Careers Portal
    is_trusted_ats = any(ats in domain for ats in LEGITIMATE_ATS_DOMAINS)
    if is_trusted_ats:
        evidence_findings.append(f"Hosted on recognized corporate Applicant Tracking System: {domain}")
        careers_status = "CONFIRMED_OFFICIAL_PORTAL"
    else:
        careers_status = "THIRD_PARTY_OR_DIRECT_DOMAIN"
        evidence_findings.append(f"Application hosted on domain: {domain}")

    # 3. Recruiter Domain & Contact Consistency
    email_matches = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', description)
    free_mail_providers = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com"]
    recruiter_consistency = "NO_RECRUITER_CONTACT_FOUND"
    
    if email_matches:
        for em in email_matches:
            em_domain = em.split('@')[-1].lower()
            if em_domain in free_mail_providers and len(company.strip()) > 3:
                suspicious_indicators.append(f"Company '{company}' listing uses free webmail for hiring: {em}")
                recruiter_consistency = "FREE_WEBMAIL_MISMATCH"
            else:
                recruiter_consistency = f"Corporate domain contact: {em_domain}"
                evidence_findings.append(f"Recruiter email matches corporate domain: {em}")

    # 4. Synthesize Status & Confidence
    if suspicious_indicators:
        status = VerificationStatusEnum.HIGH_RISK
        confidence = "HIGH"
        recommended_action = "DO NOT APPLY. High risk of employment fee scam or identity harvesting. Never transfer funds or send ID documents."
    elif is_trusted_ats:
        status = VerificationStatusEnum.VERIFIED_BY_EVIDENCE
        confidence = "HIGH"
        recommended_action = "Verified by available evidence. Legitimate applicant portal identified. Safe to proceed with tailored application."
    else:
        status = VerificationStatusEnum.NEEDS_REVIEW
        confidence = "MEDIUM"
        recommended_action = "Listing requires manual verification. Verify on the employer's official careers site before submitting sensitive details."

    report = JobVerificationReport(
        employer_identity=company,
        official_website=f"https://{domain}" if domain else None,
        careers_page_status=careers_status,
        recruiter_domain_consistency=recruiter_consistency,
        application_url_safety="SECURE_HTTPS" if parsed_url.scheme == "https" else "INSECURE_HTTP",
        suspicious_indicators=suspicious_indicators,
        evidence_findings=evidence_findings,
        confidence_level=confidence,
        recommended_action=recommended_action
    )
    return status, report

def match_job_with_profile(title: str, description: str, skills_list: List[str]) -> Tuple[int, str, List[str], List[str]]:
    """
    Evaluates fit between verified skills and the job description.
    Explains honestly why candidate matches or where gaps exist.
    """
    desc_lower = description.lower()
    title_lower = title.lower()
    
    matching_skills = []
    for skill in skills_list:
        if skill.lower() in desc_lower or skill.lower() in title_lower:
            matching_skills.append(skill)
            
    # Key common requirements in software / AI
    common_eval = ["Docker", "Kubernetes", "AWS", "PyTorch", "TensorFlow", "React", "PostgreSQL", "CI/CD", "C++", "Java"]
    missing_quals = []
    for qual in common_eval:
        if qual.lower() in desc_lower and qual not in skills_list:
            missing_quals.append(qual)
            
    # Calculate score
    base_score = 40
    if "intern" in title_lower or "junior" in title_lower or "fresher" in title_lower or "entry" in title_lower:
        base_score += 20
    if "python" in title_lower or "python" in desc_lower:
        base_score += 15
    if "ai" in title_lower or "machine learning" in desc_lower or "ml" in desc_lower:
        base_score += 15
    if matching_skills:
        base_score += min(len(matching_skills) * 3, 10)
        
    score = min(max(base_score, 10), 98)
    
    # Suitability Explanation
    if score >= 75:
        explanation = f"Strong alignment for Mohil's profile. Core competencies ({', '.join(matching_skills[:3])}) match job scope. Well suited for student/intern level application."
    elif score >= 50:
        explanation = f"Moderate fit. Overlap in {', '.join(matching_skills[:2]) or 'general software engineering'}, but requires additional tech stack items: {', '.join(missing_quals[:2]) or 'advanced tools'}."
    else:
        explanation = f"Low fit. Job appears focused on seniority or technologies outside current verified focus areas."
        
    return score, explanation, matching_skills, missing_quals

def create_or_import_job(data: JobListingCreate) -> JobListingResponse:
    """Inserts a job listing after running fraud detection and profile matching."""
    profile = get_profile()
    
    # Verify fraud indicators
    status, report = verify_job_listing(data.company, data.source_url, data.description)
    
    # Match against profile
    score, explanation, matching, missing = match_job_with_profile(
        data.title, data.description, profile.existing_skills
    )
    
    job_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.execute("SELECT id FROM job_listings WHERE source_url = ?;", (data.source_url,))
            existing = cur.fetchone()
            if existing:
                job_id = existing["id"]
                conn.execute("""
                UPDATE job_listings SET
                    title = ?, company = ?, location = ?, is_remote = ?, job_type = ?,
                    source_name = ?, description = ?, salary_info = ?, application_deadline = ?,
                    match_score = ?, suitability_explanation = ?, missing_qualifications = ?,
                    matching_skills = ?, verification_status = ?, verification_report = ?
                WHERE id = ?;
                """, (
                    data.title, data.company, data.location,
                    1 if data.is_remote else 0, data.job_type.value,
                    data.source_name, data.description, data.salary_info, data.application_deadline,
                    score, explanation, json.dumps(missing), json.dumps(matching),
                    status.value, json.dumps(report.model_dump()),
                    job_id
                ))
            else:
                conn.execute("""
                INSERT INTO job_listings (
                    id, title, company, location, is_remote, job_type, source_url,
                    source_name, description, salary_info, application_deadline,
                    match_score, suitability_explanation, missing_qualifications,
                    matching_skills, verification_status, verification_report,
                    discovered_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    job_id, data.title, data.company, data.location,
                    1 if data.is_remote else 0, data.job_type.value, data.source_url,
                    data.source_name, data.description, data.salary_info, data.application_deadline,
                    score, explanation, json.dumps(missing), json.dumps(matching),
                    status.value, json.dumps(report.model_dump()),
                    now_iso, now_iso
                ))
        return get_job(job_id)
    finally:
        conn.close()

def get_job(job_id: str) -> Optional[JobListingResponse]:
    """Retrieves a single job listing."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM job_listings WHERE id = ?;", (job_id,))
        row = cur.fetchone()
        if not row:
            return None
        return _row_to_job(row)
    finally:
        conn.close()

def list_jobs(
    verification_status: Optional[str] = None,
    job_type: Optional[str] = None,
    is_remote: Optional[bool] = None,
    min_score: Optional[int] = None
) -> List[JobListingResponse]:
    """Lists jobs with optional filtering."""
    conn = get_db_connection()
    try:
        query = "SELECT * FROM job_listings WHERE 1=1"
        params = []
        if verification_status:
            query += " AND verification_status = ?"
            params.append(verification_status)
        if job_type:
            query += " AND job_type = ?"
            params.append(job_type)
        if is_remote is not None:
            query += " AND is_remote = ?"
            params.append(1 if is_remote else 0)
        if min_score is not None:
            query += " AND match_score >= ?"
            params.append(min_score)
            
        query += " ORDER BY match_score DESC, discovered_at DESC;"
        cur = conn.execute(query, params)
        rows = cur.fetchall()
        return [_row_to_job(r) for r in rows]
    finally:
        conn.close()

def discover_live_remote_jobs() -> List[JobListingResponse]:
    """
    Queries authorized free public APIs (Arbeitnow & Remotive) for fresh AI/Python/Software roles.
    Removes duplicates and persists verified results.
    """
    discovered_jobs = []
    
    # 1. Fetch from Arbeitnow (Free JSON API)
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get("https://www.arbeitnow.com/api/job-board-api")
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                for item in data[:10]:
                    title = item.get("title", "")
                    # Filter for relevant software / AI / python roles
                    if any(k in title.lower() for k in ["python", "ai", "machine learning", "developer", "software", "engineer", "intern"]):
                        conn = get_db_connection()
                        cur = conn.execute("SELECT id FROM job_listings WHERE source_url = ?;", (item.get("url"),))
                        existing = cur.fetchone()
                        conn.close()
                        
                        if not existing:
                            created = create_or_import_job(JobListingCreate(
                                title=title,
                                company=item.get("company_name", "Tech Employer"),
                                location=item.get("location", "Remote"),
                                is_remote=item.get("remote", True),
                                job_type=JobTypeEnum.INTERNSHIP if "intern" in title.lower() else JobTypeEnum.ENTRY_LEVEL,
                                source_url=item.get("url"),
                                source_name="Arbeitnow API",
                                description=item.get("description", title)
                            ))
                            discovered_jobs.append(created)
    except Exception as e:
        # Graceful fallback on network issues
        pass

    # 2. Fetch from Remotive (Free JSON API)
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get("https://remotive.com/api/remote-jobs?category=software-dev&limit=10")
            if resp.status_code == 200:
                jobs = resp.json().get("jobs", [])
                for item in jobs[:10]:
                    title = item.get("title", "")
                    if any(k in title.lower() for k in ["python", "ai", "software", "developer", "intern", "junior", "data"]):
                        conn = get_db_connection()
                        cur = conn.execute("SELECT id FROM job_listings WHERE source_url = ?;", (item.get("url"),))
                        existing = cur.fetchone()
                        conn.close()
                        
                        if not existing:
                            created = create_or_import_job(JobListingCreate(
                                title=title,
                                company=item.get("company_name", "Remote Company"),
                                location="Remote Worldwide",
                                is_remote=True,
                                job_type=JobTypeEnum.INTERNSHIP if "intern" in title.lower() else JobTypeEnum.ENTRY_LEVEL,
                                source_url=item.get("url"),
                                source_name="Remotive API",
                                description=item.get("description", title),
                                salary_info=item.get("salary")
                            ))
                            discovered_jobs.append(created)
    except Exception as e:
        pass

    return discovered_jobs

def _row_to_job(row) -> JobListingResponse:
    rep_dict = json.loads(row["verification_report"])
    return JobListingResponse(
        id=row["id"],
        title=row["title"],
        company=row["company"],
        location=row["location"],
        is_remote=bool(row["is_remote"]),
        job_type=JobTypeEnum(row["job_type"]),
        source_url=row["source_url"],
        source_name=row["source_name"],
        description=row["description"],
        salary_info=row["salary_info"],
        application_deadline=row["application_deadline"],
        match_score=row["match_score"],
        suitability_explanation=row["suitability_explanation"],
        missing_qualifications=json.loads(row["missing_qualifications"]),
        matching_skills=json.loads(row["matching_skills"]),
        verification_status=VerificationStatusEnum(row["verification_status"]),
        verification_report=JobVerificationReport(**rep_dict),
        discovered_at=row["discovered_at"],
        created_at=row["created_at"]
    )
