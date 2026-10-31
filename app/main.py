"""Main FastAPI Application Entrypoint."""
import os
import asyncio
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
    routes_webhooks,
    routes_academic,
    routes_learning
)
from app.services.messaging_bot_service import run_continuous_telegram_poller

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PersonalAIManager")

scheduler = BackgroundScheduler(daemon=True)


def _keep_alive_ping():
    """Self-ping to prevent Render/Railway free tier from sleeping.
    Hits the local health endpoint every 10 minutes so the platform
    sees activity and keeps the service alive 24/7."""
    import httpx
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        ping_url = f"{render_url}/api/webhooks/status"
    else:
        ping_url = f"http://127.0.0.1:{settings.PORT}/api/webhooks/status"
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.get(ping_url)
            logger.debug("Keep-alive ping: %s -> %d", ping_url, resp.status_code)
    except Exception as e:
        logger.debug("Keep-alive ping failed (non-critical): %s", str(e))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database is initialized
    logger.info("Initializing SQLite database with WAL mode and baseline seed...")
    init_db()
    
    # Start reminder processor background job (every 60 seconds)
    logger.info("Starting background reminder scheduler...")
    scheduler.add_job(process_due_reminders, "interval", seconds=60, id="reminder_check", replace_existing=True)
    
    # Keep-alive self-ping every 10 minutes to prevent free-tier sleep
    logger.info("Starting keep-alive pinger (every 10 min) for 24/7 uptime...")
    scheduler.add_job(_keep_alive_ping, "interval", minutes=10, id="keep_alive", replace_existing=True)

    scheduler.start()

    # Start dedicated high-speed async Telegram long-poller (< 150ms response latency)
    telegram_task = None
    if settings.TELEGRAM_ENABLED and settings.TELEGRAM_BOT_TOKEN:
        logger.info("Starting High-Speed Async Telegram Poller...")
        telegram_task = asyncio.create_task(run_continuous_telegram_poller())
    
    yield
    
    # Shutdown
    if telegram_task:
        logger.info("Cancelling Telegram polling worker...")
        telegram_task.cancel()
    logger.info("Shutting down scheduler...")
    scheduler.shutdown(wait=False)

app = FastAPI(
    title="Meiyon",
    version=settings.APP_VERSION,
    description="Meiyon - Executive AI Personal Manager for Mohil - Career, Job Discovery, Schedule, & Memory",
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
app.include_router(routes_academic.router)
app.include_router(routes_learning.router)

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
