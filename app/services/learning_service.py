"""Self-Learning Engine & Persona Adaptation Service for Personal AI Manager.

Enables the AI to continuously learn from user interactions, explicit commands,
conversational feedback, and corrections to evolve a warm, human-friendly,
and deeply customized persona.
"""
import re
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

from app.database import get_db_connection
from app.models.learning import (
    LearnedMemory,
    LearnedMemoryCreate,
    MemoryCategoryEnum,
    MemorySourceEnum
)

logger = logging.getLogger(__name__)

# Patterns for explicit learning triggers (flexible anchors)
EXPLICIT_REMEMBER_PATTERNS = [
    r"(?:remember|note down|keep in mind|learn|don't forget)\s*(?:that|this)?[:\s]+(.+)",
    r"from now on[,\s]+(?:always\s+)?(.+)",
    r"please (?:remember|note down)[:\s]+(.+)"
]

# Patterns for tone and style preferences
TONE_STYLE_PATTERNS = [
    (r"(?:be|talk|speak|sound)\s+(?:more\s+)?(?:friendly|casual|informal|warm|human|chill|approachable)", "warm_and_casual", "Speak warmly, casually, and conversationally like a close, trusted friend. Avoid robotic or stiff corporate phrasing."),
    (r"(?:be|talk|speak|sound)\s+(?:more\s+)?(?:professional|formal|executive|serious)", "professional_executive", "Maintain a polished, crisp, and high-level executive demeanor with structured strategic clarity."),
    (r"(?:be|keep it|give)\s+(?:more\s+)?(?:concise|short|brief|crisp|direct)", "concise_direct", "Keep responses short, crisp, and directly to the point. Avoid fluff or preamble."),
    (r"(?:use|add)\s+(?:more\s+)?(?:emojis|visuals)", "use_emojis", "Use expressive, friendly emojis to make messages vibrant and engaging."),
    (r"(?:stop using|don't use|avoid|no)\s+(?:corporate|buzzwords|jargon|cliches)", "avoid_corporate_jargon", "Strictly avoid corporate buzzwords, generic HR templates, or cliché corporate boilerplate."),
    (r"(?:call me|my name is)\s+([a-zA-Z0-9_\-]+)", "preferred_name", "Address the user as {match}.")
]

# Patterns for corrections and dislikes
CORRECTION_PATTERNS = [
    r"^(?:no|actually|that's wrong|incorrect)[,\s]+(.+)",
    r"^i (?:don't like|hate|dislike)\s+(?:when you|it when you)?\s*(.+)"
]


def add_or_update_memory(
    category: str,
    key: str,
    content: str,
    source: str = "EXPLICIT_USER_COMMAND",
    confidence_score: float = 1.0
) -> LearnedMemory:
    """Creates or updates a persistent learned memory in the database."""
    conn = get_db_connection()
    now_iso = datetime.now(timezone.utc).isoformat()
    clean_cat = category.upper().strip()
    clean_key = key.strip().lower()
    clean_content = content.strip()

    try:
        with conn:
            # Check if key already exists
            cur = conn.execute("SELECT id FROM learned_memories WHERE key = ?;", (clean_key,))
            existing = cur.fetchone()

            if existing:
                real_id = existing["id"]
                conn.execute("""
                UPDATE learned_memories
                SET content = ?, category = ?, source = ?, confidence_score = ?, is_active = 1, updated_at = ?
                WHERE id = ?;
                """, (clean_content, clean_cat, source, confidence_score, now_iso, real_id))
            else:
                real_id = str(uuid.uuid4())
                conn.execute("""
                INSERT INTO learned_memories (
                    id, category, key, content, source, confidence_score, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?);
                """, (real_id, clean_cat, clean_key, clean_content, source, confidence_score, now_iso, now_iso))

        logger.info("Learned memory saved [%s]: %s -> %s", clean_cat, clean_key, clean_content[:60])
        return get_memory_by_id(real_id)
    finally:
        conn.close()


