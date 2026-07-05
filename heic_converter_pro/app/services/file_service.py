from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Iterator, List, Optional

logger = logging.getLogger(__name__)

HEIC_EXTENSIONS = {".heic", ".heif", ".heics", ".heifs"}
SUPPORTED_OUTPUT = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif", ".bmp", ".pdf"}


class FileService:
    @staticmethod
    def is_heic_file(path: Path) -> bool:
        return path.suffix.lower() in HEIC_EXTENSIONS

    @staticmethod
    def is_supported_output(extension: str) -> bool:
        return extension.lower() in SUPPORTED_OUTPUT

    @staticmethod
    def find_heic_files(paths: List[Path]) -> List[Path]:
        found: List[Path] = []
        for path in paths:
            resolved = path.resolve()
            if resolved.is_file():
                if FileService.is_heic_file(resolved):
                    found.append(resolved)
            elif resolved.is_dir():
                found.extend(FileService._scan_directory(resolved))
        return FileService._deduplicate(found)

    @staticmethod
    def _scan_directory(directory: Path) -> Iterator[Path]:
        try:
            for entry in os.scandir(str(directory)):
                entry_path = Path(entry.path)
                if entry.is_file() and FileService.is_heic_file(entry_path):
                    yield entry_path
                elif entry.is_dir() and not entry.name.startswith("."):
                    yield from FileService._scan_directory(entry_path)
        except PermissionError as exc:
            logger.warning("Permission denied scanning %s: %s", directory, exc)
        except OSError as exc:
            logger.warning("Error scanning %s: %s", directory, exc)

    @staticmethod
    def _deduplicate(paths: List[Path]) -> List[Path]:
        seen = set()
        result = []
        for p in paths:
            resolved = str(p.resolve())
            if resolved not in seen:
                seen.add(resolved)
                result.append(p)
        return result

    @staticmethod
    def generate_output_path(
        source: Path,
        output_format: str,
        template: str,
        output_dir: Optional[Path] = None,
        overwrite: bool = False,
        counter: int = 0,
    ) -> Path:
        name = source.stem
        formatted_name = template.replace("{name}", name).replace("{counter}", str(counter))
        if counter > 0 and "{counter}" not in template:
            formatted_name = f"{formatted_name}_{counter}"
        filename = f"{formatted_name}.{output_format.lower().replace('jpeg', 'jpg')}"

        if output_dir is None:
            output_dir = source.parent

        output_path = output_dir / filename

        if not overwrite:
            output_path = FileService._resolve_conflict(output_path)

        return output_path

    @staticmethod
    def _resolve_conflict(path: Path) -> Path:
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1

    @staticmethod
    def ensure_output_dir(path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_file_size(path: Path) -> int:
        try:
            return path.stat().st_size
        except OSError:
            return 0
