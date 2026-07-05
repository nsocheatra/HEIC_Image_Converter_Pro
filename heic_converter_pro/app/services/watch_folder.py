from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Callable, Optional, Set

from PySide6.QtCore import QObject, QThread, Signal

from heic_converter_pro.app.services.file_service import FileService

logger = logging.getLogger(__name__)


class WatchFolderWorker(QThread):
    files_detected = Signal(list)
    error_occurred = Signal(str)

    def __init__(
        self,
        folder: Path,
        interval: float = 2.0,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._folder = folder
        self._interval = interval
        self._running = False
        self._known_files: Set[str] = set()

    def run(self) -> None:
        self._running = True
        self._scan_existing()
        while self._running:
            time.sleep(self._interval)
            try:
                new_files = self._scan_new()
                if new_files:
                    self.files_detected.emit(new_files)
            except Exception as exc:
                self.error_occurred.emit(str(exc))

    def stop(self) -> None:
        self._running = False

    def _scan_existing(self) -> None:
        try:
            for f in self._folder.rglob("*"):
                if f.is_file() and FileService.is_heic_file(f):
                    self._known_files.add(str(f.resolve()))
        except Exception as exc:
            logger.warning("WatchFolder initial scan error: %s", exc)

    def _scan_new(self) -> list[Path]:
        new: list[Path] = []
        try:
            for f in self._folder.rglob("*"):
                if f.is_file() and FileService.is_heic_file(f):
                    resolved = str(f.resolve())
                    if resolved not in self._known_files:
                        self._known_files.add(resolved)
                        new.append(f)
        except Exception as exc:
            logger.warning("WatchFolder scan error: %s", exc)
        return new


class WatchFolderService(QObject):
    files_detected = Signal(list)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._worker: Optional[WatchFolderWorker] = None
        self._folder: Optional[Path] = None

    @property
    def is_watching(self) -> bool:
        return self._worker is not None and self._worker.isRunning()

    @property
    def folder(self) -> Optional[Path]:
        return self._folder

    def start_watching(self, folder: Path, interval: float = 2.0) -> None:
        self.stop_watching()
        self._folder = folder
        self._worker = WatchFolderWorker(folder, interval, self)
        self._worker.files_detected.connect(self.files_detected.emit)
        self._worker.start()
        logger.info("Watching folder: %s", folder)

    def stop_watching(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self._worker.wait(3000)
            self._worker = None
            self._folder = None
            logger.info("Stopped watching folder")
