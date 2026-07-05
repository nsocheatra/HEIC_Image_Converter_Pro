from __future__ import annotations

import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Optional

from heic_converter_pro.app.media.media_detector import MediaDetector

logger = logging.getLogger(__name__)


class FfmpegConverter:
    def __init__(self) -> None:
        self._ffmpeg = MediaDetector.find_ffmpeg()
        self._ffprobe = MediaDetector.find_ffprobe()

    @property
    def available(self) -> bool:
        return self._ffmpeg is not None

    def convert(
        self,
        source: Path,
        output_path: Path,
        quality: int = 95,
        output_format: str = "jpg",
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> Path:
        if not self.available:
            raise RuntimeError("FFmpeg not available")

        output_path = output_path.with_suffix(f".{output_format.lower().replace('jpeg', 'jpg')}")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        quality_map = {
            "jpg": self._ffmpeg_jpeg_quality,
            "jpeg": self._ffmpeg_jpeg_quality,
            "png": self._ffmpeg_png_args,
            "webp": self._ffmpeg_webp_args,
            "tiff": self._ffmpeg_tiff_args,
            "bmp": lambda q: [],
            "pdf": self._ffmpeg_pdf_args,
        }

        fmt = output_format.lower().replace("jpeg", "jpg")
        quality_args = quality_map.get(fmt, self._ffmpeg_jpeg_quality)(quality)

        cmd = [
            str(self._ffmpeg),
            "-i", str(source),
            "-y",
            *quality_args,
            str(output_path),
        ]

        logger.info("FFmpeg convert: %s", " ".join(str(c) for c in cmd))
        self._run_ffmpeg(cmd, progress_callback)
        logger.info("FFmpeg: %s -> %s", source.name, output_path.name)
        return output_path

    def extract_thumbnail(self, source: Path, output_path: Path, size: int = 256) -> Path:
        if not self.available:
            raise RuntimeError("FFmpeg not available")
        cmd = [
            str(self._ffmpeg),
            "-i", str(source),
            "-vf", f"scale={size}:{size}:force_original_aspect_ratio=decrease",
            "-frames:v", "1",
            "-y",
            str(output_path),
        ]
        self._run_ffmpeg(cmd)
        return output_path

    def probe(self, source: Path) -> Optional[dict]:
        if not self._ffprobe:
            return None
        cmd = [
            str(self._ffprobe),
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(source),
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as exc:
            logger.warning("FFprobe failed for %s: %s", source.name, exc)
        return None

    def _run_ffmpeg(
        self, cmd: list, progress_callback: Optional[Callable[[float], None]] = None
    ) -> None:
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREAT_NO_WINDOW") else 0,
            )
            duration = None
            for line in process.stdout or []:
                if "Duration:" in line:
                    import re
                    match = re.search(r"Duration: (\d+):(\d+):(\d+)\.(\d+)", line)
                    if match:
                        h, m, s, ms = map(int, match.groups())
                        duration = h * 3600 + m * 60 + s + ms / 100
                if progress_callback and "time=" in line:
                    import re
                    match = re.search(r"time=(\d+):(\d+):(\d+)\.(\d+)", line)
                    if match and duration:
                        h, m, s, ms = map(int, match.groups())
                        current = h * 3600 + m * 60 + s + ms / 100
                        progress_callback(min(current / duration, 1.0))
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
        except FileNotFoundError as exc:
            raise RuntimeError(f"FFmpeg executable not found: {exc}") from exc

    @staticmethod
    def _ffmpeg_jpeg_quality(quality: int) -> list[str]:
        q = int(max(1, min(100, quality)))
        return ["-qscale:v", str(q)]

    @staticmethod
    def _ffmpeg_png_args(quality: int) -> list[str]:
        return ["-compression_level", str(max(0, min(9, 9 - quality // 11)))]

    @staticmethod
    def _ffmpeg_webp_args(quality: int) -> list[str]:
        q = int(max(1, min(100, quality)))
        return ["-quality", str(q), "-lossless", "0"]

    @staticmethod
    def _ffmpeg_tiff_args(quality: int) -> list[str]:
        return ["-compression_algo", "lzw"]

    @staticmethod
    def _ffmpeg_pdf_args(quality: int) -> list[str]:
        return ["-frames:v", "1"]
