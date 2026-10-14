# Personal AI Manager - Quick Launch Script for Windows PowerShell
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       PERSONAL AI MANAGER - EXECUTIVE ASSISTANT          " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

$VENV_PYTHON = ".venv\Scripts\python.exe"

if (-not (Test-Path $VENV_PYTHON)) {
    Write-Host "[!] Virtual environment not detected. Creating with uv..." -ForegroundColor Yellow
    uv venv .venv --python C:\Users\MOHIL\.local\bin\python3.11.exe
    uv pip install fastapi uvicorn pydantic pydantic-settings apscheduler pytest httpx python-multipart
}

Write-Host "[+] Starting Personal AI Manager on http://127.0.0.1:8000 ..." -ForegroundColor Green
Write-Host "[*] Operating Timezone: Asia/Kolkata" -ForegroundColor Gray
Write-Host "[*] Database: SQLite WAL mode at data/manager.db" -ForegroundColor Gray
Write-Host "[*] Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray

& $VENV_PYTHON -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
