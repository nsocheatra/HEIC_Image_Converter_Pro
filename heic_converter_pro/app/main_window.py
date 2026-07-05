from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QByteArray, QSize, QTimer
from PySide6.QtGui import QAction, QIcon, QKeySequence, QFont, QColor
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QSplitter,
    QVBoxLayout,
    QHBoxLayout,
    QMenuBar,
    QMenu,
    QStatusBar,
    QToolBar,
    QToolButton,
    QLabel,
    QFileDialog,
    QMessageBox,
    QApplication,
    QSizePolicy,
)

from heic_converter_pro.app.config import ConfigManager
from heic_converter_pro.app.core.batch_processor import BatchProcessor
from heic_converter_pro.app.core.converter import HeicConverter
from heic_converter_pro.app.media.media_detector import MediaDetector
from heic_converter_pro.app.models.conversion_task import ConversionTask, TaskStatus
from heic_converter_pro.app.models.settings import AppSettings, ThemeMode
from heic_converter_pro.app.services.file_service import FileService
from heic_converter_pro.app.services.history_service import HistoryService, HistoryEntry
from heic_converter_pro.app.services.language_service import LanguageService
from heic_converter_pro.app.services.preset_service import PresetService
from heic_converter_pro.app.services.update_service import UpdateService
from heic_converter_pro.app.services.watch_folder import WatchFolderService
from heic_converter_pro.app.ui.widgets.drop_area import DropArea
from heic_converter_pro.app.ui.widgets.file_list import FileListWidget
from heic_converter_pro.app.ui.widgets.progress_panel import ProgressPanel
from heic_converter_pro.app.ui.widgets.conversion_log import ConversionLog
from heic_converter_pro.app.ui.widgets.settings_panel import SettingsPanel
from heic_converter_pro.app.ui.dialogs.settings_dialog import SettingsDialog
from heic_converter_pro.app.ui.dialogs.about_dialog import AboutDialog

logger = logging.getLogger(__name__)

LIGHT_THEME = """
QMainWindow { background-color: #f3f3f3; }
QWidget { background-color: #f9f9f9; color: #1e1e1e; font-family: "Segoe UI", "Arial", sans-serif; }
QMenuBar { background-color: #f3f3f3; border-bottom: 1px solid #e0e0e0; padding: 2px; }
QMenuBar::item { padding: 6px 12px; background: transparent; border-radius: 4px; }
QMenuBar::item:selected { background-color: #e0e0e0; }
QMenu { background-color: #ffffff; border: 1px solid #d0d0d0; padding: 4px; }
QMenu::item { padding: 6px 28px 6px 20px; border-radius: 4px; }
QMenu::item:selected { background-color: #0078d4; color: white; }
QToolBar { background-color: #f3f3f3; border-bottom: 1px solid #e0e0e0; spacing: 4px; padding: 4px; }
QToolButton { padding: 6px 12px; border-radius: 4px; border: 1px solid transparent; }
QToolButton:hover { background-color: #e0e0e0; border-color: #d0d0d0; }
QToolButton:checked { background-color: #0078d4; color: white; }
QSplitter::handle { background-color: #e0e0e0; width: 2px; }
QGroupBox { font-weight: bold; border: 1px solid #e0e0e0; border-radius: 6px; margin-top: 12px; padding: 16px 12px 12px 12px; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QPushButton { padding: 6px 16px; border-radius: 4px; border: 1px solid #d0d0d0; background-color: #ffffff; }
QPushButton:hover { background-color: #e8e8e8; border-color: #b0b0b0; }
QPushButton:pressed { background-color: #d0d0d0; }
QPushButton:disabled { color: #a0a0a0; background-color: #f0f0f0; }
QProgressBar { border: 1px solid #d0d0d0; border-radius: 4px; text-align: center; background-color: #e8e8e8; }
QProgressBar::chunk { background-color: #0078d4; border-radius: 3px; }
QListWidget { border: 1px solid #e0e0e0; border-radius: 4px; background-color: #ffffff; alternate-background-color: #f5f5f5; }
QListWidget::item { padding: 4px 8px; border-radius: 2px; }
QListWidget::item:selected { background-color: #0078d4; color: white; }
QComboBox { padding: 4px 8px; border: 1px solid #d0d0d0; border-radius: 4px; background-color: #ffffff; }
QComboBox:hover { border-color: #0078d4; }
QComboBox::drop-down { border: none; width: 24px; }
QSpinBox { padding: 4px 8px; border: 1px solid #d0d0d0; border-radius: 4px; background-color: #ffffff; }
QSpinBox:hover { border-color: #0078d4; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 3px; border: 2px solid #b0b0b0; }
QCheckBox::indicator:checked { background-color: #0078d4; border-color: #0078d4; }
QSlider::groove:horizontal { height: 6px; background: #e0e0e0; border-radius: 3px; }
QSlider::handle:horizontal { background: #0078d4; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }
QSlider::sub-page:horizontal { background: #0078d4; border-radius: 3px; }
QLineEdit { padding: 4px 8px; border: 1px solid #d0d0d0; border-radius: 4px; background-color: #ffffff; }
QLineEdit:hover { border-color: #0078d4; }
QPlainTextEdit { border: 1px solid #e0e0e0; border-radius: 4px; background-color: #ffffff; }
QScrollArea { border: none; }
QStatusBar { background-color: #f3f3f3; border-top: 1px solid #e0e0e0; }
QTabWidget::pane { border: 1px solid #e0e0e0; border-radius: 4px; background-color: #ffffff; }
QTabBar::tab { padding: 8px 16px; border: 1px solid transparent; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; }
QTabBar::tab:selected { background-color: #ffffff; border-color: #e0e0e0; }
QTabBar::tab:hover { background-color: #e8e8e8; }
QScrollBar:vertical { width: 10px; background: #f0f0f0; border-radius: 5px; }
QScrollBar::handle:vertical { background: #c0c0c0; border-radius: 5px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #a0a0a0; }
QScrollBar:horizontal { height: 10px; background: #f0f0f0; border-radius: 5px; }
QScrollBar::handle:horizontal { background: #c0c0c0; border-radius: 5px; min-width: 24px; }
QScrollBar::handle:horizontal:hover { background: #a0a0a0; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
"""

