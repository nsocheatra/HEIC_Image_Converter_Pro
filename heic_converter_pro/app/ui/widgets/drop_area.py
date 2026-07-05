from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

logger = logging.getLogger(__name__)


class DropArea(QWidget):
    files_dropped = Signal(list)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._drag_over = False
        self._setup_ui()
        self.setAcceptDrops(True)

    def _setup_ui(self) -> None:
        self.setMinimumHeight(200)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._icon_label = QLabel("📁")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(48)
        self._icon_label.setFont(icon_font)

        self._text_label = QLabel(
            "Drag & Drop HEIC/HEIF files or folders here\n"
            "or click 'Add Files' to browse"
        )
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._text_label.setWordWrap(True)
        text_font = QFont()
        text_font.setPointSize(12)
        self._text_label.setFont(text_font)

        self._count_label = QLabel("")
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_font = QFont()
        count_font.setPointSize(10)
        self._count_label.setFont(count_font)

        layout.addWidget(self._icon_label)
        layout.addWidget(self._text_label)
        layout.addWidget(self._count_label)

    def set_file_count(self, count: int) -> None:
        if count > 0:
            self._count_label.setText(f"{count} file(s) loaded")
            self._count_label.setVisible(True)
        else:
            self._count_label.setVisible(False)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            self._drag_over = True
            event.acceptProposedAction()
            self.update()

    def dragLeaveEvent(self, event) -> None:
        self._drag_over = False
        self.update()

    def dropEvent(self, event: QDropEvent) -> None:
        self._drag_over = False
        self.update()
        urls = event.mimeData().urls()
        paths = [Path(url.toLocalFile()) for url in urls if url.isLocalFile()]
        if paths:
            self.files_dropped.emit(paths)
            logger.info("Dropped %d paths", len(paths))

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._drag_over:
            color = QColor(0, 120, 212, 60)
            border_color = QColor(0, 120, 212)
        else:
            color = QColor(0, 0, 0, 20)
            border_color = QColor(0, 0, 0, 60)

        painter.setBrush(color)
        pen = QPen(border_color, 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        rect = self.rect().adjusted(4, 4, -4, -4)
        painter.drawRoundedRect(rect, 12, 12)
        painter.end()
