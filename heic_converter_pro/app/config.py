from __future__ import annotations

import logging
from pathlib import Path

from heic_converter_pro.app.models.settings import AppSettings

logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".heic_converter_pro"
CONFIG_FILE = CONFIG_DIR / "settings.json"


class ConfigManager:
    _instance: ConfigManager | None = None

    def __new__(cls) -> ConfigManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.settings: AppSettings = AppSettings.load(CONFIG_FILE)
        logger.info("Configuration loaded from %s", CONFIG_FILE)

    def save(self) -> None:
        self.settings.save(CONFIG_FILE)
        logger.info("Configuration saved to %s", CONFIG_FILE)

    def get(self) -> AppSettings:
        return self.settings

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        self.save()
