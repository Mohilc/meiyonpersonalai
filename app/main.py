"""Main FastAPI Application Entrypoint."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.database import init_db
from app.services.reminder_service import process_due_reminders
from app.api import (
    routes_profile,
    routes_tasks,
    routes_reminders,
    routes_approvals,
    routes_briefing,
    routes_system,
    routes_career,
    routes_communication,
    routes_webhooks
)
from app.services.messaging_bot_service import poll_telegram_updates_once

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PersonalAIManager")

scheduler = BackgroundScheduler(daemon=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database is initialized
    logger.info("Initializing SQLite database with WAL mode and baseline seed...")
    init_db()
    
    # Start reminder processor background job (every 60 seconds)
    logger.info("Starting background reminder scheduler...")
    scheduler.add_job(process_due_reminders, "interval", seconds=60, id="reminder_check", replace_existing=True)
    
    # Start Telegram update poller (every 3 seconds) if token configured
    if settings.TELEGRAM_ENABLED and settings.TELEGRAM_BOT_TOKEN:
        logger.info("Starting Telegram Bot polling engine...")
        scheduler.add_job(poll_telegram_updates_once, "interval", seconds=3, id="telegram_poll", replace_existing=True)

    scheduler.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down scheduler...")
    scheduler.shutdown(wait=False)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Executive AI Personal Manager for Mohil - Career, Job Discovery, Schedule, & Memory",
    lifespan=lifespan
)

# API Routers
app.include_router(routes_profile.router)
app.include_router(routes_tasks.router)
app.include_router(routes_reminders.router)
app.include_router(routes_approvals.router)
app.include_router(routes_briefing.router)
app.include_router(routes_system.router)
app.include_router(routes_career.router)
app.include_router(routes_communication.router)
app.include_router(routes_webhooks.router)

# Static and Web Dashboard
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
async def serve_dashboard():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Personal AI Manager API is running. Dashboard HTML not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
