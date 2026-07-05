from __future__ import annotations

from pathlib import Path

import pytest

from heic_converter_pro.app.services.file_service import FileService
from heic_converter_pro.app.services.filename_generator import FilenameGenerator, RenameRule


class TestFileService:
    def test_is_heic_file(self) -> None:
        assert FileService.is_heic_file(Path("test.heic"))
        assert FileService.is_heic_file(Path("test.HEIC"))
        assert FileService.is_heic_file(Path("test.heif"))
        assert not FileService.is_heic_file(Path("test.jpg"))
        assert not FileService.is_heic_file(Path("test.png"))

    def test_generate_output_path_same_folder(self) -> None:
        source = Path("/photos/test.heic")
        result = FileService.generate_output_path(source, "jpg", "{name}_converted")
        assert result.parent == source.parent
        assert result.name == "test_converted.jpg"

    def test_generate_output_path_custom_folder(self) -> None:
        source = Path("/photos/test.heic")
        output_dir = Path("/output")
        result = FileService.generate_output_path(
            source, "png", "{name}", output_dir=output_dir
        )
        assert result.parent == output_dir
        assert result.name == "test.png"

    def test_generate_output_path_with_counter(self) -> None:
        source = Path("/photos/test.heic")
        result = FileService.generate_output_path(source, "jpg", "{name}_{counter}", counter=3)
        assert result.name == "test_3.jpg"


class TestFilenameGenerator:
    def test_template_basic(self) -> None:
        source = Path("test.heic")
        result = FilenameGenerator.generate(source, "{name}_converted")
        assert result == "test_converted"

    def test_template_with_counter(self) -> None:
        source = Path("test.heic")
        result = FilenameGenerator.generate(source, "{name}_{counter}", counter=5)
        assert result == "test_005"

    def test_rename_rules(self) -> None:
        source = Path("IMG_0001.heic")
        rules = RenameRule(
            prefix="Vacation_",
            use_counter=True,
            counter_start=1,
            counter_digits=3,
            original_name=False,
        )
        result = FilenameGenerator.generate(source, rules=rules, counter=1)
        assert "Vacation_" in result
        assert "001" in result

    def test_rename_rules_with_date(self) -> None:
        from datetime import datetime
        source = Path("test.heic")
        rules = RenameRule(
            use_date=True,
            date_format="%Y%m%d",
            original_name=True,
        )
        result = FilenameGenerator.generate(source, rules=rules, counter=0)
        assert datetime.now().strftime("%Y%m%d") in result
        assert "test" in result
