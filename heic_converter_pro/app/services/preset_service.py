from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from heic_converter_pro.app.models.settings import AppSettings, ExportFormat

logger = logging.getLogger(__name__)

PRESETS_FILE = Path.home() / ".heic_converter_pro" / "presets.json"


@dataclass
class Preset:
    name: str
    export_format: str = "jpg"
    jpeg_quality: int = 95
    webp_quality: int = 90
    resize_enabled: bool = False
    resize_width: int = 1920
    resize_height: int = 1080
    resize_keep_aspect: bool = True
    rotation: int = 0
    flip_horizontal: bool = False
    flip_vertical: bool = False
    preserve_exif: bool = True
    preserve_icc: bool = True
    preserve_orientation: bool = True
    filename_template: str = "{name}_converted"

    @classmethod
    def from_settings(cls, name: str, settings: AppSettings) -> Preset:
        return cls(
            name=name,
            export_format=settings.export_format.value,
            jpeg_quality=settings.jpeg_quality,
            webp_quality=settings.webp_quality,
            resize_enabled=settings.resize_enabled,
            resize_width=settings.resize_width,
            resize_height=settings.resize_height,
            resize_keep_aspect=settings.resize_keep_aspect,
            rotation=settings.rotation,
            flip_horizontal=settings.flip_horizontal,
            flip_vertical=settings.flip_vertical,
            preserve_exif=settings.preserve_exif,
            preserve_icc=settings.preserve_icc,
            preserve_orientation=settings.preserve_orientation,
            filename_template=settings.filename_template,
        )

    def apply_to(self, settings: AppSettings) -> None:
        settings.export_format = ExportFormat(self.export_format)
        settings.jpeg_quality = self.jpeg_quality
        settings.webp_quality = self.webp_quality
        settings.resize_enabled = self.resize_enabled
        settings.resize_width = self.resize_width
        settings.resize_height = self.resize_height
        settings.resize_keep_aspect = self.resize_keep_aspect
        settings.rotation = self.rotation
        settings.flip_horizontal = self.flip_horizontal
        settings.flip_vertical = self.flip_vertical
        settings.preserve_exif = self.preserve_exif
        settings.preserve_icc = self.preserve_icc
        settings.preserve_orientation = self.preserve_orientation
        settings.filename_template = self.filename_template


class PresetService:
    def __init__(self) -> None:
        self._presets: list[Preset] = []
        self._load()

    @property
    def presets(self) -> list[Preset]:
        return self._presets

    def add(self, preset: Preset) -> None:
        self._presets = [p for p in self._presets if p.name != preset.name]
        self._presets.append(preset)
        self._save()

    def remove(self, name: str) -> bool:
        before = len(self._presets)
        self._presets = [p for p in self._presets if p.name != name]
        if len(self._presets) != before:
            self._save()
            return True
        return False

    def get(self, name: str) -> Optional[Preset]:
        for p in self._presets:
            if p.name == name:
                return p
        return None

    def _load(self) -> None:
        if PRESETS_FILE.exists():
            try:
                data = json.loads(PRESETS_FILE.read_text(encoding="utf-8"))
                self._presets = [Preset(**p) for p in data]
            except (json.JSONDecodeError, TypeError):
                self._presets = []

    def _save(self) -> None:
        PRESETS_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(p) for p in self._presets]
        PRESETS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
