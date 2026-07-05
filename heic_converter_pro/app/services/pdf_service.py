from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from PIL import Image

from heic_converter_pro.app.services.export_service import ExportService

logger = logging.getLogger(__name__)


class PdfService:
    @staticmethod
    def create_pdf(
        images: List[Image.Image],
        output_path: Path,
        quality: int = 95,
        title: Optional[str] = None,
    ) -> Path:
        if not images:
            raise ValueError("No images provided for PDF generation")
        return ExportService.save_pdf_multipage(images, output_path, quality)

    @staticmethod
    def create_single_image_pdf(
        image: Image.Image,
        output_path: Path,
        quality: int = 95,
    ) -> Path:
        return ExportService.save_pdf_multipage([image], output_path, quality)
