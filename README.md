# Personal AI Manager

A modular, production-ready Executive Personal AI Manager architected for **Mohil** (B.Tech in Computer Science with Artificial Intelligence at Mar Baselios Christian College of Engineering & Technology, Kuttikkanam, Class of 2027) to manage career planning, job discovery & fraud detection, communications, schedules, persistent memory, and safe autonomous task execution.

---

## 1. System Architecture & Safety Model

- **Operating System**: Windows laptop (Local Timezone: `Asia/Kolkata`)
- **Backend Core**: Python 3.11 with FastAPI, Pydantic v2, and APScheduler
- **Package Management**: `uv` (fast, isolated virtual environment)
- **Persistence Engine**: SQLite in Write-Ahead Logging (`WAL`) mode with automatic point-in-time snapshot backups and restores
- **Autonomy Safety Guardrails**:
  - **Mode A (Assisted)**: Agent plans and drafts actions; halts and requests human authorization before performing external communications or submissions.
  - **Mode B (Supervised)**: Automatically executes internal low-risk tasks (indexing, parsing, checking deadlines); requires approval for external actions.
  - **Mode C (Restricted Autonomy)**: Executes pre-approved routine tasks within strict rate limits.
  - **Audit Logging**: Every action, status change, and approval decision is recorded in an immutable audit table.

```
       ┌────────────────────────────────────────────────────────┐
       │     Executive Web Dashboard (Dark Glassmorphism SPA)    │
       └───────────────────────────┬────────────────────────────┘
                                   │ HTTP / JSON
       ┌───────────────────────────▼────────────────────────────┐
       │                      FastAPI Router                    │
       ├──────────────┬──────────────┬──────────────┬───────────┤
       │ Briefing API │  Tasks API   │  Career API  │ Comms API │
       └──────┬───────┴──────┬───────┴──────┬───────┴─────┬─────┘
              │              │              │             │
       ┌──────▼──────────────▼──────────────▼─────────────▼─────┐
       │               Services & Safety Gate Layer             │
       │  • Daily & Weekly Briefing Synthesizer                 │
       │  • Task & Reminder Engine (APScheduler)                │
       │  • Evidence-based Fraud Detector (Advance Fee / Scams) │
       │  • Factual Resume Tailoring & ATS Gap Analyzer         │
       │  • Email Triage & Prompt Injection Sanitizer           │
       │  • Permitted LinkedIn Career Assistant                 │
       │  • Approval Gate (Human-In-The-Loop Authorizations)    │
       └───────────────────────────┬────────────────────────────┘
                                   │ WAL Mode
       ┌───────────────────────────▼────────────────────────────┐
       │          SQLite Storage (manager.db + Backups)         │
       └────────────────────────────────────────────────────────┘
```

---

## 2. Directory Structure

```
agenticai/
├── app/
│   ├── api/
│   │   ├── routes_approvals.py       # Security gates & audit trail API
│   │   ├── routes_briefing.py        # Executive daily briefing API
│   │   ├── routes_career.py          # Jobs, fraud check, resumes, & applications API
│   │   ├── routes_communication.py   # Email triage, LinkedIn assistant, & weekly reports API
│   │   ├── routes_profile.py         # Verified user profile API
│   │   ├── routes_reminders.py       # Reminder scheduling, triggers, & snooze API
│   │   ├── routes_system.py          # Backups, restore, health, & autonomy mode API
│   │   └── routes_tasks.py           # Full Task CRUD API
│   ├── models/
│   │   ├── approval.py               # Approval requests & audit log schemas
│   │   ├── briefing.py               # Daily briefing schema
│   │   ├── career.py                 # Jobs, fraud reports, resumes, & applications schemas
│   │   ├── communication.py          # Emails, phishing, LinkedIn, & weekly report schemas
│   │   ├── profile.py                # User profile schema
│   │   └── task.py                   # Tasks & reminders schemas
│   ├── services/
│   │   ├── audit_service.py          # Security logging & approval workflows
│   │   ├── briefing_service.py       # Daily priority ranking & executive summary generator
│   │   ├── communication_service.py  # Email triage, injection defense, & LinkedIn assistant
│   │   ├── job_service.py            # Job discovery, evidence-based fraud detection, & matching
│   │   ├── profile_service.py        # Profile storage & persistent memory
│   │   ├── reminder_service.py       # Delivery tracker, background trigger, & snooze
│   │   ├── resume_service.py         # Factual resume tailoring, ATS gap analysis, & applications
│   │   └── task_service.py           # Task lifecycle & persistence
│   ├── static/
│   │   ├── css/style.css             # Glassmorphic dark theme CSS design system
│   │   ├── js/app.js                 # SPA frontend logic & live updates
│   │   └── index.html                # Executive web dashboard
│   ├── config.py                     # Pydantic Settings & environment config
│   ├── database.py                   # SQLite WAL connection, migrations, seeds, backups
│   └── main.py                       # FastAPI entrypoint, lifespan, background scheduler
├── data/                             # SQLite database (manager.db) & point-in-time backups
├── tests/
│   ├── test_api.py                   # FastAPI TestClient endpoint tests
│   ├── test_approvals.py             # Security gate & audit logging tests
│   ├── test_briefing.py              # Daily briefing & timezone tests
│   ├── test_career.py                # Fraud detection, resume tailoring, & application tests
│   ├── test_communication.py         # Prompt injection defense, phishing, & LinkedIn tests
│   ├── test_database.py              # WAL mode, seeding, backup/restore tests
│   ├── test_reminders.py             # Delivery tracking & snooze tests
│   └── test_tasks.py                 # Task CRUD & confirmed vs inferred tests
├── run.ps1                           # Windows PowerShell one-click launcher
└── README.md
```

