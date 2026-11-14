"""API integration tests using FastAPI TestClient."""
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)

def test_api_health():
    res = client.get("/api/system/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["autonomy_mode"] in ["ASSISTED", "SUPERVISED", "RESTRICTED_AUTONOMY"]

def test_api_dashboard_served():
    res = client.get("/")
    assert res.status_code == 200
    assert "Personal AI Manager" in res.text

def test_api_tasks_crud_and_complete():
    # 1. Create task
    create_payload = {
        "title": "API Test Task",
        "description": "Integration test for API",
        "priority": "P2_HIGH",
        "category": "PROJECT",
        "is_confirmed": True
    }
    res = client.post("/api/tasks", json=create_payload)
    assert res.status_code == 201
    task = res.json()
    task_id = task["id"]
    assert task["title"] == "API Test Task"
    
    # 2. Get task
    res = client.get(f"/api/tasks/{task_id}")
    assert res.status_code == 200
    assert res.json()["id"] == task_id
    
    # 3. Complete task
    res = client.post(f"/api/tasks/{task_id}/complete")
    assert res.status_code == 200
    assert res.json()["status"] == "COMPLETED"
    
    # 4. Delete task
    res = client.delete(f"/api/tasks/{task_id}")
    assert res.status_code == 204

def test_api_profile_and_briefing():
    # Profile
    res = client.get("/api/profile")
    assert res.status_code == 200
    prof = res.json()
    assert prof["expected_graduation"] == "2027"
    
    # Briefing
    res = client.get("/api/briefing")
    assert res.status_code == 200
    briefing = res.json()
    assert "executive_summary" in briefing
    assert "top_three_priorities" in briefing

def test_api_career_endpoints():
    # 1. Get Master Resume
    res = client.get("/api/career/resume")
    assert res.status_code == 200
    resume = res.json()
    assert resume["full_name"] == "Mohil"
    assert "Python" in resume["skills"]
    
    # 2. Add / inspect job via API
    job_payload = {
        "title": "Machine Learning Intern",
        "company": "Cognitive AI Lab",
        "source_url": "https://boards.greenhouse.io/cognitive/ml-intern",
        "description": "Python, Machine Learning, and API backend engineering."
    }
    res = client.post("/api/career/jobs", json=job_payload)
    assert res.status_code == 201
    job = res.json()
    job_id = job["id"]
    assert job["verification_status"] == "VERIFIED_BY_EVIDENCE"
    
    # 3. Tailor resume for job via API
    res = client.post(f"/api/career/jobs/{job_id}/tailor")
    assert res.status_code == 200
    tailored = res.json()
    assert "Cognitive AI Lab" in tailored["cover_letter"]
    
    # 4. Create application via API (triggers human authorization)
    app_payload = {
        "job_id": job_id,
        "company": "Cognitive AI Lab",
        "position": "Machine Learning Intern",
        "job_url": job["source_url"]
    }
    res = client.post("/api/career/applications", json=app_payload)
    assert res.status_code == 201
    app_data = res.json()
    assert app_data["status"] == "READY_FOR_APPROVAL"

def test_security_defenses_and_backdoor_protection():
    """Verifies security boundaries, path traversal rejection, and outbound locks."""
    # 1. Security Headers
    res = client.get("/api/system/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert "1" in res.headers.get("X-XSS-Protection", "")

    # 2. Path Traversal on System Restore
    res_trav = client.post("/api/system/restore?filename=../../etc/passwd")
    assert res_trav.status_code in (400, 404)

    # 3. Path Traversal on Supabase Cloud Restore
    res_sub_trav = client.post("/api/supabase/restore?remote_path=../../etc/passwd")
    assert res_sub_trav.status_code == 400

    # 4. Outbound WhatsApp destination lock (reject unauthorized third-party numbers)
    res_spam = client.post("/api/webhooks/whatsapp/send-message", data={
        "to_number": "whatsapp:+19999999999",
        "text": "Spam test"
    })
    assert res_spam.status_code == 403
    assert "Security restriction" in res_spam.json()["detail"]

