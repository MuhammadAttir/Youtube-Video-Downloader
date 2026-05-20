"""
Temporary file cleanup utilities.
Ensures downloaded/temp files don't pile up on disk.
"""
import os
import time
import glob
import logging
import threading

logger = logging.getLogger(__name__)


def delete_file_after_delay(filepath: str, delay: int = 120):
    """
    Delete a single file after `delay` seconds in a background thread.
    Used to clean up served download files.
    """
    def _delete():
        time.sleep(delay)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Auto-deleted temp file: {filepath}")
        except Exception as e:
            logger.warning(f"Failed to auto-delete {filepath}: {e}")

    thread = threading.Thread(target=_delete, daemon=True)
    thread.start()


def cleanup_old_files(directory: str, max_age_seconds: int = 600):
    """
    Remove files older than max_age_seconds from the given directory.
    Call this periodically to prevent disk buildup.
    """
    now = time.time()
    cleaned = 0
    try:
        for filepath in glob.glob(os.path.join(directory, "*")):
            if os.path.isfile(filepath):
                age = now - os.path.getmtime(filepath)
                if age > max_age_seconds:
                    os.remove(filepath)
                    cleaned += 1
                    logger.info(f"Cleaned old file: {filepath}")
    except Exception as e:
        logger.warning(f"Cleanup error in {directory}: {e}")
    return cleaned


def cleanup_directory(directory: str):
    """Remove ALL files in a directory (use with caution)."""
    cleaned = 0
    try:
        for filepath in glob.glob(os.path.join(directory, "*")):
            if os.path.isfile(filepath):
                os.remove(filepath)
                cleaned += 1
    except Exception as e:
        logger.warning(f"Full cleanup error: {e}")
    return cleaned
