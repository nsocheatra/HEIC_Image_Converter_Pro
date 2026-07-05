from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Callable, List, Optional

from PySide6.QtCore import QObject, QRunnable, Signal, QThreadPool

from heic_converter_pro.app.core.converter import HeicConverter
from heic_converter_pro.app.models.conversion_task import ConversionTask, TaskStatus
from heic_converter_pro.app.models.settings import AppSettings

logger = logging.getLogger(__name__)


class ConversionWorker(QRunnable):
    class Signals(QObject):
        progress_changed = Signal(str, float)
        task_completed = Signal(object)
        all_completed = Signal()

    def __init__(
        self,
        tasks: List[ConversionTask],
        settings: AppSettings,
    ) -> None:
        super().__init__()
        self._tasks = tasks
        self._settings = settings
        self.signals = ConversionWorker.Signals()
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        converter = HeicConverter(self._settings)
        total = len(self._tasks)
        for index, task in enumerate(self._tasks):
            if self._cancelled:
                task.status = TaskStatus.CANCELLED
                self.signals.task_completed.emit(task)
                continue

            def make_progress(task_id: str):
                def callback(value: float):
                    overall = (index + value) / total
                    self.signals.progress_changed.emit(task_id, overall)
                return callback

            task = converter.convert(task, progress_callback=make_progress(task.task_id))
            self.signals.task_completed.emit(task)
        self.signals.all_completed.emit()


class BatchProcessor(QObject):
    progress_changed = Signal(str, float)
    task_completed = Signal(object)
    all_completed = Signal()

    def __init__(self, max_threads: int = 4) -> None:
        super().__init__()
        self._pool = QThreadPool()
        self._pool.setMaxThreadCount(max_threads)
        self._worker: Optional[ConversionWorker] = None

    def start(
        self,
        tasks: List[ConversionTask],
        settings: AppSettings,
    ) -> None:
        self.stop()
        if not tasks:
            self.all_completed.emit()
            return
        self._worker = ConversionWorker(tasks, settings)
        self._worker.signals.progress_changed.connect(self.progress_changed.emit)
        self._worker.signals.task_completed.connect(self.task_completed.emit)
        self._worker.signals.all_completed.connect(self.all_completed.emit)
        self._pool.start(self._worker)

    def stop(self) -> None:
        if self._worker is not None:
            self._worker.cancel()
            self._worker = None

    def is_running(self) -> bool:
        return self._pool.activeThreadCount() > 0

    @property
    def active_thread_count(self) -> int:
        return self._pool.activeThreadCount()