def get_memory_by_id(memory_id: str) -> Optional[LearnedMemory]:
    """Fetches a specific learned memory by ID."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM learned_memories WHERE id = ?;", (memory_id,))
        row = cur.fetchone()
        if not row:
            return None
        return _row_to_memory(row)
    finally:
        conn.close()


def get_memory_by_key(key: str) -> Optional[LearnedMemory]:
    """Fetches a specific learned memory by key."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM learned_memories WHERE key = ? AND is_active = 1;", (key.strip().lower(),))
        row = cur.fetchone()
        if not row:
            return None
        return _row_to_memory(row)
    finally:
        conn.close()


def list_active_memories(category: Optional[str] = None) -> List[LearnedMemory]:
    """Retrieves all active learned memories."""
    conn = get_db_connection()
    try:
        if category:
            cur = conn.execute("""
            SELECT * FROM learned_memories
            WHERE is_active = 1 AND category = ?
            ORDER BY updated_at DESC;
            """, (category.upper().strip(),))
        else:
            cur = conn.execute("""
            SELECT * FROM learned_memories
            WHERE is_active = 1
            ORDER BY CASE category
                WHEN 'COMMUNICATION_STYLE' THEN 1
                WHEN 'PREFERENCE' THEN 2
                WHEN 'CORRECTION' THEN 3
                ELSE 4 END, updated_at DESC;
            """)
        rows = cur.fetchall()
        return [_row_to_memory(r) for r in rows]
    finally:
        conn.close()


def deactivate_memory(memory_id_or_key: str) -> bool:
    """Soft-deletes/deactivates a memory by ID, short ID, key, or content match."""
    conn = get_db_connection()
    target = memory_id_or_key.strip()
    target_lower = target.lower()
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        with conn:
            # First try exact id or exact key
            cur = conn.execute("""
            UPDATE learned_memories
            SET is_active = 0, updated_at = ?
            WHERE is_active = 1 AND (id = ? OR key = ?);
            """, (now_iso, target, target_lower))
            if cur.rowcount > 0:
                return True

            # Next try ID prefix (e.g. 8-char short ID shown in /memory)
            cur = conn.execute("""
            UPDATE learned_memories
            SET is_active = 0, updated_at = ?
            WHERE is_active = 1 AND id LIKE ?;
            """, (now_iso, f"{target}%"))
            if cur.rowcount > 0:
                return True

            # Next try content or key fuzzy match
            cur = conn.execute("""
            UPDATE learned_memories
            SET is_active = 0, updated_at = ?
            WHERE is_active = 1 AND (
                LOWER(key) LIKE ? OR LOWER(content) LIKE ?
            );
            """, (now_iso, f"%{target_lower}%", f"%{target_lower}%"))
            return cur.rowcount > 0
    finally:
        conn.close()


