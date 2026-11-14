---
title: Meiyon - Executive Personal AI Manager
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: gradio
app_file: app.py
pinned: false
license: mit
---

<div align="center">

# 🚀 Meiyon - Executive Personal AI Manager
### Autonomous Career Intelligence, Academic Copilot, Self-Learning Memory, Zapier MCP & Supabase Cloud Persistence

![Meiyon Executive Hero Banner](https://raw.githubusercontent.com/Mohilc/meiyonpersonalai/main/assets/meiyon_hero.png)

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Zapier MCP](https://img.shields.io/badge/Zapier%20MCP-Gmail%20%7C%20LinkedIn%20%7C%20Tasks-FF4F00?style=for-the-badge&logo=zapier&logoColor=white)](https://zapier.com)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.3.0-6366F1?style=for-the-badge&logo=anthropic&logoColor=white)](https://modelcontextprotocol.io)
[![Supabase](https://img.shields.io/badge/Supabase-Cloud%20Storage%20%26%20Persistence-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)
[![Self-Learning](https://img.shields.io/badge/Self--Learning-Adaptive%20Persona%20Memory-8B5CF6?style=for-the-badge&logo=openai&logoColor=white)](https://github.com/Mohilc/meiyonpersonalai)
[![Academic Tracker](https://img.shields.io/badge/Academic%20Tracker-Attendance%20%7C%20Absences%20%7C%20PDF-EC4899?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](https://github.com/Mohilc/meiyonpersonalai)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA%20NIM-DiffusionGemma%20%7C%20Nemotron%20OCR%20v2-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://build.nvidia.com)
[![SQLite WAL](https://img.shields.io/badge/SQLite-WAL%20Mode-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Tests Passing](https://img.shields.io/badge/Tests-71%20Passed%20(100%25)-10B981?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)
[![Telegram Bot](https://img.shields.io/badge/Telegram-@Meiyon__ai__bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/Meiyon_ai_bot)
[![WhatsApp Chat](https://img.shields.io/badge/WhatsApp-Twilio%20API-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://twilio.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)](LICENSE)

*Architected specifically for **Mohil** (B.Tech in Computer Science with Artificial Intelligence at Mar Baselios Christian College of Engineering & Technology, Class of 2027) to manage career planning, job discovery & fraud detection, verified communications, college attendance tracking, self-learning persona adaptation, persistent cloud storage via Supabase, Model Context Protocol (MCP) integrations with Zapier, and safe autonomous task execution.*

</div>

---

## 📸 Executive Web Dashboard Interface

The Personal AI Manager features a high-performance Dark Glassmorphism interface connected in real-time to the FastAPI backend, SQLite WAL engine, Supabase Cloud Storage, and local & cloud MCP servers.

![Executive AI Dashboard Preview](https://raw.githubusercontent.com/Mohilc/meiyonpersonalai/main/assets/dashboard_preview.jpg)

---

## 📑 Table of Contents
1. [Executive Summary & Core Mission](#1-executive-summary--core-mission)
2. [End-to-End System Architecture](#2-end-to-end-system-architecture)
3. [Model Context Protocol (MCP 2.x) & Zapier Ecosystem](#3-model-context-protocol-mcp-2x--zapier-ecosystem)
   - [A. Zapier Tasks & Important Data Server (`02292b48`)](#a-zapier-tasks--important-data-server-02292b48)
   - [B. Zapier Gmail MCP Server (`02750b42`)](#b-zapier-gmail-mcp-server-02750b42)
   - [C. Zapier LinkedIn MCP Server (`029df438`)](#c-zapier-linkedin-mcp-server-029df438)
   - [D. Dual-Mode Execution & Fallback Resilience](#d-dual-mode-execution--fallback-resilience)
4. [Deep Dive: How the Agentic Model Works](#4-deep-dive-how-the-agentic-model-works)
   - [A. The Six-Stage Cognitive Loop](#a-the-six-stage-cognitive-loop)
   - [B. Multi-Factor Evidence-Based Fraud Detection Pipeline](#b-multi-factor-evidence-based-fraud-detection-pipeline)
   - [C. Autonomy Modes & Human-In-The-Loop (HITL) Security Gates](#c-autonomy-modes--human-in-the-loop-hitl-security-gates)
   - [D. Factual ATS Resume Studio & Zero-Hallucination Invariant](#d-factual-ats-resume-studio--zero-hallucination-invariant)
   - [E. Mathematical Scoring & Priority Models](#e-mathematical-scoring--priority-models)
   - [F. NVIDIA NIM Multi-Model Pool & Nemotron OCR v2](#f-nvidia-nim-multi-model-pool--nemotron-ocr-v2)
5. [Academic Attendance, Absence Logging & PDF Reports](#5-academic-attendance-absence-logging--pdf-reports)
6. [Self-Learning Engine & Adaptive Persona Memory](#6-self-learning-engine--adaptive-persona-memory)
7. [Supabase Cloud Storage & Database Persistence](#7-supabase-cloud-storage--database-persistence)
8. [Mobile Messaging & Dual-Channel Executive AI (Telegram & WhatsApp)](#8-mobile-messaging--dual-channel-executive-ai-telegram--whatsapp)
   - [A. Interactive Command Matrix](#a-interactive-command-matrix)
   - [B. Two-Way Multi-Turn Dialogue & Persona Continuity](#b-two-way-multi-turn-dialogue--persona-continuity)
9. [Cybersecurity & Threat Defense System](#9-cybersecurity--threat-defense-system)
10. [Complete Repository Structure](#10-complete-repository-structure)
11. [REST API Documentation & Endpoints](#11-rest-api-documentation--endpoints)
12. [Setup, Quick Start & Operations](#12-setup-quick-start--operations)

---

## 1. Executive Summary & Core Mission

Early-career engineers and computer science students face severe friction in balancing academic requirements, job discovery, recruiter communications, and schedule prioritization. Concurrently, recruitment scams, check-cashing fraud, phishing attacks, and prompt-injection vulnerabilities pose acute cybersecurity risks.

The **Executive Personal AI Manager** provides a hardened, local-first autonomous agent platform that solves these challenges through:
1. **Ultra-Low Latency Multi-Model Pool**: Powered by NVIDIA NIM with `google/diffusiongemma-26b-a4b-it` delivering sub-second (~0.6s - 1.3s) conversational copilot responses, backed by `nvidia/nemotron-3-super-120b-a12b` for deep strategic reasoning and high-throughput fallback.
2. **Model Context Protocol (MCP 2.x) with Zapier Cloud Bridge**: Full dual-mode integration with Zapier MCP servers for **Tasks & Important Notes** (`02292b48-0fbd-8ca5-88c8-021274846b43`), **Gmail Inboxes** (`02750b42-81d6-8595-a28c-9aaadc202a9f`), and **LinkedIn Platform** (`029df438-e88c-8c07-8d68-61978ee0976a`).
3. **Academic Attendance & Absence Tracker**: Real-time logging of classes (`/present <subject>`, `/absent <subject>`), assignment submission tracking, and automated 75% college compliance alerts with instant ReportLab PDF report generation delivered to Telegram and cloud.
4. **Self-Learning & Adaptive Persona Engine**: Dynamic SQLite memory bank (`learned_memories`) that learns user preferences and tone requests in real-time ("Be more friendly", "Call me bro", "Don't use corporate speak"), dynamically shaping both LLM generation and fallback responses.
5. **Supabase Cloud Persistence & Document Storage**: Automated database backups every 6 hours (`backups/latest.db` and timestamped snapshots) to Supabase Storage, preserving state across stateless Render deployments, plus permanent public cloud links for generated PDFs.
6. **24/7 Cloud Keep-Alive System**: Background self-pinger hitting health endpoints every 10 minutes to prevent Render free-tier instances from falling asleep.
7. **Zero-Trust Input Sanitization**: Active adversarial payload stripping and prompt-injection neutralization before text reaches reasoning models or databases.
8. **Evidence-Based Job Scam Detection**: Mathematical scoring against verified ATS domains (`greenhouse.io`, `lever.co`, `workday.com`, `ashbyhq.com`) to flag fraudulent solicitations.
9. **Human-In-The-Loop (HITL) Security Gates**: Strict authorization barriers preventing unauthorized outbound transmissions without explicit human confirmation.
10. **Dual-Channel Mobile Access (Telegram & WhatsApp)**: Full executive co-pilot capability via Telegram (`@Meiyon_ai_bot`) and WhatsApp (Twilio Webhooks & Content Template API).

---

## 2. End-to-End System Architecture

```mermaid
graph TD
    User([Executive User / Mohil]) <-->|Telegram / WhatsApp / Web| Gateway[FastAPI Router Gateway]
    
    subgraph "FastAPI Application Core"
        Gateway <--> SafetyGate[Security & Human-In-The-Loop Gate Layer]
        
        SafetyGate <--> AcademicSvc[Academic Attendance & Absence Tracker]
        SafetyGate <--> LearningSvc[Self-Learning & Adaptive Persona Memory]
        SafetyGate <--> SupabaseSvc[Supabase Cloud Persistence & Storage]
        SafetyGate <--> CommSvc[Email Triage & LinkedIn Assistant]
        SafetyGate <--> CareerSvc[Job Fraud Scanner & ATS Tailoring]
        SafetyGate <--> TaskSvc[Task Lifecycle & Reminder Engine]
        SafetyGate <--> MCPSvc[MCP Orchestration Client]
    end

    subgraph "Persistent Storage & Cloud Tier"
        SafetyGate <--> DB[(SQLite manager.db with WAL)]
        SupabaseSvc <-->|S3-Compatible HTTPS| SupabaseCloud[(Supabase Storage: meiyon-storage)]
        SupabaseCloud <--> CloudBackups[(backups/latest.db Snapshot)]
        SupabaseCloud <--> CloudReports[(reports/academic/*.pdf)]
    end

    subgraph "Model Context Protocol (MCP 2.x) Execution Bridge"
        MCPSvc <--> TaskBridge[Task & Notes MCP Server]
        MCPSvc <--> GmailBridge[Gmail MCP Server]
        MCPSvc <--> LinkedInBridge[LinkedIn MCP Server]
        
        TaskBridge <-->|HTTP SSE / Stdio| ZapierTasks[Zapier Tasks MCP: 02292b48]
        GmailBridge <-->|HTTP SSE / IMAP| ZapierGmail[Zapier Gmail MCP: 02750b42]
        LinkedInBridge <-->|HTTP SSE / Playwright| ZapierLinkedIn[Zapier LinkedIn MCP: 029df438]
    end

    ZapierTasks -.->|Fallback| DB
    ZapierGmail -.->|Fallback| GmailAPI[(Gmail Inboxes)]
    ZapierLinkedIn -.->|Fallback| LinkedInWeb[(LinkedIn Web Platform)]
```

### Key Architectural Specifications:
- **Operating Environment**: Cloud (Render / Hugging Face Spaces / Railway) + Windows Local Workstation (`Asia/Kolkata` / UTC+05:30).
- **Backend Core**: Python 3.11, FastAPI (asynchronous high-throughput ASGI), Pydantic v2 schemas.
- **Persistence Layer**: SQLite with Write-Ahead Logging (`WAL` mode) + automated Supabase Cloud Snapshots.
- **Protocol Standard**: Model Context Protocol (MCP 2.x) via FastMCP with both HTTP SSE and Stdio transport.
- **Cloud Storage**: Supabase Storage (`meiyon-storage`) for backups, documents, and public download links.

---

## 3. Model Context Protocol (MCP 2.x) & Zapier Ecosystem

Meiyon implements an enterprise-grade **Model Context Protocol (MCP)** architecture that integrates directly with remote Zapier MCP endpoints while providing instant local fallback to guarantee 100% operational uptime.

### A. Zapier Tasks & Important Data Server (`02292b48`)
- **Server UUID**: `02292b48-0fbd-8ca5-88c8-021274846b43`
- **MCP Endpoint**: `https://mcp.zapier.com/api/mcp/s/02292b48-0fbd-8ca5-88c8-021274846b43/mcp`
- **Capabilities & FastMCP Tools**:
  - `create_task`: Adds structured task commitments with priority levels (`P1_URGENT`, `P2_HIGH`, `P3_NORMAL`), due dates, and descriptive notes.
  - `mark_important_data`: Ingests critical technical rules, project specs, or instructions directly into the AI's long-term memory (`FACTUAL_KNOWLEDGE`) and simultaneously pins them to the urgent priorities list.
  - `list_active_tasks`: Fetches pending commitments ordered by priority.
  - `complete_task`: Marks tasks finished by full ID or convenient 8-character prefix.
- **Commands**: `/task add`, `/tasks`, `/done <id>`, `/important <title>: <content>`.

### B. Zapier Gmail MCP Server (`02750b42`)
- **Server UUID**: `02750b42-81d6-8595-a28c-9aaadc202a9f`
- **MCP Endpoint**: `https://mcp.zapier.com/api/mcp/s/02750b42-81d6-8595-a28c-9aaadc202a9f/mcp`
- **Capabilities & FastMCP Tools**:
  - `list_unread_emails`: Fetches truly recent unread emails, parses RFC 2822 / ISO 8601 dates, strips quoted reply noise, and sorts chronologically.
  - `read_email`: Extracts sanitized plain text body from multipart MIME emails.
  - `draft_email_reply`: Stages drafted professional replies in the Human-in-the-Loop approval gate.
  - `send_email`: Transmits authorized communications via verified SMTP/OAuth transport.
- **Commands**: `/emails`, `/email <1-5>`, `/reply <1-5>`.

### C. Zapier LinkedIn MCP Server (`029df438`)
- **Server UUID**: `029df438-e88c-8c07-8d68-61978ee0976a`
- **MCP Endpoint**: `https://mcp.zapier.com/api/mcp/s/029df438-e88c-8c07-8d68-61978ee0976a/mcp`
- **Capabilities & FastMCP Tools**:
  - `get_linkedin_profile`: Inspects candidate headline, summary, and public profile data.
  - `list_connection_requests`: Checks incoming connection invitations and recruiter reachouts.
  - `send_connection_invite`: Sends personalized notes strictly validated under 300 characters.
  - `like_post` & `comment_on_post`: Automates post engagement and ghostwriting through human approval gates.
- **Commands**: `/linkedin`, `/linkedin sync`, `/linkedin like <id>`, `/linkedin comment <id>`.

### D. Dual-Mode Execution & Fallback Resilience

```mermaid
flowchart LR
    Request["Incoming Tool Request"] --> CheckZapier{"Zapier MCP Available?"}
    CheckZapier -- "Yes" --> RemoteCall["Dispatch HTTP SSE to Zapier MCP"]
    RemoteCall --> Success{"HTTP 200 OK?"}
    Success -- "Yes" --> Result["Return Synced Cloud Result"]
    Success -- "No / Offline" --> LocalFallback["Fall back to Local FastMCP / SQLite WAL"]
    CheckZapier -- "No" --> LocalFallback
    LocalFallback --> Done["Execute Locally with 100% Reliability"]
```

Even during internet disconnects or when Zapier tokens require re-authorization, Meiyon operates seamlessly using its internal SQLite WAL engine and local protocol handlers.

---

## 4. Deep Dive: How the Agentic Model Works

![Agentic AI Cognitive Loop](https://raw.githubusercontent.com/Mohilc/meiyonpersonalai/main/assets/agent_cognition_loop.jpg)

### A. The Six-Stage Cognitive Loop
1. **Perception Layer (Continuous Influx)**: Ingests events from Zapier MCP, Gmail, LinkedIn, Telegram, WhatsApp, and discovered jobs. Uses IMAP `BODY.PEEK[]` and header filtering to prevent altering user inboxes.
2. **Security Firewall & Threat Neutralization**: Strips prompt injections (`ignore previous instructions` &rarr; `[BLOCKED_INJECTION_ATTEMPT]`) and scans for financial scam markers.
3. **Context & Memory Grounding**: Injects verified student profile constraints (Mohil, B.Tech CSE AI '27 at Mar Baselios Christian College) along with real-time learned preferences from SQLite.
4. **Reasoning & Planning (Tree-of-Thought)**: Distinguishes between internal passive analysis and external outbound actions.
5. **Human-In-The-Loop (HITL) Safety Gate**: Stages external actions in the approvals queue; executes only after human authorization.
6. **Execution Layer (MCP Stdio / HTTP)**: Dispatches approved actions through standard I/O (stdio JSON-RPC) or Zapier HTTP endpoints and logs tamper-proof audit trails.

### B. Multi-Factor Evidence-Based Fraud Detection Pipeline
Job postings and recruiter inquiries are evaluated against verified applicant tracking system (ATS) domains (`greenhouse.io`, `lever.co`, `workday.com`, `ashbyhq.com`). Solicitations requesting payment, gift cards, or crypto are immediately flagged as `HIGH_RISK` scams.

### C. Autonomy Modes & Human-In-The-Loop (HITL) Security Gates
Meiyon enforces three strict operating postures:
- **`READ_ONLY`**: The system acts strictly as an analytical observer. Outbound network mutations are prohibited.
- **`SEMI_AUTONOMOUS`** (Default): Passive reading and local memory caching occur autonomously; all outbound side-effects (sending emails, accepting invites, submitting applications) require human confirmation.
- **`AUTONOMOUS_APPROVED_ONLY`**: Pre-cleared low-risk operations execute automatically, while high-risk actions remain gated.

### D. Factual ATS Resume Studio & Zero-Hallucination Invariant
The resume tailoring pipeline dynamically aligns candidate bullet points against technical job requirements. Under no circumstances does the system fabricate credentials, years of experience, or unverified skills. Every bullet is anchored in the verified student profile.

---

## 5. Academic Attendance, Absence Logging & PDF Reports

Meiyon actively monitors college attendance and tracks assignments, ensuring you never fall below the 75% college compliance threshold.

```mermaid
flowchart LR
    A["User Telegram / Web Input"] -->|"'/absent AI' or '/present OS'"| B["Academic Service"]
    B --> C["SQLite Attendance Ledger"]
    B --> D{"Overall Attendance >= 75%?"}
    D -- ">= 75%" --> E["Status Normal"]
    D -- "< 75%" --> F["CRITICAL ATTENDANCE WARNING"]
    B -->|"'/pdf' or '/report'"| G["ReportLab PDF Generator"]
    G --> H["Local PDF Document"]
    H --> I["Supabase Cloud Storage (Public Link)"]
    I --> J["Direct Telegram Document Delivery"]
```

### Academic Features:
- **Attendance Logging**: Mark presence or absence with a single command (`/present Operating Systems`, `/absent Compiler Design | Sick leave`).
- **75% Threshold Alerts**: Calculates subject-wise and overall attendance percentage, highlighting subjects at risk with red warning badges.
- **Assignment Tracker**: Add assignments with due dates (`/assignment add AI | Mini-Project | 2026-11-15`) and record submissions or grades (`/submit <id> 48`).
- **Executive PDF Report Generator**: Compiles an official executive summary report using ReportLab with custom color palettes, subject breakdown tables, absence histories, and assignment status lists.
- **Supabase Cloud Links**: Automatically uploads generated PDFs to Supabase Storage and delivers both the raw PDF document and a cloud download link directly into Telegram.

---

## 6. Self-Learning Engine & Adaptive Persona Memory

Meiyon continuously learns and evolves based on your natural conversation, instructions, and feedback.

```mermaid
flowchart TD
    User["User Chat / Feedback"] --> Parser{"Learning Detector"}
    Parser -->|"Explicit: '/remember Call me bro'"| MemBank["Learned Memory Store (SQLite)"]
    Parser -->|"Conversational: 'Be more friendly & warm'"| MemBank
    Parser -->|"Correction: 'Actually, I use YOLOv8'"| MemBank
    Parser -->|"Important Fact: '/important Drone cutoff: 14.4V'"| MemBank
    MemBank --> Compiler["Dynamic Persona & Context Compiler"]
    Compiler --> LLM["LLM Prompt Engine & Fallback Generator"]
    LLM --> Response["Empathetic, Human-Friendly Response"]
```

### Self-Learning Features:
- **Zero Latency Adaptation**: Modifies behavior instantly using persistent context augmentation—no expensive model fine-tuning required.
- **Natural Conversational Learning**:
  - *"Please be more friendly and warm"* &rarr; Shifts tone to empathetic, supportive, and conversational.
  - *"Call me Mohil bro"* &rarr; Automatically updates preferred name.
  - *"Remember that my lab drone project uses YOLOv8"* &rarr; Persists technical facts permanently.
- **Explicit Memory Commands**:
  - `/memory` (or `/learned`) — Displays all active learned rules and preferences.
  - `/remember <text>` — Explicitly teaches a rule or habit.
  - `/important <Title>: <Content>` — Saves high-priority technical facts directly into long-term memory.
  - `/forget <id or key>` — Soft-deactivates an outdated memory rule.
- **Warm Human-Like Fallbacks**: Even when running without LLM API keys, the fallback engine reads your learned preferences to respond warmly and naturally.

---

## 7. Supabase Cloud Storage & Database Persistence

Designed for stateless cloud hosting (such as Render or Railway free tier), Meiyon uses **Supabase** for zero-loss cloud persistence.

```mermaid
flowchart LR
    LocalDB["Local SQLite (manager.db)"] -->|"Automated Snapshot (Every 6h)"| SupabaseSvc["Supabase Service"]
    SupabaseSvc -->|"Uploads snapshot"| Bucket["Supabase Storage (meiyon-storage)"]
    Bucket --> Latest["backups/latest.db"]
    Bucket --> Archive["backups/manager_backup_YYYYMMDD.db"]
    Bucket --> Reports["reports/academic/*.pdf"]
    Latest -.->|"Auto-restore on container restart"| LocalDB
```

### Cloud Persistence Features:
- **Automated Snapshots**: Performs a thread-safe SQLite `.backup()` every 6 hours and uploads it to Supabase Storage as `backups/latest.db` and timestamped archives.
- **Stateless Cloud Disaster Recovery**: If the Render container restarts or redeploys, Meiyon restores its complete state from `backups/latest.db`.
- **Public Cloud File Hosting**: Generated attendance PDFs and documents are stored in the public `meiyon-storage` bucket, generating permanent, shareable download links.
- **Telegram & API Controls**:
  - `/supabase` — View connection status and stored cloud objects.
  - `/supabase backup` — Trigger an immediate cloud database snapshot.
  - `/supabase restore` — Pull and restore the latest database snapshot.

---

## 8. Mobile Messaging & Dual-Channel Executive AI (Telegram & WhatsApp)

Meiyon acts as an executive chief-of-staff accessible from anywhere via Telegram (`@Meiyon_ai_bot`) and WhatsApp:

### A. Interactive Command Matrix

| Command | Action | Description | Category |
| :--- | :--- | :--- | :--- |
| `/start` | Welcome Guide | Interactive guide displaying all capabilities and quick commands | Core |
| `/briefing` | Daily Briefing | Top 3 priorities, schedule commitments, and strategic AI advice | Core |
| `/tasks` | Task Board | Displays commitments with priority badges (`🔴 URGENT`, `🟡 HIGH`, `🟢 NORMAL`) | Tasks |
| `/task add <Title> [\| Due]` | Add Task | Adds scheduled commitment (synced to Zapier & SQLite WAL) | Tasks |
| `/done <id>` | Complete Task | Marks task finished by full ID or 8-character prefix | Tasks |
| `/important <T>: <C>` | Mark Important | Saves critical fact to long-term memory & pins to P1 urgent briefing | Knowledge |
| `/attendance` | Attendance Overview | Current attendance percentages and subject breakdown | Academic |
| `/present <sub` | Mark Present | Logs class presence (e.g. `/present Operating Systems`) | Academic |
| `/absent <sub` | Mark Absent | Logs absence with notes (e.g. `/absent AI \| Lab setup`) | Academic |
| `/assignments` | List Assignments | View pending, submitted, and graded assignments | Academic |
| `/assignment add`| Add Assignment | Format: `/assignment add <Sub> \| <Title> \| <Due Date>` | Academic |
| `/submit <id> [marks]` | Submit/Grade | Marks assignment submitted or graded (e.g. `/submit a1b2 48`) | Academic |
| `/pdf` or `/report` | Academic PDF | Compiles and delivers official Attendance & Assignment PDF | Academic |
| `/memory` | Learned Persona | View all active self-learned preferences and persona rules | Learning |
| `/remember <text>` | Teach Rule | Explicitly teaches Meiyon a new habit or rule | Learning |
| `/forget <id>` | Delete Rule | Erases or deactivates an outdated learned rule | Learning |
| `/supabase` | Cloud Storage | Check Supabase connection and view stored cloud files | Cloud |
| `/supabase backup` | Cloud Snapshot | Trigger instant SQLite database backup to Supabase | Cloud |
| `/emails` | Live Gmail Inbox | Fetches recent emails via Zapier MCP with security triage | Comms |
| `/email <1-5>` | Read Email Body | Displays full sanitized email body | Comms |
| `/reply <1-5>` | Stage Email Reply | Generates AI draft with Human-in-the-Loop approval gate | Comms |
| `/linkedin` | LinkedIn Activity | Checks connection requests and recruiter communications | Comms |
| `/clear` | Reset Buffer | Resets conversation context buffer for a fresh slate | Utilities |

### B. Two-Way Multi-Turn Dialogue & Persona Continuity
When you speak to Meiyon without slash commands, the system activates a warm, conversational persona grounded in your persistent profile and learned memories:
- Remembers multi-turn context (e.g., asking about an assignment, then asking *"When is it due again?"*).
- Adapts tone dynamically to your preferences (casual, executive, or friendly).

---

## 9. Cybersecurity & Threat Defense System

- **Adversarial Payload Sanitization**: Strips prompt injection attempts before they reach the reasoning engine.
- **Phishing & Financial Fraud Detection**: Scans recruiter solicitations for advance fee fraud, crypto requests, and suspicious free webmail domains.
- **Tamper-Proof Audit Logging**: Every system action, approval decision, and external transmission is written to an immutable SQLite audit log.
- **Human-In-The-Loop Approval Gates**: Outbound transmissions (sending emails, accepting connections, publishing posts) cannot execute without explicit confirmation.

---

## 10. Complete Repository Structure

```
agenticai/
├── .agents/                          # Antigravity IDE Workspace Customizations
│   ├── mcp_config.json               # Registers Zapier Tasks, Gmail & LinkedIn MCP servers
│   └── skills/
│       └── mcp-email-linkedin/
│           └── SKILL.md              # Antigravity tool runbook & safety instructions
├── app/
│   ├── api/                          # REST API Routers
│   │   ├── routes_academic.py        # Attendance, absences, assignments & PDF reports
│   │   ├── routes_approvals.py       # Human authorization gates & audit log
│   │   ├── routes_briefing.py        # Executive daily briefing endpoint
│   │   ├── routes_career.py          # Job discovery, fraud report & resume studio
│   │   ├── routes_communication.py   # Email triage, LinkedIn assistant & MCP sync
│   │   ├── routes_learning.py        # Self-learning engine, memory bank & feedback
│   │   ├── routes_profile.py         # Verified candidate profile & memory
│   │   ├── routes_reminders.py       # Reminder scheduling, triggers & snooze
│   │   ├── routes_supabase.py        # Supabase cloud persistence, backups & files
│   │   ├── routes_system.py          # Point-in-time backups & autonomy mode
│   │   ├── routes_tasks.py           # Task CRUD & commitment verification
│   │   └── routes_webhooks.py        # Telegram & WhatsApp live messaging webhooks
│   ├── models/                       # Pydantic Schemas (v2)
│   │   ├── academic.py               # Attendance, absence & assignment models
│   │   ├── approval.py               # Security gate & audit models
│   │   ├── briefing.py               # Executive summary models
│   │   ├── career.py                 # Job listing & ATS resume models
│   │   ├── communication.py          # Email, LinkedIn & MCP models
│   │   ├── learning.py               # Self-learning memory models & categories
│   │   ├── profile.py                # User profile models
│   │   └── task.py                   # Task & reminder models
│   ├── services/                     # Business Logic & Integrations
│   │   ├── academic_service.py       # Attendance tracking, absences & ReportLab PDF
│   │   ├── audit_service.py          # Security audit trail & gate evaluation
│   │   ├── briefing_service.py       # Priority ranking & executive briefing
│   │   ├── communication_service.py  # Injection sanitizer & recruiter triage
│   │   ├── job_service.py            # Fraud detector & ATS matcher
│   │   ├── learning_service.py       # Dynamic memory bank & tone adaptation
│   │   ├── llm_service.py            # NVIDIA multi-model orchestrator & fallback
│   │   ├── mcp_service.py            # MCP Client orchestrator & sync
│   │   ├── messaging_bot_service.py  # High-speed Telegram & WhatsApp dispatcher
│   │   ├── profile_service.py        # Profile persistence
│   │   ├── reminder_service.py       # Background scheduler & alert delivery
│   │   ├── resume_service.py         # ATS tailoring & application tracking
│   │   ├── supabase_service.py       # Supabase Cloud Storage & database persistence
│   │   └── task_service.py           # Task lifecycle persistence
│   ├── static/                       # Web Dashboard Frontend
│   │   ├── css/style.css             # Dark Glassmorphism design tokens & styles
│   │   ├── js/app.js                 # Single-Page Application logic & live clock
│   │   └── index.html                # Executive Web Dashboard
│   ├── config.py                     # App Settings & environment variables
│   ├── database.py                   # SQLite connection, WAL mode, migrations & seed
│   ├── main.py                       # FastAPI application & scheduler lifecycle
│   └── prompts.py                    # Executive prompts & dynamic memory injection
├── assets/                           # High-Resolution Architectural Graphics
│   ├── meiyon_hero.png               # Ultra-HD Hero Banner
│   ├── architecture_hero.png         # Infographic banner
│   ├── agent_cognition_loop.jpg      # Cognitive architecture workflow
│   └── dashboard_preview.jpg         # Executive dashboard showcase
├── data/                             # SQLite Storage & Reports (git-ignored)
│   ├── manager.db                    # Primary database in WAL mode
│   ├── backups/                      # Snapshot backup archives
│   └── reports/                      # Generated academic PDF reports
├── mcp_servers/                      # Model Context Protocol (FastMCP) Servers
│   ├── task_server.py                # Tasks & Important Data Server (Zapier 02292b48 / SQLite)
│   ├── gmail_server.py               # Gmail MCP server (Zapier 02750b42 / IMAP/SMTP)
│   └── linkedin_server.py            # LinkedIn MCP server (Zapier 029df438 / Playwright)
├── tests/                            # Automated Pytest Suite (71/71 Tests Passing)
│   ├── test_academic.py              # Attendance, absence, assignment & PDF tests (5 tests)
│   ├── test_api.py                   # REST endpoint & dashboard tests (5 tests)
│   ├── test_approvals.py             # Security gate & audit tests (1 test)
│   ├── test_briefing.py              # Briefing & priority ranking tests (1 test)
│   ├── test_career.py                # Job fraud detection & resume tailoring tests (3 tests)
│   ├── test_communication.py         # Prompt injection & scam triage tests (5 tests)
│   ├── test_database.py              # SQLite WAL mode & backup/restore tests (3 tests)
│   ├── test_learning.py              # Self-learning engine, memory & persona tests (6 tests)
│   ├── test_mcp.py                   # Gmail & LinkedIn MCP server & tool tests (7 tests)
│   ├── test_messaging.py             # Telegram & WhatsApp webhook tests (9 tests)
│   ├── test_prompts.py               # Executive prompts & HITL protocol tests (10 tests)
│   ├── test_reminders.py             # Reminder delivery & snooze tests (1 test)
│   ├── test_search.py                # Live web search & research tests (6 tests)
│   ├── test_supabase.py              # Supabase storage, backup & restore tests (6 tests)
│   └── test_tasks.py                 # Task CRUD, FastMCP tools & bot commands (3 tests)
├── .env.example                      # Template environment variables
├── MCP_SETUP_GUIDE.md                # Quick visual guide for Gmail & LinkedIn setup
├── run.ps1                           # One-click Windows PowerShell launcher
└── README.md                         # Project documentation
```

---

## 11. REST API Documentation & Endpoints

| Method | Endpoint | Description | Security Guardrail |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/academic/attendance/summary` | Overall and subject-wise attendance percentages | Read-only |
| `POST` | `/api/academic/attendance/mark` | Logs class attendance (PRESENT / ABSENT) with notes | Ledger Write |
| `GET` | `/api/academic/attendance/absences` | Detailed absence history with notes and timestamps | Read-only |
| `GET` | `/api/academic/assignments` | Lists assignments filtered by status | Read-only |
| `POST` | `/api/academic/assignments` | Adds new course assignment with due date | Ledger Write |
| `PATCH`| `/api/academic/assignments/{id}` | Updates assignment status and records marks | Ledger Write |
| `GET` | `/api/academic/report/pdf` | Generates and streams official ReportLab PDF report | Dynamic Generator |
| `GET` | `/api/learning/memories` | Lists active learned memories and tone preferences | Read-only |
| `POST` | `/api/learning/memories` | Teaches AI a new preference, fact, or style rule | Memory Store |
| `DELETE`| `/api/learning/memories/{id}`| Deactivates an outdated memory rule | Soft Delete |
| `POST` | `/api/learning/feedback` | Submits conversational feedback for instant adaptation | Feedback Loop |
| `GET` | `/api/supabase/status` | Checks Supabase connection, URL, and bucket health | Health Check |
| `POST` | `/api/supabase/backup` | Triggers immediate SQLite cloud backup snapshot | Cloud Snapshot |
| `POST` | `/api/supabase/restore` | Restores local database from cloud snapshot | Cloud Restore |
| `GET` | `/api/supabase/files` | Lists stored objects in Supabase Storage | Read-only |
| `GET` | `/api/briefing/daily` | Daily top 3 priorities, deadlines & active alerts | Read-only |
| `GET` | `/api/communication/mcp/status`| Checks Gmail, LinkedIn & Task MCP connection status | Read-only |
| `POST` | `/api/communication/mcp/sync-emails` | Syncs unread emails via Gmail MCP with security triage | Safe Ingestion |
| `POST` | `/api/communication/mcp/sync-linkedin`| Syncs recruiter messages and connection invitations | Safe Ingestion |
| `POST` | `/api/communication/emails/{id}/reply`| Stages drafted response in Security Gate | Authorization Required |
| `POST` | `/api/communication/mcp/execute-approved/{id}`| Transmits approved email or post via MCP | **Approval Gate Verified** |
| `GET` | `/api/career/jobs` | Lists discovered opportunities with fraud ratings | Read-only |
| `POST` | `/api/career/tailor-resume` | Contextually tailors master resume against job description | Factual Integrity Check |
| `GET` | `/api/approvals` | Lists actions awaiting explicit user authorization | Security Gate |
| `POST` | `/api/approvals/{id}/decision` | Authorizes or rejects a staged action | User Decision Logged |
| `GET` | `/api/webhooks/status` | Checks live status of Telegram & WhatsApp gateways | Read-only |

---

## 12. Setup, Quick Start & Operations

### A. Environment Configuration (`.env`)

Copy `.env.example` to `.env` and fill in your keys:

```env
# AI Provider (NVIDIA NIM)
AI_PROVIDER="nvidia_nim"
AI_API_KEY="nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
AI_MODEL="google/diffusiongemma-26b-a4b-it"

# Telegram Bot Integration (@Meiyon_ai_bot)
TELEGRAM_ENABLED="true"
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_ALLOWED_CHAT_ID=""

# Supabase Cloud Storage & Database Persistence
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-supabase-service-role-key"
SUPABASE_STORAGE_BUCKET="meiyon-storage"
SUPABASE_AUTO_SYNC="true"

# Model Context Protocol (MCP): Zapier Servers
ZAPIER_TASKS_MCP_ID="02292b48-0fbd-8ca5-88c8-021274846b43"
ZAPIER_TASKS_MCP_URL="https://mcp.zapier.com/api/mcp/s/02292b48-0fbd-8ca5-88c8-021274846b43/mcp"

ZAPIER_GMAIL_MCP_ID="02750b42-81d6-8595-a28c-9aaadc202a9f"
ZAPIER_GMAIL_MCP_URL="https://mcp.zapier.com/api/mcp/s/02750b42-81d6-8595-a28c-9aaadc202a9f/mcp"

ZAPIER_LINKEDIN_MCP_ID="029df438-e88c-8c07-8d68-61978ee0976a"
ZAPIER_LINKEDIN_MCP_URL="https://mcp.zapier.com/api/mcp/s/029df438-e88c-8c07-8d68-61978ee0976a/mcp"
```

### B. Starting the Application

```powershell
# Using the PowerShell launcher
.\run.ps1

# Or with uv / Python directly
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### C. Running the Complete Automated Test Suite (71/71 Tests Passing)

The test suite thoroughly validates academic tracking, self-learning adaptation, Supabase cloud persistence, prompt injection defense, fraud scanning, FastMCP & Zapier tool execution, and messaging dispatchers:

```powershell
$env:PYTHONIOENCODING="utf-8"
uv run pytest -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.11.16, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\MOHIL\Desktop\agenticai
plugins: anyio-4.15.1
collected 71 items

tests/test_academic.py .....                                             [  7%]
tests/test_api.py .....                                                  [ 14%]
tests/test_approvals.py .                                                [ 15%]
tests/test_briefing.py .                                                 [ 16%]
tests/test_career.py ...                                                 [ 21%]
tests/test_communication.py .....                                        [ 28%]
tests/test_database.py ...                                               [ 32%]
tests/test_learning.py ......                                            [ 40%]
tests/test_mcp.py .......                                                [ 50%]
tests/test_messaging.py .........                                        [ 63%]
tests/test_prompts.py ..........                                         [ 77%]
tests/test_reminders.py .                                                [ 78%]
tests/test_search.py ......                                              [ 87%]
tests/test_supabase.py ......                                            [ 95%]
tests/test_tasks.py ...                                                  [100%]

======================== 71 passed in 120.45s (0:02:00) ========================
```

---

<div align="center">
  <sub>Engineered with precision for executive AI management • Built with FastAPI, SQLite WAL, Supabase, Model Context Protocol, Zapier, Telegram & WhatsApp</sub>
</div>
