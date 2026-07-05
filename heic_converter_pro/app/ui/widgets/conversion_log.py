from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QPushButton,
    QLabel,
    QFontDialog,
    QFileDialog,
    QCheckBox,
)

from heic_converter_pro.app.models.conversion_task import ConversionTask, TaskStatus
from heic_converter_pro.app.services.language_service import LanguageService

logger = logging.getLogger(__name__)


class ConversionLog(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._ls = LanguageService()
        self._setup_ui()

    def retranslate(self) -> None:
        t = self._ls.get
        self._title.setText(t("log.title"))
        self._auto_scroll.setText(t("log.auto_scroll"))
        self._clear_btn.setText(t("log.clear"))
        self._export_btn.setText(t("log.export"))

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        self._title = QLabel("Conversion Log")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        self._title.setFont(title_font)
        header_layout.addWidget(self._title)
        header_layout.addStretch()

        self._auto_scroll = QCheckBox("Auto-scroll")
        self._auto_scroll.setChecked(True)
        header_layout.addWidget(self._auto_scroll)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.clicked.connect(self.clear_log)
        header_layout.addWidget(self._clear_btn)

        self._export_btn = QPushButton("Export Log")
        self._export_btn.clicked.connect(self._export_log)
        header_layout.addWidget(self._export_btn)

        layout.addLayout(header_layout)

        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(10000)
        self._log.setFont(QFont("Consolas", 9))
        self._log.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self._log)

    def log_message(self, message: str, level: str = "INFO") -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = {
            "INFO": "gray",
            "SUCCESS": "green",
            "WARNING": "orange",
            "ERROR": "red",
        }.get(level, "gray")
        html = (
            f'<span style="color: {color};">'
            f"[{timestamp}] [{level}] {message}</span><br>"
        )
        self._log.appendHtml(html)
        if self._auto_scroll.isChecked():
            self._log.moveCursor(QTextCursor.MoveOperation.End)

    def log_task(self, task: ConversionTask) -> None:
        if task.status == TaskStatus.COMPLETED:
            reduction = ""
            if task.size_reduction is not None:
                sign = "-" if task.size_reduction >= 0 else "+"
                reduction = f" ({sign}{abs(task.size_reduction):.1f}%)"
            self.log_message(
                f"✓ {task.filename} → {task.output_path.name} "
                f"in {task.elapsed_time:.2f}s{reduction}",
                "SUCCESS",
            )
        elif task.status == TaskStatus.FAILED:
            self.log_message(
                f"✗ {task.filename}: {task.error_message}",
                "ERROR",
            )
        elif task.status == TaskStatus.CANCELLED:
            self.log_message(
                f"— {task.filename}: Cancelled",
                "WARNING",
            )
        elif task.status == TaskStatus.SKIPPED:
            self.log_message(
                f"→ {task.filename}: Skipped",
                "WARNING",
            )

    def log_info(self, message: str) -> None:
        self.log_message(message, "INFO")

    def log_error(self, message: str) -> None:
        self.log_message(message, "ERROR")

    def log_success(self, message: str) -> None:
        self.log_message(message, "SUCCESS")

    def clear_log(self) -> None:
        self._log.clear()

    def _export_log(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Conversion Log",
            "conversion_log.txt",
            "Text Files (*.txt);;All Files (*.*)",
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self._log.toPlainText())
                self.log_info(f"Log exported to {file_path}")
            except OSError as exc:
                self.log_error(f"Failed to export log: {exc}")
