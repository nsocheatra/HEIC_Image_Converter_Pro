from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

logger = logging.getLogger(__name__)


class DropArea(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setMinimumHeight(200)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._icon_label = QLabel("📁")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(48)
        self._icon_label.setFont(icon_font)

        self._text_label = QLabel("Add HEIC/HEIF files using 'Add Files' button")
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

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(0, 0, 0, 20))
        pen = QPen(QColor(0, 0, 0, 60), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        rect = self.rect().adjusted(4, 4, -4, -4)
        painter.drawRoundedRect(rect, 12, 12)
        painter.end()
