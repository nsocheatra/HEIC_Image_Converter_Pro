from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

TRANSLATIONS_DIR = Path(__file__).parent / "translations"


class LanguageService:
    _instance: Optional[LanguageService] = None

    def __new__(cls) -> LanguageService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_loaded"):
            return
        self._loaded = True
        self._current_lang = "en"
        self._translations: dict[str, str] = {}
        self._load_translations("en")

    @property
    def current_language(self) -> str:
        return self._current_lang

    def set_language(self, lang: str) -> None:
        if self._load_translations(lang):
            self._current_lang = lang

    def get(self, key: str, default: Optional[str] = None) -> str:
        return self._translations.get(key, default or key)

    def _load_translations(self, lang: str) -> bool:
        file_path = TRANSLATIONS_DIR / f"{lang}.json"
        if not file_path.exists():
            file_path = TRANSLATIONS_DIR / "en.json"
            if not file_path.exists() and lang != "en":
                self._translations = {}
                return False

        try:
            with open(str(file_path), "r", encoding="utf-8") as f:
                self._translations = json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            logger.warning("Failed to load translations for %s: %s", lang, exc)
            self._translations = {}
            return False
