from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

HISTORY_FILE = Path.home() / ".heic_converter_pro" / "history.json"


@dataclass
class HistoryEntry:
    source_path: str
    output_path: str
    source_format: str = ""
    output_format: str = ""
    status: str = "success"
    duration: float = 0.0
    source_size: int = 0
    output_size: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class HistoryService:
    MAX_ENTRIES = 500

    def __init__(self) -> None:
        self._entries: list[HistoryEntry] = []
        self._load()

    def add_entry(self, entry: HistoryEntry) -> None:
        self._entries.insert(0, entry)
        if len(self._entries) > self.MAX_ENTRIES:
            self._entries = self._entries[: self.MAX_ENTRIES]
        self._save()

    def get_entries(self, limit: int = 100) -> list[HistoryEntry]:
        return self._entries[:limit]

    def clear(self) -> None:
        self._entries.clear()
        self._save()

    def export_csv(self, path: Path) -> None:
        import csv
        with open(str(path), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Timestamp", "Source", "Output", "Source Format",
                "Output Format", "Status", "Duration (s)",
                "Source Size (bytes)", "Output Size (bytes)",
            ])
            for e in self._entries:
                writer.writerow([
                    e.timestamp, e.source_path, e.output_path,
                    e.source_format, e.output_format, e.status,
                    e.duration, e.source_size, e.output_size,
                ])
        logger.info("History exported to %s", path)

    def get_stats(self) -> dict:
        total = len(self._entries)
        successes = sum(1 for e in self._entries if e.status == "success")
        failures = total - successes
        total_src_size = sum(e.source_size for e in self._entries)
        total_out_size = sum(e.output_size for e in self._entries)
        return {
            "total": total,
            "successes": successes,
            "failures": failures,
            "total_source_size": total_src_size,
            "total_output_size": total_out_size,
            "savings_percent": (
                (1 - total_out_size / max(total_src_size, 1)) * 100
                if total_src_size > 0 else 0
            ),
        }

    def _load(self) -> None:
        if HISTORY_FILE.exists():
            try:
                data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
                self._entries = [HistoryEntry(**e) for e in data]
            except (json.JSONDecodeError, TypeError):
                self._entries = []

    def _save(self) -> None:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(e) for e in self._entries]
        HISTORY_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
