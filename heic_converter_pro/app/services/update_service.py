from __future__ import annotations

import logging
import json
import re
from pathlib import Path
from typing import Optional
from packaging.version import Version

logger = logging.getLogger(__name__)

APP_VERSION = "1.0.0"
GITHUB_REPO = "user/heic-converter-pro"
RELEASE_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


class UpdateService:
    @staticmethod
    def check_for_update() -> Optional[dict]:
        try:
            import urllib.request
            req = urllib.request.Request(
                RELEASE_API,
                headers={"User-Agent": "HEIC-Converter-Pro/1.0"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                latest_version = data.get("tag_name", "").lstrip("v")
                if latest_version and Version(latest_version) > Version(APP_VERSION):
                    return {
                        "version": latest_version,
                        "url": data.get("html_url", ""),
                        "download_url": data.get("assets", [{}])[0].get(
                            "browser_download_url", ""
                        ) if data.get("assets") else "",
                        "release_notes": data.get("body", "")[:500],
                    }
        except Exception as exc:
            logger.debug("Update check failed: %s", exc)
        return None

    @staticmethod
    def download_update(url: str, target: Path) -> bool:
        try:
            import urllib.request
            with urllib.request.urlopen(url, timeout=300) as resp:
                target.write_bytes(resp.read())
            return True
        except Exception as exc:
            logger.error("Update download failed: %s", exc)
            return False
