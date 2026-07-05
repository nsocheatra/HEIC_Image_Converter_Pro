from __future__ import annotations

import logging
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class MediaDetector:
    FFMPEG_DIR = Path(__file__).parent.parent.parent.parent / "ffmpeg"

    @classmethod
    def find_ffmpeg(cls) -> Optional[Path]:
        paths = cls._search_paths()
        for path in paths:
            if path.exists() and os.access(str(path), os.X_OK):
                try:
                    result = subprocess.run(
                        [str(path), "-version"],
                        capture_output=True, text=True, timeout=5,
                    )
                    if result.returncode == 0 and "ffmpeg" in result.stdout.lower():
                        logger.info("FFmpeg found: %s", path)
                        return path
                except (OSError, subprocess.TimeoutExpired):
                    continue
        logger.warning("FFmpeg not found")
        return None

    @classmethod
    def find_ffprobe(cls) -> Optional[Path]:
        paths = cls._search_paths("ffprobe")
        for path in paths:
            if path.exists() and os.access(str(path), os.X_OK):
                try:
                    result = subprocess.run(
                        [str(path), "-version"],
                        capture_output=True, text=True, timeout=5,
                    )
                    if result.returncode == 0 and "ffprobe" in result.stdout.lower():
                        logger.info("FFprobe found: %s", path)
                        return path
                except (OSError, subprocess.TimeoutExpired):
                    continue
        return None

    @classmethod
    def _search_paths(cls, executable: str = "ffmpeg") -> list[Path]:
        paths: list[Path] = []
        bundled = cls.FFMPEG_DIR / f"{executable}.exe"
        if bundled.exists():
            paths.append(bundled)
        system_path = shutil.which(executable)
        if system_path:
            paths.append(Path(system_path))
        for candidate in Path(".").glob(f"**/{executable}.exe"):
            if candidate.resolve() not in [p.resolve() for p in paths]:
                paths.append(candidate.resolve())
        return paths

    @classmethod
    def is_available(cls) -> bool:
        return cls.find_ffmpeg() is not None

    @classmethod
    def probe_file(cls, path: Path) -> Optional[dict]:
        ffprobe = cls.find_ffprobe()
        if not ffprobe:
            return None
        cmd = [
            str(ffprobe),
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]
        try:
            import json
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            logger.warning("FFprobe failed for %s: %s", path.name, exc)
        return None
