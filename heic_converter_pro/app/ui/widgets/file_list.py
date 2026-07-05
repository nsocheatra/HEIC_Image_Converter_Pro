from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QMenu,
    QAbstractItemView,
    QFileDialog,
    QMessageBox,
)

from heic_converter_pro.app.models.conversion_task import ConversionTask, TaskStatus
from heic_converter_pro.app.services.file_service import FileService
from heic_converter_pro.app.services.language_service import LanguageService

logger = logging.getLogger(__name__)


class FileListWidget(QWidget):
    files_changed = Signal(list)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._tasks: List[ConversionTask] = []
        self._ls = LanguageService()
        self._setup_ui()

    def retranslate(self) -> None:
        t = self._ls.get
        self._title.setText(t("file_list.title"))
        self._add_btn.setText(t("file_list.add_files"))
        self._add_folder_btn.setText(t("file_list.add_folder"))
        self._clear_btn.setText(t("file_list.clear"))
        self._remove_btn.setText(t("file_list.remove"))
        self._update_count()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        self._title = QLabel("Input Files")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        self._title.setFont(title_font)
        header_layout.addWidget(self._title)
        header_layout.addStretch()

        self._count_label = QLabel("0 files")
        header_layout.addWidget(self._count_label)
        layout.addLayout(header_layout)

        self._list = QListWidget()
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.setAlternatingRowColors(True)
        self._list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._list)

        btn_layout = QHBoxLayout()
        self._add_btn = QPushButton("Add Files")
        self._add_btn.clicked.connect(self._add_files)
        self._add_folder_btn = QPushButton("Add Folder")
        self._add_folder_btn.clicked.connect(self._add_folder)
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.clicked.connect(self._clear_all)
        self._remove_btn = QPushButton("Remove Selected")
        self._remove_btn.clicked.connect(self._remove_selected)

        btn_layout.addWidget(self._add_btn)
        btn_layout.addWidget(self._add_folder_btn)
        btn_layout.addWidget(self._remove_btn)
        btn_layout.addWidget(self._clear_btn)
        layout.addLayout(btn_layout)

    @property
    def tasks(self) -> List[ConversionTask]:
        return self._tasks

    def add_paths(self, paths: List[Path]) -> None:
        heic_files = FileService.find_heic_files(paths)
        existing = {str(t.source_path) for t in self._tasks}
        new_count = 0
        for file_path in heic_files:
            if str(file_path) not in existing:
                task = ConversionTask(source_path=file_path)
                self._tasks.append(task)
                self._add_list_item(task)
                new_count += 1
        if new_count > 0:
            self._update_count()
            self.files_changed.emit(self._tasks)
            logger.info("Added %d new files", new_count)

    def _add_list_item(self, task: ConversionTask) -> None:
        item = QListWidgetItem(task.filename)
        item.setData(Qt.ItemDataRole.UserRole, task.task_id)
        item.setToolTip(str(task.source_path))
        self._list.addItem(item)

    def _update_count(self) -> None:
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self._tasks if t.status == TaskStatus.FAILED)
        parts = [str(total)]
        if completed:
            parts.append(f"✓ {completed}")
        if failed:
            parts.append(f"✗ {failed}")
        self._count_label.setText(" | ".join(parts))

    def update_task_status(self, task: ConversionTask) -> None:
        for i in range(self._list.count()):
            item = self._list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == task.task_id:
                status_symbols = {
                    TaskStatus.COMPLETED: "✓ ",
                    TaskStatus.FAILED: "✗ ",
                    TaskStatus.PROCESSING: "⟳ ",
                    TaskStatus.CANCELLED: "— ",
                    TaskStatus.SKIPPED: "→ ",
                }
                prefix = status_symbols.get(task.status, "")
                item.setText(f"{prefix}{task.filename}")
                if task.status == TaskStatus.COMPLETED:
                    item.setForeground(Qt.GlobalColor.darkGreen)
                elif task.status == TaskStatus.FAILED:
                    item.setForeground(Qt.GlobalColor.red)
                break
        self._update_count()

    def _add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select HEIC/HEIF Files",
            "",
            "HEIC/HEIF Files (*.heic *.heif *.heics *.heifs);;All Files (*.*)",
        )
        if files:
            self.add_paths([Path(f) for f in files])

    def _add_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with HEIC Files")
        if folder:
            self.add_paths([Path(folder)])

    def _remove_selected(self) -> None:
        selected = self._list.selectedItems()
        for item in selected:
            task_id = item.data(Qt.ItemDataRole.UserRole)
            self._tasks = [t for t in self._tasks if t.task_id != task_id]
            self._list.takeItem(self._list.row(item))
        self._update_count()
        self.files_changed.emit(self._tasks)

    def _clear_all(self) -> None:
        self._tasks.clear()
        self._list.clear()
        self._update_count()
        self.files_changed.emit(self._tasks)

    def _show_context_menu(self, position) -> None:
        menu = QMenu()
        item = self._list.itemAt(position)
        if item:
            remove_action = menu.addAction("Remove")
            action = menu.exec(self._list.mapToGlobal(position))
            if action == remove_action:
                self._remove_selected()

    def get_pending_tasks(self) -> List[ConversionTask]:
        return [t for t in self._tasks if t.status in (TaskStatus.PENDING, TaskStatus.FAILED)]

    def get_all_tasks(self) -> List[ConversionTask]:
        return self._tasks
