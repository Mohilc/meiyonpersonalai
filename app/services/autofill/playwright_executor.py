"""Playwright Headless Browser Executor for Form Autofilling and Visual Verification."""
import os
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)

REPORTS_DIR = Path(settings.DB_PATH).parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


async def execute_headless_autofill(
    url: str,
    field_values: Dict[str, str],
    take_screenshot: bool = True
) -> Dict[str, Any]:
    """
    Executes headless Playwright browser to populate form fields and captures
    a visual verification screenshot before any submission.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        return {
            "success": False,
            "error": "Playwright is not installed in the environment.",
            "filled_count": 0
        }

    screenshot_path: Optional[str] = None
    filled_count = 0
    errors = []

    try:
        async with async_playwright() as p:
            # Launch Chromium with sandboxing flags
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1280, "height": 900})

            # Navigate to target form
            logger.info("Playwright navigating to form: %s", url)
            await page.goto(url, timeout=20000, wait_until="domcontentloaded")
            await asyncio.sleep(1.0)  # brief settle for dynamic widgets

            # Fill each field
            for selector, value in field_values.items():
                if not selector or not value:
                    continue
                try:
                    el = await page.wait_for_selector(selector, timeout=2500)
                    if el:
                        tag_name = await el.evaluate("el => el.tagName.toLowerCase()")
                        if tag_name == "select":
                            # Try selecting by label or value
                            try:
                                await el.select_option(label=value)
                            except Exception:
                                await el.select_option(value=value)
                        else:
                            await el.fill(str(value))
                        filled_count += 1
                except Exception as e:
                    errors.append(f"Failed to fill {selector}: {str(e)[:60]}")

            # Capture visual verification screenshot
            if take_screenshot:
                now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                target_file = REPORTS_DIR / f"autofill_preview_{now_str}.png"
                await page.screenshot(path=str(target_file), full_page=True)
                screenshot_path = str(target_file)
                logger.info("Captured autofill visual screenshot: %s", screenshot_path)

            await browser.close()

        return {
            "success": True,
            "url": url,
            "filled_count": filled_count,
            "screenshot_path": screenshot_path,
            "errors": errors,
            "staged_for_review": True
        }

    except Exception as e:
        logger.warning("Playwright execution notice for %s: %s", url, str(e))
        return {
            "success": False,
            "url": url,
            "filled_count": filled_count,
            "error": str(e),
            "simulated": True,
            "notice": "Form can be populated directly in browser using the 1-click JavaScript bookmarklet."
        }
