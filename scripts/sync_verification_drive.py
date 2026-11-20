#!/usr/bin/env python3
"""CLI Trigger for EmailAI Verification RAG Google Drive Sync.

Usage:
    python scripts/sync_verification_drive.py
    python scripts/sync_verification_drive.py --folder-id <GOOGLE_DRIVE_FOLDER_ID>

CRITICAL:
Run this on-demand or as a cron job to keep Supabase pgvector allowlists updated.
NEVER invoke this script or Google Drive within user chat requests.
"""
import sys
import argparse
import logging
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.services import verification_rag

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("DriveSyncCLI")


def main():
    parser = argparse.ArgumentParser(description="Sync Google Drive verification documents into Supabase pgvector.")
    parser.add_argument("--folder-id", type=str, default=None, help="Google Drive Folder ID override")
    args = parser.parse_args()

    logger.info("Starting Google Drive verification sync...")
    try:
        result = verification_rag.sync_drive_documents(folder_id=args.folder_id)
        logger.info("Sync complete! Details: %s", result)
        print("\n--- SYNC SUMMARY ---")
        print(f"Status:             {result.get('status')}")
        print(f"Documents Fetched:  {result.get('fetched_from_drive')}")
        print(f"New Vectors Added:  {result.get('inserted')}")
        print(f"Vectors Updated:    {result.get('updated')}")
        print(f"Unchanged/Skipped:  {result.get('skipped')}")
        print(f"Active Index Size:  {result.get('active_index_size')}")
        print("---------------------\n")
    except Exception as e:
        logger.error("Sync failed: %s", str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