---

## 3. Key Capabilities & Implemented Modules

### A. Job Search & Evidence-Based Fraud Detection
- **Permitted Free Live APIs**: Discovers remote and software engineering roles from Arbeitnow and Remotive APIs without paid API keys.
- **Evidence-Based Verification**: Inspects application URLs and company domains against recognized Applicant Tracking Systems (`greenhouse.io`, `lever.co`, `workday.com`, `smartrecruiters.com`, `ashbyhq.com`, etc.).
- **Fraud & Scam Detection**:
  - Flags advance-fee scams, mandatory background check fees, equipment check cashing, wire transfers, and crypto payment demands as **HIGH RISK**.
  - Identifies recruiter email domain inconsistencies (e.g. corporate hiring claimed from free webmail accounts like `@gmail.com`).
  - Classifies listings into `VERIFIED_BY_EVIDENCE`, `NEEDS_REVIEW`, or `HIGH_RISK`.
- **Profile Matching**: Compares job description against verified profile competencies, calculates fit score (0-100%), and produces an honest explanation of suitability and skill gaps.

### B. Resume Studio & Application Management
- **100% Factual Integrity**: Strictly preserves verified facts (B.Tech AI at Mar Baselios Christian College '27, autonomous drone systems, executive agentic AI). Never invents commercial employment or fake qualifications.
- **Contextual Tailoring**: Re-orders project highlights and skills based on relevance to the specific role.
- **ATS Keyword Gap Analysis**: Highlights matching keywords and identifies missing technologies without artificial keyword stuffing.
- **Application Tracking**: Tracks company, role, stage history (`DRAFTED`, `READY_FOR_APPROVAL`, `SUBMITTED`, `INTERVIEW_SCHEDULED`, `OFFER`, `REJECTED`), follow-up dates, and recruiter details.
- **Human Authorization Gate**: Submitting applications requires explicit user authorization via the security gate.

### C. Email & Recruiter Triage (with Prompt-Injection Defense)
- **Prompt Injection Neutralization**: Sanitizes untrusted incoming email content, blocking prompt overrides (`ignore previous instructions`, `developer mode`, `reveal secrets`).
- **Phishing & Scam Classifier**: Flags employment scams and fake hiring attempts.
- **Intent Detection**: Classifies messages into `INTERVIEW`, `OFFER`, `REJECTION`, `INFO_REQUEST`, or `GENERAL`.
- **Date Extraction**: Extracts meeting and deadline dates, distinguishing confirmed appointments from suggested/inferred times.
- **Draft Replies with Approval Gate**: Drafts professional responses, requiring user approval before any external message transmission.

### D. Permitted LinkedIn Career Assistant
- Generates polished, professional headline and About section drafts tailored to Mohil's academic profile.
- Contextual, authentic post drafts highlighting learnings from drone systems and agentic AI.
- Personalized connection request notes strictly under LinkedIn's 300-character limit.

### E. Schedule, Reminders & Executive Reporting
- **Timezone Awareness**: Configured for `Asia/Kolkata` (UTC+05:30).
- **Daily Briefing**: Synthesizes top 3 focus priorities, upcoming deadlines, overdue tasks, active reminders, and items awaiting approval.
- **Weekly Executive Report**: Summarizes completed tasks, discovered opportunities, application progress, and recommended focus areas for the upcoming week.
- **Active Reminders Engine**: Automatically checks for due reminders in the background every 60 seconds, recording honest delivery timestamps, snooze counts, and escalation status.

---

## 4. Quick Start & Operation

### Start the Manager
Run the PowerShell launcher script:
```powershell
.\run.ps1
```

Or start manually with the virtual environment:
```powershell
.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Executive Web Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Run Automated Tests
```powershell
.venv\Scripts\pytest -v
```
All **21 automated tests pass** covering persistence, backup/restore cycles, reminder delivery tracking, briefing generation, job fraud detection, ATS tailoring, prompt injection defense, and REST endpoints.
