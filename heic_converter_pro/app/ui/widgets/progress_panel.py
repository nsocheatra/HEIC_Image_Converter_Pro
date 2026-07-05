from __future__ import annotations

import logging
import time
from typing import Optional

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QPushButton,
    QLabel,
    QFrame,
)

from heic_converter_pro.app.models.conversion_task import ConversionTask, TaskStatus

logger = logging.getLogger(__name__)


class ProgressPanel(QFrame):
    cancelled = Signal()
    retry_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._start_time: Optional[float] = None
        self._processed_count = 0
        self._total_count = 0
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_eta)
        self.setVisible(False)

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFixedHeight(24)
        layout.addWidget(self._progress_bar)

        info_layout = QHBoxLayout()

        self._status_label = QLabel("Ready")
        status_font = QFont()
        status_font.setPointSize(10)
        self._status_label.setFont(status_font)
        info_layout.addWidget(self._status_label)

        info_layout.addStretch()

        self._eta_label = QLabel("")
        eta_font = QFont()
        eta_font.setPointSize(10)
        self._eta_label.setFont(eta_font)
        info_layout.addWidget(self._eta_label)

        info_layout.addStretch()

        self._count_label = QLabel("0 / 0")
        count_font = QFont()
        count_font.setPointSize(10)
        self._count_label.setFont(count_font)
        info_layout.addWidget(self._count_label)

        layout.addLayout(info_layout)

        btn_layout = QHBoxLayout()

        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.clicked.connect(self.cancelled.emit)
        btn_layout.addWidget(self._cancel_btn)

        self._retry_btn = QPushButton("Retry Failed")
        self._retry_btn.clicked.connect(self.retry_requested.emit)
        btn_layout.addWidget(self._retry_btn)

        layout.addLayout(btn_layout)

    def start_batch(self, total: int) -> None:
        self._start_time = time.time()
        self._processed_count = 0
        self._total_count = total
        self._progress_bar.setValue(0)
        self._progress_bar.setMaximum(total * 100)
        self._count_label.setText(f"0 / {total}")
        self._status_label.setText("Starting conversion...")
        self.setVisible(True)
        self._timer.start(500)

    def on_task_completed(self, task: ConversionTask) -> None:
        self._processed_count += 1
        progress_value = int((self._processed_count / max(self._total_count, 1)) * 100)
        self._progress_bar.setValue(progress_value)
        self._count_label.setText(f"{self._processed_count} / {self._total_count}")

        if task.status == TaskStatus.COMPLETED:
            self._status_label.setText(f"Converted: {task.filename}")
        elif task.status == TaskStatus.FAILED:
            self._status_label.setText(f"Failed: {task.filename}")
        elif task.status == TaskStatus.CANCELLED:
            self._status_label.setText(f"Cancelled: {task.filename}")

    def _update_eta(self) -> None:
        if self._processed_count == 0 or self._start_time is None:
            self._eta_label.setText("Calculating...")
            return
        elapsed = time.time() - self._start_time
        rate = self._processed_count / elapsed if elapsed > 0 else 0
        remaining = self._total_count - self._processed_count
        if rate > 0:
            eta_seconds = remaining / rate
            self._eta_label.setText(f"ETA: {self._format_eta(eta_seconds)}")
        else:
            self._eta_label.setText("ETA: --")

    def finish_batch(self) -> None:
        self._timer.stop()
        self._progress_bar.setValue(100)
        self._status_label.setText("Batch completed!")
        self._eta_label.setText("Done")

    def reset(self) -> None:
        self._timer.stop()
        self._progress_bar.setValue(0)
        self._status_label.setText("Ready")
        self._eta_label.setText("")
        self._count_label.setText("0 / 0")
        self.setVisible(False)

    @staticmethod
    def _format_eta(seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds / 60:.0f}m {seconds % 60:.0f}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
