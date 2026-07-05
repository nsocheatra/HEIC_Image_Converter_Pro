from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional


class RenameRule:
    def __init__(
        self,
        prefix: str = "",
        suffix: str = "",
        use_counter: bool = True,
        counter_start: int = 1,
        counter_digits: int = 3,
        use_date: bool = False,
        use_camera_model: bool = False,
        date_format: str = "%Y%m%d",
        original_name: bool = True,
        find_text: str = "",
        replace_text: str = "",
    ) -> None:
        self.prefix = prefix
        self.suffix = suffix
        self.use_counter = use_counter
        self.counter_start = counter_start
        self.counter_digits = counter_digits
        self.use_date = use_date
        self.use_camera_model = use_camera_model
        self.date_format = date_format
        self.original_name = original_name
        self.find_text = find_text
        self.replace_text = replace_text


class FilenameGenerator:
    @staticmethod
    def generate(
        source: Path,
        template: str = "{name}_converted",
        counter: int = 0,
        counter_digits: int = 3,
        rules: Optional[RenameRule] = None,
    ) -> str:
        name = source.stem
        ext = source.suffix

        if rules:
            return FilenameGenerator._apply_rules(source, rules, counter)
        else:
            return FilenameGenerator._apply_template(template, name, counter, counter_digits)

    @staticmethod
    def _apply_template(template: str, name: str, counter: int, digits: int) -> str:
        result = template.replace("{name}", name)
        result = result.replace("{counter}", str(counter).zfill(digits))
        result = result.replace("{date}", datetime.now().strftime("%Y%m%d"))
        result = result.replace("{time}", datetime.now().strftime("%H%M%S"))
        return result

    @staticmethod
    def _apply_rules(source: Path, rules: RenameRule, counter: int) -> str:
        name = source.stem
        ext = source.suffix

        parts = []

        if rules.prefix:
            parts.append(rules.prefix)

        if rules.use_date:
            parts.append(datetime.now().strftime(rules.date_format))
            if rules.use_counter or rules.original_name:
                parts.append("_")

        if rules.original_name:
            nm = name
            if rules.find_text and rules.replace_text:
                nm = re.sub(re.escape(rules.find_text), rules.replace_text, nm)
            parts.append(nm)

        if rules.use_counter:
            if rules.original_name:
                parts.append("_")
            parts.append(str(counter).zfill(rules.counter_digits))

        if rules.suffix:
            parts.append(rules.suffix)

        result = "".join(parts) if parts else name
        return result + ext
