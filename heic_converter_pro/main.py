from __future__ import annotations

import sys
import os
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor, QPen, QFontMetrics

from heic_converter_pro.app.logger import setup_logging
from heic_converter_pro.app.main_window import MainWindow


def _create_splash() -> QSplashScreen:
    pixmap = QPixmap(500, 320)
    pixmap.fill(QColor(30, 30, 30))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setPen(Qt.GlobalColor.white)
    title_font = QFont("Segoe UI", 22, QFont.Weight.Bold)
    painter.setFont(title_font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "HEIC Image Converter Pro")

    sub_font = QFont("Segoe UI", 11)
    painter.setFont(sub_font)
    painter.setPen(QColor(180, 180, 180))
    subtitle_rect = pixmap.rect().adjusted(0, 50, 0, -60)
    painter.drawText(subtitle_rect, Qt.AlignmentFlag.AlignCenter, "Loading...")

    author_font = QFont("Segoe UI", 10)
    painter.setFont(author_font)
    painter.setPen(QColor(0, 120, 212))
    author_rect = pixmap.rect().adjusted(0, 0, 0, -20)
    painter.drawText(author_rect, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, "Create By XiaoPang (Stra)")

    painter.end()

    splash = QSplashScreen(pixmap, Qt.WindowType.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
    return splash


def main() -> None:
    setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName("HEIC Image Converter Pro")
    app.setOrganizationName("HEIC Converter")
    app.setApplicationVersion("1.0.0")

    app.setStyle("Fusion")

    default_font = QFont("Segoe UI", 9)
    default_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(default_font)

    splash = _create_splash()
    splash.show()
    app.processEvents()

    window = MainWindow()
    window.show()
    splash.finish(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