DARK_THEME = """
QMainWindow { background-color: #1e1e1e; }
QWidget { background-color: #252526; color: #d4d4d4; font-family: "Segoe UI", "Arial", sans-serif; }
QMenuBar { background-color: #2d2d2d; border-bottom: 1px solid #3c3c3c; padding: 2px; }
QMenuBar::item { padding: 6px 12px; background: transparent; border-radius: 4px; }
QMenuBar::item:selected { background-color: #3c3c3c; }
QMenu { background-color: #2d2d2d; border: 1px solid #3c3c3c; padding: 4px; }
QMenu::item { padding: 6px 28px 6px 20px; border-radius: 4px; }
QMenu::item:selected { background-color: #0078d4; color: white; }
QToolBar { background-color: #2d2d2d; border-bottom: 1px solid #3c3c3c; spacing: 4px; padding: 4px; }
QToolButton { padding: 6px 12px; border-radius: 4px; border: 1px solid transparent; color: #d4d4d4; }
QToolButton:hover { background-color: #3c3c3c; border-color: #555555; }
QToolButton:checked { background-color: #0078d4; color: white; }
QSplitter::handle { background-color: #3c3c3c; width: 2px; }
QGroupBox { font-weight: bold; border: 1px solid #3c3c3c; border-radius: 6px; margin-top: 12px; padding: 16px 12px 12px 12px; color: #d4d4d4; }
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
QPushButton { padding: 6px 16px; border-radius: 4px; border: 1px solid #3c3c3c; background-color: #333333; color: #d4d4d4; }
QPushButton:hover { background-color: #404040; border-color: #555555; }
QPushButton:pressed { background-color: #505050; }
QPushButton:disabled { color: #555555; background-color: #2d2d2d; }
QProgressBar { border: 1px solid #3c3c3c; border-radius: 4px; text-align: center; background-color: #333333; color: #d4d4d4; }
QProgressBar::chunk { background-color: #0078d4; border-radius: 3px; }
QListWidget { border: 1px solid #3c3c3c; border-radius: 4px; background-color: #1e1e1e; alternate-background-color: #2a2a2a; color: #d4d4d4; }
QListWidget::item { padding: 4px 8px; border-radius: 2px; }
QListWidget::item:selected { background-color: #0078d4; color: white; }
QComboBox { padding: 4px 8px; border: 1px solid #3c3c3c; border-radius: 4px; background-color: #333333; color: #d4d4d4; }
QComboBox:hover { border-color: #0078d4; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView { background-color: #2d2d2d; color: #d4d4d4; }
QSpinBox { padding: 4px 8px; border: 1px solid #3c3c3c; border-radius: 4px; background-color: #333333; color: #d4d4d4; }
QSpinBox:hover { border-color: #0078d4; }
QCheckBox { spacing: 8px; color: #d4d4d4; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 3px; border: 2px solid #555555; }
QCheckBox::indicator:checked { background-color: #0078d4; border-color: #0078d4; }
QSlider::groove:horizontal { height: 6px; background: #3c3c3c; border-radius: 3px; }
QSlider::handle:horizontal { background: #0078d4; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }
QSlider::sub-page:horizontal { background: #0078d4; border-radius: 3px; }
QLineEdit { padding: 4px 8px; border: 1px solid #3c3c3c; border-radius: 4px; background-color: #333333; color: #d4d4d4; }
QLineEdit:hover { border-color: #0078d4; }
QPlainTextEdit { border: 1px solid #3c3c3c; border-radius: 4px; background-color: #1e1e1e; color: #d4d4d4; }
QScrollArea { border: none; }
QStatusBar { background-color: #2d2d2d; border-top: 1px solid #3c3c3c; color: #d4d4d4; }
QTabWidget::pane { border: 1px solid #3c3c3c; border-radius: 4px; background-color: #252526; }
QTabBar::tab { padding: 8px 16px; border: 1px solid transparent; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; color: #d4d4d4; }
QTabBar::tab:selected { background-color: #252526; border-color: #3c3c3c; }
QTabBar::tab:hover { background-color: #333333; }
QScrollBar:vertical { width: 10px; background: #2d2d2d; border-radius: 5px; }
QScrollBar::handle:vertical { background: #555555; border-radius: 5px; min-height: 24px; }
QScrollBar::handle:vertical:hover { background: #777777; }
QScrollBar:horizontal { height: 10px; background: #2d2d2d; border-radius: 5px; }
QScrollBar::handle:horizontal { background: #555555; border-radius: 5px; min-width: 24px; }
QScrollBar::handle:horizontal:hover { background: #777777; }
QScrollBar::add-line, QScrollBar::sub-line { height: 0; }
"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._config = ConfigManager()
        self._batch_processor = BatchProcessor()
        self._is_converting = False
        self._history_service = HistoryService()
        self._language_service = LanguageService()
        self._preset_service = PresetService()
        self._watch_folder = WatchFolderService()
        self._update_service = UpdateService()
        self._recent_files: list[str] = []
        self._recent_folders: list[str] = []

        self.setWindowTitle("HEIC Image Converter Pro")
        self.setMinimumSize(1200, 750)
        self.resize(1400, 850)

        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()
        self._load_window_geometry()
        self._apply_theme()
        self._update_theme_action()

        logger.info("MainWindow initialized")

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(3)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)

        self._drop_area = DropArea()
        self._file_list = FileListWidget()
        self._progress_panel = ProgressPanel()

        left_layout.addWidget(self._drop_area)
        left_layout.addWidget(self._file_list)
        left_layout.addWidget(self._progress_panel)
        self._splitter.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)

        self._settings_panel = SettingsPanel()
        self._conversion_log = ConversionLog()

        right_layout.addWidget(self._settings_panel)
        right_layout.addWidget(self._conversion_log)
        self._splitter.addWidget(right_panel)

        self._splitter.setSizes(self._config.get().splitter_sizes)
        main_layout.addWidget(self._splitter)

    def _setup_menu(self) -> None:
        menubar = self.menuBar()

        # --- File Menu ---
        file_menu = menubar.addMenu(self._tr("menu.file"))
        add_files_action = QAction(self._tr("menu.open_file"), self)
        add_files_action.setShortcut(QKeySequence("Ctrl+O"))
        add_files_action.triggered.connect(self._on_add_files)
        file_menu.addAction(add_files_action)

        add_folder_action = QAction(self._tr("menu.open_folder"), self)
        add_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        add_folder_action.triggered.connect(self._on_add_folder)
        file_menu.addAction(add_folder_action)

        file_menu.addSeparator()

        self._recent_files_menu = file_menu.addMenu(self._tr("menu.recent_files"))
        self._update_recent_files_menu()

        self._recent_folders_menu = file_menu.addMenu(self._tr("menu.recent_folders"))
        self._update_recent_folders_menu()

        file_menu.addSeparator()

        watch_action = QAction("Watch Folder...", self)
        watch_action.triggered.connect(self._toggle_watch_folder)
        file_menu.addAction(watch_action)

        file_menu.addSeparator()

        clear_action = QAction(self._tr("menu.clear_queue"), self)
        clear_action.triggered.connect(self._on_clear)
        file_menu.addAction(clear_action)

        file_menu.addSeparator()

        export_log_action = QAction("Export Log as CSV...", self)
        export_log_action.triggered.connect(self._export_history_csv)
        file_menu.addAction(export_log_action)

        file_menu.addSeparator()

        exit_action = QAction(self._tr("menu.exit"), self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # --- Convert Menu ---
        convert_menu = menubar.addMenu("&Convert")

        self._start_action = QAction("&Start Conversion", self)
        self._start_action.setShortcut(QKeySequence("Ctrl+R"))
        self._start_action.triggered.connect(self._start_conversion)
        convert_menu.addAction(self._start_action)

        self._stop_action = QAction("&Stop Conversion", self)
        self._stop_action.setShortcut(QKeySequence("Ctrl+Shift+R"))
        self._stop_action.setEnabled(False)
        self._stop_action.triggered.connect(self._stop_conversion)
        convert_menu.addAction(self._stop_action)

        convert_menu.addSeparator()

        retry_action = QAction("&Retry Failed", self)
        retry_action.triggered.connect(self._retry_failed)
        convert_menu.addAction(retry_action)

        # --- Edit Menu ---
        edit_menu = menubar.addMenu(self._tr("menu.edit"))
        select_all_action = QAction(self._tr("menu.select_all"), self)
        select_all_action.setShortcut(QKeySequence("Ctrl+A"))
        select_all_action.triggered.connect(self._select_all)
        edit_menu.addAction(select_all_action)

        remove_action = QAction(self._tr("menu.remove_selected"), self)
        remove_action.setShortcut(QKeySequence("Delete"))
        remove_action.triggered.connect(self._remove_selected)
        edit_menu.addAction(remove_action)

        # --- View Menu ---
        view_menu = menubar.addMenu(self._tr("menu.view"))

        self._theme_action = QAction(self._tr("menu.dark_mode"), self)
        self._theme_action.setShortcut(QKeySequence("Ctrl+T"))
        self._theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(self._theme_action)

        view_menu.addSeparator()

        lang_menu = view_menu.addMenu(self._tr("menu.language"))
        self._setup_language_menu(lang_menu)

        view_menu.addSeparator()

        # --- Tools Menu ---
        tools_menu = menubar.addMenu(self._tr("menu.tools"))

        batch_rename_action = QAction(self._tr("menu.batch_rename"), self)
        batch_rename_action.triggered.connect(self._show_batch_rename)
        tools_menu.addAction(batch_rename_action)

        tools_menu.addSeparator()

        preset_menu = tools_menu.addMenu("Presets")
        self._setup_preset_menu(preset_menu)

        tools_menu.addSeparator()

        settings_action = QAction(self._tr("menu.settings"), self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._show_settings)
        tools_menu.addAction(settings_action)

        # --- Help Menu ---
        help_menu = menubar.addMenu(self._tr("menu.help"))

        update_action = QAction(self._tr("menu.check_update"), self)
        update_action.triggered.connect(self._check_update)
        help_menu.addAction(update_action)

        help_menu.addSeparator()

        about_action = QAction(self._tr("menu.about"), self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        add_files_btn = QToolButton()
        add_files_btn.setText("+ Files")
        add_files_btn.setToolTip("Add HEIC files (Ctrl+O)")
        add_files_btn.clicked.connect(self._on_add_files)
        toolbar.addWidget(add_files_btn)

        add_folder_btn = QToolButton()
        add_folder_btn.setText("+ Folder")
        add_folder_btn.setToolTip("Add folder (Ctrl+D)")
        add_folder_btn.clicked.connect(self._on_add_folder)
        toolbar.addWidget(add_folder_btn)

        toolbar.addSeparator()

        self._convert_btn = QToolButton()
        self._convert_btn.setText("▶ Convert")
        self._convert_btn.setToolTip("Start conversion (Ctrl+R)")
        self._convert_btn.clicked.connect(self._start_conversion)
        toolbar.addWidget(self._convert_btn)

        self._stop_btn = QToolButton()
        self._stop_btn.setText("■ Stop")
        self._stop_btn.setToolTip("Stop conversion (Ctrl+Shift+R)")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_conversion)
        toolbar.addWidget(self._stop_btn)

        toolbar.addSeparator()

        clear_btn = QToolButton()
        clear_btn.setText("Clear")
        clear_btn.clicked.connect(self._on_clear)
        toolbar.addWidget(clear_btn)

        toolbar.addSeparator()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        theme_btn = QToolButton()
        theme_btn.setText("🌙")
        theme_btn.setToolTip("Toggle theme")
        theme_btn.clicked.connect(self._toggle_theme)
        toolbar.addWidget(theme_btn)

    def _setup_statusbar(self) -> None:
        self._status_label = QLabel("Ready")
        self.statusBar().addWidget(self._status_label, 1)

        ffmpeg_avail = MediaDetector.is_available()
        ffmpeg_status = "FFmpeg: ✓" if ffmpeg_avail else "FFmpeg: ✗"
        self._ffmpeg_label = QLabel(ffmpeg_status)
        self._ffmpeg_label.setStyleSheet(
            "color: green; font-weight: bold; padding: 0 8px;"
            if ffmpeg_avail else
            "color: red; padding: 0 8px;"
        )
        self.statusBar().addPermanentWidget(self._ffmpeg_label)

        self._file_count_label = QLabel("0 files")
        self.statusBar().addPermanentWidget(self._file_count_label)

    def _connect_signals(self) -> None:
        self._drop_area.files_dropped.connect(self._on_files_dropped)
        self._file_list.files_changed.connect(self._on_files_changed)
        self._batch_processor.progress_changed.connect(self._on_batch_progress)
        self._batch_processor.task_completed.connect(self._on_task_completed)
        self._batch_processor.all_completed.connect(self._on_batch_completed)

        self._progress_panel.cancelled.connect(self._stop_conversion)
        self._progress_panel.retry_requested.connect(self._retry_failed)

        self._settings_panel.settings_changed.connect(self._on_settings_changed)

        self._watch_folder.files_detected.connect(self._on_watch_files_detected)

    def _on_files_dropped(self, paths: list[Path]) -> None:
        self._file_list.add_paths(paths)
        for p in paths:
            if p.is_file():
                self._add_to_recent("files", str(p))
            elif p.is_dir():
                self._add_to_recent("folders", str(p))

    def _on_watch_files_detected(self, paths: list[Path]) -> None:
        self._file_list.add_paths(paths)
        self._conversion_log.log_info(f"Watch folder detected {len(paths)} new file(s)")

    def _on_files_changed(self, tasks) -> None:
        count = len(tasks)
        pending = sum(1 for t in tasks if t.status == TaskStatus.PENDING)
        self._drop_area.set_file_count(count)
        self._file_count_label.setText(f"{count} files ({pending} pending)")

    def _add_to_recent(self, which: str, path: str) -> None:
        if which == "files":
            files = self._config.get().recent_files
            if path in files:
                files.remove(path)
            files.insert(0, path)
            self._config.get().recent_files = files[:10]
        else:
            folders = self._config.get().recent_folders
            if path in folders:
                folders.remove(path)
            folders.insert(0, path)
            self._config.get().recent_folders = folders[:10]
        self._config.save()
        self._update_recent_files_menu()
        self._update_recent_folders_menu()

    def _start_conversion(self) -> None:
        pending = self._file_list.get_pending_tasks()
        if not pending:
            QMessageBox.information(
                self, "No Tasks", "No pending files to convert. Add HEIC files first."
            )
            return

        if self._config.get().output_mode.value == "ask_every":
            folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
            if not folder:
                return
            output_dir = Path(folder)
            for task in pending:
                task.output_path = FileService.generate_output_path(
                    task.source_path,
                    self._config.get().export_format.value,
                    self._config.get().filename_template,
                    output_dir,
                )
            self._config.get().custom_output_folder = str(output_dir)

        self._settings_panel.apply_settings()
        self._is_converting = True
        self._set_conversion_ui_state(True)

        self._conversion_log.log_info(
            f"Starting conversion of {len(pending)} file(s)..."
        )
        self._progress_panel.start_batch(len(pending))
        self._status_label.setText("Converting...")

        self._batch_processor = BatchProcessor(max_threads=self._config.get().max_threads)
        self._batch_processor.progress_changed.connect(self._on_batch_progress)
        self._batch_processor.task_completed.connect(self._on_task_completed)
        self._batch_processor.all_completed.connect(self._on_batch_completed)
        self._batch_processor.start(pending, self._config.get())

    def _stop_conversion(self) -> None:
        self._batch_processor.stop()
        self._is_converting = False
        self._set_conversion_ui_state(False)
        self._conversion_log.log_info("Conversion stopped by user")
        self._status_label.setText("Conversion stopped")

    def _retry_failed(self) -> None:
        failed = [
            t for t in self._file_list.get_all_tasks()
            if t.status == TaskStatus.FAILED
        ]
        if failed:
            for task in failed:
                task.status = TaskStatus.PENDING
                task.error_message = ""
            self._on_files_changed(self._file_list.get_all_tasks())
            self._conversion_log.log_info(
                f"Retrying {len(failed)} failed file(s)..."
            )
            self._start_conversion()
        else:
            self._conversion_log.log_info("No failed tasks to retry")

    def _on_batch_progress(self, task_id: str, progress: float) -> None:
        for task in self._file_list.get_all_tasks():
            if task.task_id == task_id:
                task.progress = progress
                break

    def _on_task_completed(self, task: ConversionTask) -> None:
        self._file_list.update_task_status(task)
        self._conversion_log.log_task(task)
        self._progress_panel.on_task_completed(task)

        if task.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            entry = HistoryEntry(
                source_path=str(task.source_path),
                output_path=str(task.output_path) if task.output_path else "",
                source_format=task.source_path.suffix,
                output_format=self._config.get().export_format.value,
                status="success" if task.status == TaskStatus.COMPLETED else "failed",
                duration=task.elapsed_time,
                source_size=task.original_size,
                output_size=task.output_size,
            )
            self._history_service.add_entry(entry)

    def _on_batch_completed(self) -> None:
        self._is_converting = False
        self._set_conversion_ui_state(False)
        self._progress_panel.finish_batch()
        self._status_label.setText("Conversion completed")

        completed = sum(
            1 for t in self._file_list.get_all_tasks()
            if t.status == TaskStatus.COMPLETED
        )
        failed = sum(
            1 for t in self._file_list.get_all_tasks()
            if t.status == TaskStatus.FAILED
        )
        self._conversion_log.log_info(
            f"Batch completed: {completed} succeeded, {failed} failed"
        )

        if not self._config.get().keep_original:
            removed = 0
            for task in self._file_list.get_all_tasks():
                if task.status == TaskStatus.COMPLETED and task.source_path.exists():
                    try:
                        task.source_path.unlink()
                        removed += 1
                    except OSError as exc:
                        self._conversion_log.log_error(
                            f"Failed to remove original {task.filename}: {exc}"
                        )
            if removed:
                self._conversion_log.log_info(
                    f"Removed {removed} original file(s)"
                )

        if failed > 0:
            QMessageBox.warning(
                self,
                "Conversion Complete",
                f"Completed with {failed} failure(s).\nCheck the log for details.",
            )

    def _set_conversion_ui_state(self, converting: bool) -> None:
        self._start_action.setEnabled(not converting)
        self._stop_action.setEnabled(converting)
        self._convert_btn.setEnabled(not converting)
        self._stop_btn.setEnabled(converting)

    def _on_settings_changed(self) -> None:
        self._settings_panel.apply_settings()

    def _on_add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select HEIC/HEIF Files",
            "",
            "HEIC/HEIF Files (*.heic *.heif *.heics *.heifs);;All Files (*.*)",
        )
        if files:
            paths = [Path(f) for f in files]
            self._file_list.add_paths(paths)
            for p in paths:
                self._add_to_recent("files", str(p))

    def _on_add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with HEIC Files")
        if folder:
            self._file_list.add_paths([Path(folder)])
            self._add_to_recent("folders", folder)

    def _on_clear(self) -> None:
        if self._is_converting:
            QMessageBox.warning(self, "Busy", "Cannot clear while conversion is running.")
            return
        self._file_list._clear_all()
        self._drop_area.set_file_count(0)
        self._file_count_label.setText("0 files")

    def _toggle_theme(self) -> None:
        current = self._config.get().theme
        if current == ThemeMode.DARK:
            self._config.get().theme = ThemeMode.LIGHT
        else:
            self._config.get().theme = ThemeMode.DARK
        self._config.save()
        self._apply_theme()
        self._update_theme_action()

    def _update_theme_action(self) -> None:
        is_dark = self._config.get().theme == ThemeMode.DARK
        self._theme_action.setText("Toggle &Light Theme" if is_dark else "Toggle &Dark Theme")

    def _tr(self, key: str) -> str:
        return self._language_service.get(key)

    def _setup_language_menu(self, menu: QMenu) -> None:
        languages = [
            ("English", "en"),
            ("Khmer", "km"),
            ("中文", "zh"),
            ("日本語", "ja"),
        ]
        for label, code in languages:
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(self._config.get().language == code)
            action.triggered.connect(lambda checked, c=code: self._set_language(c))
            menu.addAction(action)

    def _set_language(self, code: str) -> None:
        self._language_service.set_language(code)
        self._config.get().language = code
        self._config.save()
        QMessageBox.information(
            self, "Language", "Language changed. Restart to apply fully."
        )

    def _setup_preset_menu(self, menu: QMenu) -> None:
        presets = self._preset_service.presets
        menu.clear()
        for preset in presets:
            action = QAction(preset.name, self)
            action.triggered.connect(lambda checked, p=preset: self._apply_preset(p))
            menu.addAction(action)
        if presets:
            menu.addSeparator()
        save_action = QAction("Save Current as Preset...", self)
        save_action.triggered.connect(self._save_preset)
        menu.addAction(save_action)
        manage_action = QAction("Manage Presets...", self)
        manage_action.triggered.connect(self._manage_presets)
        menu.addAction(manage_action)

    def _apply_preset(self, preset) -> None:
        preset.apply_to(self._config.get())
        self._config.save()
        self._settings_panel._load_settings()
        self._conversion_log.log_info(f"Applied preset: {preset.name}")

    def _save_preset(self) -> None:
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if ok and name:
            from heic_converter_pro.app.services.preset_service import Preset
            preset = Preset.from_settings(name, self._config.get())
            self._preset_service.add(preset)
            self._conversion_log.log_info(f"Saved preset: {name}")

    def _manage_presets(self) -> None:
        from PySide6.QtWidgets import QInputDialog, QListWidget, QDialog, QVBoxLayout, QPushButton
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Presets")
        dialog.setMinimumWidth(300)
        layout = QVBoxLayout(dialog)
        list_widget = QListWidget()
        for p in self._preset_service.presets:
            list_widget.addItem(p.name)
        layout.addWidget(list_widget)
        remove_btn = QPushButton("Remove Selected")
        def remove():
            item = list_widget.currentItem()
            if item:
                self._preset_service.remove(item.text())
                list_widget.takeItem(list_widget.row(item))
        remove_btn.clicked.connect(remove)
        layout.addWidget(remove_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec()

    def _update_recent_files_menu(self) -> None:
        self._recent_files_menu.clear()
        files = self._config.get().recent_files[:10]
        for path in files:
            action = QAction(path, self)
            action.triggered.connect(lambda checked, p=path: self._file_list.add_paths([Path(p)]))
            self._recent_files_menu.addAction(action)
        if files:
            self._recent_files_menu.addSeparator()
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(lambda: self._clear_recent("files"))
            self._recent_files_menu.addAction(clear_action)

    def _update_recent_folders_menu(self) -> None:
        self._recent_folders_menu.clear()
        folders = self._config.get().recent_folders[:10]
        for path in folders:
            action = QAction(path, self)
            action.triggered.connect(lambda checked, p=path: self._file_list.add_paths([Path(p)]))
            self._recent_folders_menu.addAction(action)
        if folders:
            self._recent_folders_menu.addSeparator()
            clear_action = QAction("Clear Recent Folders", self)
            clear_action.triggered.connect(lambda: self._clear_recent("folders"))
            self._recent_folders_menu.addAction(clear_action)

    def _clear_recent(self, which: str) -> None:
        if which == "files":
            self._config.get().recent_files = []
        else:
            self._config.get().recent_folders = []
        self._config.save()
        self._update_recent_files_menu()
        self._update_recent_folders_menu()

    def _toggle_watch_folder(self) -> None:
        if self._watch_folder.is_watching:
            self._watch_folder.stop_watching()
            self._conversion_log.log_info("Stopped watching folder")
            return
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Watch")
        if folder:
            self._watch_folder.start_watching(Path(folder))
            self._conversion_log.log_info(f"Watching folder: {folder}")

    def _export_history_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export History", "conversion_history.csv",
            "CSV Files (*.csv);;All Files (*.*)",
        )
        if path:
            self._history_service.export_csv(Path(path))
            self._conversion_log.log_info(f"History exported to {path}")

    def _select_all(self) -> None:
        self._file_list._list.selectAll()

    def _remove_selected(self) -> None:
        self._file_list._remove_selected()

    def _show_batch_rename(self) -> None:
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox, QCheckBox, QDialogButtonBox, QLabel
        dialog = QDialog(self)
        dialog.setWindowTitle("Batch Rename Rules")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()

        prefix_edit = QLineEdit(self._config.get().rename_prefix)
        form.addRow("Prefix:", prefix_edit)
        suffix_edit = QLineEdit(self._config.get().rename_suffix)
        form.addRow("Suffix:", suffix_edit)
        counter_start = QSpinBox()
        counter_start.setRange(1, 99999)
        counter_start.setValue(self._config.get().rename_counter_start)
        form.addRow("Counter start:", counter_start)
        counter_digits = QSpinBox()
        counter_digits.setRange(1, 10)
        counter_digits.setValue(self._config.get().rename_counter_digits)
        form.addRow("Counter digits:", counter_digits)
        use_date = QCheckBox()
        use_date.setChecked(self._config.get().rename_use_date)
        form.addRow("Include date:", use_date)
        date_fmt = QLineEdit(self._config.get().rename_date_format)
        form.addRow("Date format:", date_fmt)
        find_text = QLineEdit(self._config.get().rename_find)
        form.addRow("Find:", find_text)
        replace_text = QLineEdit(self._config.get().rename_replace)
        form.addRow("Replace:", replace_text)

        layout.addLayout(form)
        layout.addWidget(QLabel("Preview: {prefix}{date}{name}_{counter}{suffix}.ext"))

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec():
            s = self._config.get()
            s.rename_prefix = prefix_edit.text()
            s.rename_suffix = suffix_edit.text()
            s.rename_counter_start = counter_start.value()
            s.rename_counter_digits = counter_digits.value()
            s.rename_use_date = use_date.isChecked()
            s.rename_date_format = date_fmt.text()
            s.rename_find = find_text.text()
            s.rename_replace = replace_text.text()
            s.rename_enabled = True
            self._config.save()
            self._conversion_log.log_info("Batch rename rules saved")

    def _check_update(self) -> None:
        self._conversion_log.log_info("Checking for updates...")
        update = self._update_service.check_for_update()
        if update:
            reply = QMessageBox.question(
                self, "Update Available",
                f"Version {update['version']} is available.\n{update.get('release_notes', '')}\n\nDownload now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes and update.get("download_url"):
                import webbrowser
                webbrowser.open(update["download_url"])
        else:
            QMessageBox.information(self, "Up to Date", "You have the latest version.")

    def _detect_system_theme(self) -> ThemeMode:
        try:
            import winreg
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            ) as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return ThemeMode.LIGHT if value else ThemeMode.DARK
        except Exception:
            return ThemeMode.LIGHT

    def _apply_theme(self) -> None:
        theme = self._config.get().theme
        if theme == ThemeMode.SYSTEM:
            theme = self._detect_system_theme()
        if theme == ThemeMode.DARK:
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet(LIGHT_THEME)
        logger.info("Applied %s theme", theme.value)

        from PySide6.QtGui import QPalette
        if theme == ThemeMode.DARK:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(37, 37, 38))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(212, 212, 212))
            palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(42, 42, 42))
            palette.setColor(QPalette.ColorRole.Text, QColor(212, 212, 212))
            palette.setColor(QPalette.ColorRole.Button, QColor(51, 51, 51))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(212, 212, 212))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 212))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            self.setPalette(palette)
        else:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(243, 243, 243))
            palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 30, 30))
            palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(245, 245, 245))
            palette.setColor(QPalette.ColorRole.Text, QColor(30, 30, 30))
            palette.setColor(QPalette.ColorRole.Button, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor(30, 30, 30))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 212))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
            self.setPalette(palette)

    def _show_settings(self) -> None:
        dialog = SettingsDialog(self)
        if dialog.exec():
            if dialog.theme_changed:
                self._apply_theme()
                self._update_theme_action()
            self._settings_panel._load_settings()

    def _show_about(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()

    def _load_window_geometry(self) -> None:
        geometry = self._config.get().window_geometry
        if geometry:
            try:
                self.restoreGeometry(QByteArray.fromHex(
                    bytes(geometry.get("geometry", ""), "utf-8")
                ))
                self.restoreState(QByteArray.fromHex(
                    bytes(geometry.get("state", ""), "utf-8")
                ))
            except Exception:
                pass

    def closeEvent(self, event) -> None:
        self._batch_processor.stop()
        self._config.get().splitter_sizes = self._splitter.sizes()
        self._config.get().window_geometry = {
            "geometry": bytes(self.saveGeometry().toHex()).decode("utf-8"),
            "state": bytes(self.saveState().toHex()).decode("utf-8"),
        }
        self._config.save()
        logger.info("MainWindow closed, settings saved")
        super().closeEvent(event)
