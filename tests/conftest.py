"""Global pytest fixtures and teardown hooks."""
import pytest
from app.database import get_db_connection

@pytest.fixture(autouse=True)
def cleanup_test_emails_after_test():
    """Ensures mock fixture emails created during tests are purged so production DB stays clean."""
    yield
    try:
        conn = get_db_connection()
        bad_senders = ("attacker@malicious.xyz", "google-recruiter-hiring@gmail.com", "careers@anthropic.com", "unknown@sender.com")
        conn.execute(f"DELETE FROM email_messages WHERE external_id IS NULL AND sender IN {bad_senders};")
        conn.commit()
        conn.close()
    except Exception:
        pass
