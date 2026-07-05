from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from heic_converter_pro.app.models.conversion_task import ConversionTask, TaskStatus
from heic_converter_pro.app.models.settings import AppSettings, ExportFormat, ThemeMode, OutputMode


class TestConversionTask:
    def test_default_creation(self) -> None:
        task = ConversionTask(source_path=Path("test.heic"))
        assert task.status == TaskStatus.PENDING
        assert task.progress == 0.0
        assert task.source_path.name == "test.heic"

    def test_status_enum_values(self) -> None:
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"

    def test_size_reduction(self) -> None:
        task = ConversionTask(source_path=Path("test.heic"))
        task.original_size = 1000
        task.output_size = 500
        assert task.size_reduction == 50.0

    def test_size_reduction_none(self) -> None:
        task = ConversionTask(source_path=Path("test.heic"))
        assert task.size_reduction is None


class TestAppSettings:
    def test_default_values(self) -> None:
        settings = AppSettings()
        assert settings.theme == ThemeMode.SYSTEM
        assert settings.export_format == ExportFormat.JPG
        assert settings.jpeg_quality == 95

    def test_save_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            settings = AppSettings(theme=ThemeMode.DARK, export_format=ExportFormat.PNG, jpeg_quality=85)
            settings.save(path)
            assert path.exists()

            loaded = AppSettings.load(path)
            assert loaded.theme == ThemeMode.DARK
            assert loaded.export_format == ExportFormat.PNG
            assert loaded.jpeg_quality == 85

    def test_load_missing_file(self) -> None:
        settings = AppSettings.load(Path("nonexistent.json"))
        assert settings.theme == ThemeMode.SYSTEM

    def test_load_corrupted_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text("invalid json", encoding="utf-8")
            settings = AppSettings.load(path)
            assert settings.theme == ThemeMode.SYSTEM

    def test_enum_values(self) -> None:
        assert ExportFormat.JPG.value == "jpg"
        assert ExportFormat.PNG.value == "png"
        assert ExportFormat.WEBP.value == "webp"
        assert ThemeMode.LIGHT.value == "light"
        assert ThemeMode.DARK.value == "dark"
        assert OutputMode.SAME_FOLDER.value == "same_folder"