def extract_learnings_from_user_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Real-time semantic learning detector:
    Parses conversational user input to automatically extract style preferences,
    explicit memory instructions, or behavioral feedback.
    """
    clean_text = text.strip()
    clean_lower = clean_text.lower()

    # 1. Check for explicit "remember that / note down that / from now on"
    for pat in EXPLICIT_REMEMBER_PATTERNS:
        match = re.search(pat, clean_text, re.IGNORECASE)
        if match:
            learned_content = match.group(1).strip()
            key_slug = re.sub(r"[^a-z0-9_]+", "_", learned_content[:30].lower()).strip("_")
            mem = add_or_update_memory(
                category="PREFERENCE",
                key=f"user_{key_slug}",
                content=learned_content,
                source="EXPLICIT_USER_COMMAND",
                confidence_score=1.0
            )
            return {
                "type": "EXPLICIT_MEMORY",
                "key": mem.key,
                "content": mem.content,
                "acknowledgment": f"🧠 *Memory Learned!*\nI've noted that down: _\"{learned_content}\"_\nI'll remember this in our future conversations! ✨"
            }

    # 2. Check for conversational style / tone feedback
    for pat, key, instruction_tmpl in TONE_STYLE_PATTERNS:
        match = re.search(pat, clean_lower)
        if match:
            if "{match}" in instruction_tmpl:
                val = match.group(1).title() if match.groups() else ""
                instruction = instruction_tmpl.replace("{match}", val)
            else:
                instruction = instruction_tmpl
                
            mem = add_or_update_memory(
                category="COMMUNICATION_STYLE",
                key=key,
                content=instruction,
                source="AUTOMATIC_EXTRACTION",
                confidence_score=0.95
            )
            return {
                "type": "TONE_ADAPTATION",
                "key": mem.key,
                "content": mem.content,
                "acknowledgment": f"✨ *Style Adapted!*\nGot it! I've updated my tone: _\"{instruction}\"_\nFrom now on, I'll keep our conversations friendly, warm, and natural! 🤝"
            }

    # 3. Check for corrections ("no, actually...", "i don't like when you...")
    for pat in CORRECTION_PATTERNS:
        match = re.search(pat, clean_text, re.IGNORECASE)
        if match:
            correction_text = match.group(1).strip()
            key_slug = re.sub(r"[^a-z0-9_]+", "_", correction_text[:25].lower()).strip("_")
            mem = add_or_update_memory(
                category="CORRECTION",
                key=f"corr_{key_slug}",
                content=f"Correction from user: {correction_text}",
                source="AUTOMATIC_EXTRACTION",
                confidence_score=0.9
            )
            return {
                "type": "CORRECTION",
                "key": mem.key,
                "content": mem.content,
                "acknowledgment": f"💡 *Correction Learned!*\nThank you for correcting me! I've saved: _\"{correction_text}\"_ and will adapt right away."
            }

    # 4. Check for implicit factual knowledge & project context
    AUTO_FACT_PATTERNS = [
        (r"(?:i am working on|i'm working on|my project is|my current project is)\s+([^.!?\n]+)", "project", "Working on: {match}"),
        (r"(?:my goal is|i want to become|i am targeting|i want to work as|aiming for)\s+([^.!?\n]+)", "goal", "Career goal: {match}"),
        (r"(?:i code in|i program in|my favorite language is)\s+([^.!?\n]+)", "tech", "Primary technical tools: {match}"),
        (r"(?:my college is|i study at|i'm studying at)\s+([^.!?\n]+)", "education", "Studying at: {match}"),
        (r"(?:i prefer to|i like when|i really like)\s+([^.!?\n]+)", "preference", "User preference: {match}")
    ]
    for pat, key, tmpl in AUTO_FACT_PATTERNS:
        match = re.search(pat, clean_text, re.IGNORECASE)
        if match:
            extracted = match.group(1).strip()
            if 2 < len(extracted) < 120:
                formatted = tmpl.replace("{match}", extracted)
                key_slug = re.sub(r"[^a-z0-9_]+", "_", extracted[:25].lower()).strip("_")
                mem = add_or_update_memory(
                    category="FACTUAL_KNOWLEDGE",
                    key=f"{key}_{key_slug}",
                    content=formatted,
                    source="AUTOMATIC_EXTRACTION",
                    confidence_score=0.9
                )
                return {
                    "type": "AUTO_FACT",
                    "key": mem.key,
                    "content": mem.content,
                    "acknowledgment": f"🧠 *Noted & Saved to Memory!*\nI've learned: _\"{formatted}\"_\nI'll remember this across all our future conversations! ✨"
                }

    return None


def compile_learned_prompt_instructions() -> str:
    """
    Compiles all active learned memories and communication styles into a
    structured prompt block to ground the LLM in the user's evolved preferences.
    """
    memories = list_active_memories()
    if not memories:
        return ""

    lines = [
        "=== SELF-LEARNED ADAPTIVE USER PREFERENCES & PERSONA ===",
        "You have continuously learned the following habits, style preferences, and facts directly from the user.",
        "You MUST strictly adhere to these learned rules:\n"
    ]

    for m in memories:
        cat_badge = f"[{m.category.value}]"
        lines.append(f"• {cat_badge} {m.content}")

    lines.append("\nRemember: Treat the user like a respected close friend and partner. Speak warmly, naturally, and avoid sounding like a machine.")
    return "\n".join(lines)


def _row_to_memory(row: Any) -> LearnedMemory:
    """Helper to convert sqlite3.Row to LearnedMemory model."""
    return LearnedMemory(
        id=row["id"],
        category=MemoryCategoryEnum(row["category"]),
        key=row["key"],
        content=row["content"],
        source=MemorySourceEnum(row["source"]),
        confidence_score=float(row["confidence_score"]),
        is_active=bool(row["is_active"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )
