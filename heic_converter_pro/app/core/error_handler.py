from __future__ import annotations

import logging
import os
import traceback
from pathlib import Path
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class ErrorHandler:
    ERROR_MESSAGES = {
        "corrupt": "The file appears to be corrupt or unreadable",
        "permission": "Permission denied. Check file/folder permissions",
        "disk_full": "Disk is full. Free up space and try again",
        "ffmpeg_missing": "FFmpeg is not available. Install FFmpeg or use Pillow",
        "unsupported": "Unsupported file format",
        "memory": "Out of memory. Try processing fewer files at once",
        "unknown": "An unexpected error occurred",
    }

    @staticmethod
    def classify_error(exc: Exception) -> str:
        msg = str(exc).lower()
        if "corrupt" in msg or "truncated" in msg or "broken" in msg:
            return "corrupt"
        if "permission" in msg or "access is denied" in msg:
            return "permission"
        if "disk" in msg or "space" in msg or "no space" in msg:
            return "disk_full"
        if "ffmpeg" in msg.lower():
            return "ffmpeg_missing"
        if "unsupported" in msg or "cannot identify" in msg:
            return "unsupported"
        if "memory" in msg or "alloc" in msg:
            return "memory"
        return "unknown"

    @staticmethod
    def handle_exception(
        exc: Exception,
        context: Optional[str] = None,
        user_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        category = ErrorHandler.classify_error(exc)
        message = ErrorHandler.ERROR_MESSAGES.get(category, str(exc))
        if context:
            full_msg = f"[{context}] {message}"
        else:
            full_msg = message

        logger.error("%s\n%s", full_msg, traceback.format_exc())

        if user_callback:
            user_callback(full_msg)

        return full_msg

    @staticmethod
    def safe_delete(path: Path) -> bool:
        try:
            path.unlink()
            return True
        except (OSError, PermissionError) as exc:
            logger.warning("Failed to delete %s: %s", path, exc)
            return False

    @staticmethod
    def safe_makedirs(path: Path) -> bool:
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError) as exc:
            logger.error("Failed to create directory %s: %s", path, exc)
            return False
