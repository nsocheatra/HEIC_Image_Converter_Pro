from __future__ import annotations

import sys
import os
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from heic_converter_pro.app.logger import setup_logging
from heic_converter_pro.app.main_window import MainWindow


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

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
