"""SQLite database connection, schema setup, WAL mode, and backup/restore utilities."""
import sqlite3
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Generator
from app.config import settings

def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection with WAL mode enabled and Row factory."""
    conn = sqlite3.connect(settings.DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes schema and seeds baseline profile if not existing."""
    conn = get_db_connection()
    with conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            full_name TEXT NOT NULL DEFAULT 'User',
            education TEXT NOT NULL,
            college TEXT NOT NULL,
            expected_graduation TEXT NOT NULL,
            technical_interests TEXT NOT NULL,
            career_objectives TEXT NOT NULL,
            operating_environment TEXT NOT NULL,
            existing_skills TEXT NOT NULL,
            budget_preference TEXT NOT NULL,
            timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata',
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            priority TEXT NOT NULL DEFAULT 'P3_MEDIUM',
            status TEXT NOT NULL DEFAULT 'PENDING',
            category TEXT NOT NULL DEFAULT 'PERSONAL',
            source TEXT NOT NULL DEFAULT 'MANUAL',
            related_entity_type TEXT,
            related_entity_id TEXT,
            recurrence TEXT,
            is_confirmed INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            completed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS reminders (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            remind_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'SCHEDULED',
            channel TEXT NOT NULL DEFAULT 'DASHBOARD',
            delivery_message TEXT,
            delivery_timestamp TEXT,
            snooze_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id TEXT PRIMARY KEY,
            action_type TEXT NOT NULL,
            target_entity TEXT NOT NULL,
            details TEXT,
            mode TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS approvals (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            action_payload TEXT NOT NULL,
            risk_level TEXT NOT NULL DEFAULT 'MEDIUM',
            status TEXT NOT NULL DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            decided_at TEXT,
            decision_reason TEXT
        );

        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS job_listings (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            is_remote INTEGER NOT NULL DEFAULT 0,
            job_type TEXT NOT NULL DEFAULT 'INTERNSHIP',
            source_url TEXT NOT NULL UNIQUE,
            source_name TEXT NOT NULL,
            description TEXT NOT NULL,
            salary_info TEXT,
            application_deadline TEXT,
            match_score INTEGER NOT NULL DEFAULT 0,
            suitability_explanation TEXT,
            missing_qualifications TEXT,
            matching_skills TEXT,
            verification_status TEXT NOT NULL DEFAULT 'NEEDS_REVIEW',
            verification_report TEXT NOT NULL,
            discovered_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS master_resumes (
            id TEXT PRIMARY KEY,
            version_label TEXT NOT NULL,
            full_name TEXT NOT NULL,
            contact_email TEXT,
            phone TEXT,
            linkedin_url TEXT,
            github_url TEXT,
            summary TEXT NOT NULL,
            education TEXT NOT NULL,
            experience TEXT NOT NULL,
            projects TEXT NOT NULL,
            skills TEXT NOT NULL,
            certifications TEXT NOT NULL,
            ats_score INTEGER NOT NULL DEFAULT 85,
            ats_feedback TEXT NOT NULL,
            raw_text TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tailored_resumes (
            id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            version_label TEXT NOT NULL,
            tailored_summary TEXT NOT NULL,
            tailored_skills TEXT NOT NULL,
            tailored_projects TEXT NOT NULL,
            cover_letter TEXT NOT NULL,
            application_answers TEXT NOT NULL,
            keyword_gap_analysis TEXT NOT NULL,
            changes_made TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES job_listings (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS job_applications (
            id TEXT PRIMARY KEY,
            job_id TEXT,
            company TEXT NOT NULL,
            position TEXT NOT NULL,
            job_url TEXT,
            resume_version TEXT,
            status TEXT NOT NULL DEFAULT 'DRAFTED',
            recruiter_name TEXT,
            recruiter_email TEXT,
            interview_stages TEXT NOT NULL DEFAULT '[]',
            application_date TEXT,
            follow_up_date TEXT,
            next_action TEXT,
            notes TEXT,
            approval_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (job_id) REFERENCES job_listings (id) ON DELETE SET NULL,
            FOREIGN KEY (approval_id) REFERENCES approvals (id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS email_messages (
            id TEXT PRIMARY KEY,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            received_at TEXT NOT NULL,
            is_recruiter INTEGER NOT NULL DEFAULT 0,
            detected_intent TEXT NOT NULL DEFAULT 'GENERAL',
            phishing_risk TEXT NOT NULL DEFAULT 'LOW',
            phishing_flags TEXT NOT NULL DEFAULT '[]',
            extracted_dates TEXT NOT NULL DEFAULT '[]',
            proposed_reply TEXT,
            status TEXT NOT NULL DEFAULT 'UNREAD',
            created_at TEXT NOT NULL
        );
        """)

        # Seed profile if empty
        cur = conn.execute("SELECT id FROM user_profile WHERE id = 1;")
        if not cur.fetchone():
            now_iso = datetime.now(timezone.utc).isoformat()
            conn.execute("""
            INSERT INTO user_profile (
                id, full_name, education, college, expected_graduation,
                technical_interests, career_objectives, operating_environment,
                existing_skills, budget_preference, timezone, updated_at
            ) VALUES (
                1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """, (
                "AI Student & Engineer",
                "B.Tech Computer Science with Artificial Intelligence",
                "Mar Baselios Christian College of Engineering & Technology, Kuttikkanam",
                "2027",
                json.dumps([
                    "Artificial Intelligence",
                    "Machine Learning",
                    "Python",
                    "software development",
                    "web development",
                    "drone systems"
                ]),
                json.dumps([
                    "internships",
                    "graduate roles",
                    "entry-level software positions",
                    "AI/ML opportunities",
                    "relevant remote work"
                ]),
                "Windows laptop",
                json.dumps([
                    "Python",
                    "JavaScript",
                    "Git",
                    "GitHub",
                    "Node.js",
                    "Hermes Agent"
                ]),
                "free or low-cost tools",
                "Asia/Kolkata",
                now_iso
            ))
            
            # Record initial audit entry
            import uuid
            conn.execute("""
            INSERT INTO audit_logs (id, action_type, target_entity, details, mode, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                "SYSTEM_INIT",
                "database",
                json.dumps({"message": "Database and user profile initialized with verified defaults"}),
                settings.AUTONOMY_MODE,
                "SUCCESS",
                now_iso
            ))

        # Seed master resume if empty
        cur_res = conn.execute("SELECT id FROM master_resumes WHERE is_active = 1;")
        if not cur_res.fetchone():
            import uuid
            now_iso = datetime.now(timezone.utc).isoformat()
            conn.execute("""
            INSERT INTO master_resumes (
                id, version_label, full_name, contact_email, phone,
                linkedin_url, github_url, summary, education, experience,
                projects, skills, certifications, ats_score, ats_feedback,
                raw_text, is_active, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                str(uuid.uuid4()),
                "v1.0-master",
                "Mohil",
                "mohil@example.com",
                "+91-XXXXXXXXXX",
                "https://linkedin.com/in/mohil",
                "https://github.com/mohil",
                "Undergraduate AI & Computer Science Engineer (B.Tech '27) passionate about Artificial Intelligence, Machine Learning, autonomous drone systems, and software engineering. Experienced in Python, Node.js, API development, and agentic workflows.",
                json.dumps([{
                    "degree": "B.Tech in Computer Science with Artificial Intelligence",
                    "institution": "Mar Baselios Christian College of Engineering & Technology, Kuttikkanam",
                    "expected_graduation": "2027",
                    "coursework": ["Artificial Intelligence", "Machine Learning", "Data Structures", "Python Programming", "Database Management"]
                }]),
                json.dumps([]),  # Factually honest: no invented employment history
                json.dumps([
                    {
                        "title": "Autonomous Drone Systems & ML Telemetry",
                        "technologies": ["Python", "Machine Learning", "Drone Systems", "Computer Vision"],
                        "highlights": [
                            "Engineered drone telemetry processing pipelines and real-time navigation heuristics.",
                            "Explored AI/ML model integration for edge inference and aerial vision tasks."
                        ]
                    },
                    {
                        "title": "Personal AI Executive Manager & Agentic Assistant",
                        "technologies": ["Python", "FastAPI", "SQLite WAL", "Pydantic", "HTML5/CSS"],
                        "highlights": [
                            "Architected executive assistant managing career matching, fraud detection, and task scheduling.",
                            "Implemented strict human-in-the-loop security gates (Mode A/B/C) and SQLite WAL snapshot engine."
                        ]
                    }
                ]),
                json.dumps([
                    "Python", "Artificial Intelligence", "Machine Learning", "Node.js", "JavaScript",
                    "Git", "GitHub", "FastAPI", "SQLite", "Drone Systems", "REST APIs", "Agentic Systems"
                ]),
                json.dumps([]),
                88,
                json.dumps([
                    "Strong technical profile for AI/ML and software internships.",
                    "Factual integrity preserved: clearly distinguishes undergraduate projects from commercial employment.",
                    "ATS-friendly clean structure with quantified highlights."
                ]),
                "Mohil - B.Tech AI Resume",
                now_iso
            ))
    conn.close()

def backup_database() -> Path:
    """Creates a timestamped backup of the SQLite database."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = settings.BACKUP_DIR / f"manager_backup_{timestamp}.db"
    
    # Use SQLite native backup API to ensure safety even if writes are active
    src_conn = get_db_connection()
    dst_conn = sqlite3.connect(backup_file)
    with dst_conn:
        src_conn.backup(dst_conn)
    dst_conn.close()
    src_conn.close()
    return backup_file

def restore_database(backup_path: Path) -> bool:
    """Restores database from a verified backup file."""
    if not backup_path.exists():
        raise FileNotFoundError(f"Backup file not found at {backup_path}")
    
    # Verify the backup file can be opened and has tables
    test_conn = sqlite3.connect(backup_path)
    cur = test_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    test_conn.close()
    
    if "user_profile" not in tables or "tasks" not in tables:
        raise ValueError("Invalid backup file: required tables missing")
        
    # Safely copy into place
    shutil.copy2(backup_path, settings.DB_PATH)
    return True
