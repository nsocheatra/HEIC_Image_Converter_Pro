from __future__ import annotations

import enum
import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


class ExportFormat(str, enum.Enum):
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    PDF = "pdf"


class ThemeMode(str, enum.Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class OutputMode(str, enum.Enum):
    SAME_FOLDER = "same_folder"
    CUSTOM_FOLDER = "custom_folder"
    ASK_EVERY = "ask_every"


@dataclass
class AppSettings:
    theme: ThemeMode = ThemeMode.SYSTEM
    language: str = "en"
    export_format: ExportFormat = ExportFormat.JPG
    jpeg_quality: int = 95
    webp_quality: int = 90
    output_mode: OutputMode = OutputMode.SAME_FOLDER
    custom_output_folder: str = ""
    resize_enabled: bool = False
    resize_width: int = 1920
    resize_height: int = 1080
    resize_keep_aspect: bool = True
    rotation: int = 0
    flip_horizontal: bool = False
    flip_vertical: bool = False
    filename_template: str = "{name}_converted"
    preserve_exif: bool = True
    preserve_gps: bool = True
    preserve_icc: bool = True
    preserve_orientation: bool = True
    overwrite_existing: bool = False
    keep_original: bool = True
    brightness: float = 1.0
    contrast: float = 1.0
    sharpness: float = 1.0
    saturation: float = 1.0
    gamma: float = 1.0
    blur_radius: int = 0
    auto_enhance: bool = False
    strip_metadata: bool = False
    watermark_text: str = ""
    watermark_position: str = "bottom_right"
    watermark_opacity: int = 128
    border_width: int = 0
    border_color: str = "000000"
    max_threads: int = 4
    rename_enabled: bool = False
    rename_prefix: str = ""
    rename_suffix: str = ""
    rename_counter_start: int = 1
    rename_counter_digits: int = 3
    rename_use_date: bool = False
    rename_date_format: str = "%Y%m%d"
    rename_find: str = ""
    rename_replace: str = ""
    use_ffmpeg_fallback: bool = True
    watch_folder_enabled: bool = False
    watch_folder_path: str = ""
    recent_files: list[str] = field(default_factory=list)
    recent_folders: list[str] = field(default_factory=list)
    window_geometry: Optional[dict] = None
    splitter_sizes: list[int] = field(default_factory=lambda: [300, 400, 300])

    @classmethod
    def load(cls, path: Path) -> AppSettings:
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
            filtered = {k: v for k, v in data.items() if k in valid_keys}
            enum_fields = {
                "theme": ThemeMode,
                "export_format": ExportFormat,
                "output_mode": OutputMode,
            }
            for field_name, enum_type in enum_fields.items():
                if field_name in filtered and isinstance(filtered[field_name], str):
                    filtered[field_name] = enum_type(filtered[field_name])
            return cls(**filtered)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            logging.getLogger(__name__).warning("Failed to load settings: %s", exc)
            return cls()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = asdict(self)
        data["theme"] = self.theme.value
        data["export_format"] = self.export_format.value
        data["output_mode"] = self.output_mode.value
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
