from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from PIL import Image

from heic_converter_pro.app.media.ffmpeg_converter import FfmpegConverter

logger = logging.getLogger(__name__)

THUMB_CACHE_DIR = Path.home() / ".heic_converter_pro" / "thumb_cache"


class ThumbnailService:
    def __init__(self) -> None:
        THUMB_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, Path] = {}
        self._ffmpeg = FfmpegConverter()

    def get_thumbnail(self, image_path: Path, size: int = 256) -> Optional[Path]:
        cache_key = f"{image_path.stem}_{image_path.stat().st_mtime}_{size}"
        cached = THUMB_CACHE_DIR / f"{hash(cache_key)}.jpg"

        if cached.exists():
            return cached

        try:
            result = self._generate_thumbnail(image_path, cached, size)
            if result:
                self._cache[cache_key] = result
            return result
        except Exception as exc:
            logger.warning("Thumbnail failed for %s: %s", image_path.name, exc)
            return None

    def _generate_thumbnail(self, source: Path, output: Path, size: int) -> Optional[Path]:
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            pass

        try:
            with Image.open(str(source)) as img:
                img.thumbnail((size, size), Image.LANCZOS)
                if img.mode == "RGBA":
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, mask=img.split()[3])
                    img = bg
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                img.save(str(output), "JPEG", quality=85)
                return output
        except Exception as exc:
            logger.debug("Pillow thumbnail failed, trying FFmpeg: %s", exc)

        if self._ffmpeg.available:
            try:
                return self._ffmpeg.extract_thumbnail(source, output, size)
            except Exception as exc:
                logger.debug("FFmpeg thumbnail failed: %s", exc)

        return None

    @staticmethod
    def clear_cache() -> None:
        count = 0
        for f in THUMB_CACHE_DIR.iterdir():
            if f.is_file():
                f.unlink()
                count += 1
        logger.info("Cleared %d cached thumbnails", count)
