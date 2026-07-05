from __future__ import annotations

import logging
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QWidget,
    QFormLayout,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QLabel,
    QGroupBox,
    QDialogButtonBox,
)

from heic_converter_pro.app.config import ConfigManager
from heic_converter_pro.app.models.settings import ThemeMode

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._config = ConfigManager()
        self._settings = self._config.get()
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_general_tab(), "General")
        self._tabs.addTab(self._build_processing_tab(), "Processing")
        layout.addWidget(self._tabs)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self._apply_settings
        )
        layout.addWidget(button_box)

    def _build_general_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Appearance")
        form = QFormLayout(group)
        self._theme_combo = QComboBox()
        self._theme_combo.addItem("Light", ThemeMode.LIGHT.value)
        self._theme_combo.addItem("Dark", ThemeMode.DARK.value)
        self._theme_combo.addItem("System", ThemeMode.SYSTEM.value)
        form.addRow("Theme:", self._theme_combo)

        self._language_combo = QComboBox()
        self._language_combo.addItem("English", "en")
        self._language_combo.addItem("Khmer", "km")
        self._language_combo.addItem("中文", "zh")
        self._language_combo.addItem("日本語", "ja")
        form.addRow("Language:", self._language_combo)
        layout.addWidget(group)

        group2 = QGroupBox("Startup")
        form2 = QFormLayout(group2)
        self._restore_window_cb = QCheckBox("Restore window position")
        self._restore_window_cb.setChecked(True)
        form2.addRow("", self._restore_window_cb)
        layout.addWidget(group2)

        layout.addStretch()
        return widget

    def _build_processing_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("Performance")
        form = QFormLayout(group)
        self._threads_spin = QSpinBox()
        self._threads_spin.setRange(1, 32)
        form.addRow("Max threads:", self._threads_spin)
        layout.addWidget(group)

        group2 = QGroupBox("File Handling")
        form2 = QFormLayout(group2)
        self._keep_original_cb = QCheckBox("Keep original files after conversion")
        self._keep_original_cb.setChecked(True)
        form2.addRow("", self._keep_original_cb)
        layout.addWidget(group2)

        layout.addStretch()
        return widget

    def _load_settings(self) -> None:
        idx = self._theme_combo.findData(self._settings.theme.value)
        if idx >= 0:
            self._theme_combo.setCurrentIndex(idx)
        idx = self._language_combo.findData(self._settings.language)
        if idx >= 0:
            self._language_combo.setCurrentIndex(idx)
        self._threads_spin.setValue(self._settings.max_threads)
        self._keep_original_cb.setChecked(self._settings.keep_original)

    def _apply_settings(self) -> None:
        self._settings.theme = ThemeMode(self._theme_combo.currentData())
        self._settings.language = self._language_combo.currentData()
        self._settings.max_threads = self._threads_spin.value()
        self._settings.keep_original = self._keep_original_cb.isChecked()
        self._config.save()
        logger.info("Settings applied")

    def accept(self) -> None:
        self._apply_settings()
        super().accept()

    @property
    def theme_changed(self) -> bool:
        old_theme = self._config.get().theme
        new_theme = ThemeMode(self._theme_combo.currentData())
        return old_theme != new_theme
