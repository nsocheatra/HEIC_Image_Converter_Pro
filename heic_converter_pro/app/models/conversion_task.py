from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class TaskStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class ConversionTask:
    source_path: Path
    output_path: Optional[Path] = None
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    error_message: str = ""
    original_size: int = 0
    output_size: int = 0
    elapsed_time: float = 0.0
    metadata_preserved: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.source_path, str):
            self.source_path = Path(self.source_path)
        if isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)

    @property
    def filename(self) -> str:
        return self.source_path.name

    @property
    def stem(self) -> str:
        return self.source_path.stem

    @property
    def size_reduction(self) -> Optional[float]:
        if self.original_size > 0 and self.output_size > 0:
            return (1 - self.output_size / self.original_size) * 100
        return None
