from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PIL import Image

from heic_converter_pro.app.models.settings import ExportFormat

logger = logging.getLogger(__name__)


class ExportService:
    _FORMAT_MAP = {
        ExportFormat.JPG: "JPEG",
        ExportFormat.PNG: "PNG",
        ExportFormat.WEBP: "WEBP",
        ExportFormat.TIFF: "TIFF",
        ExportFormat.BMP: "BMP",
        ExportFormat.PDF: "PDF",
    }

    @staticmethod
    def save(
        image: Image.Image,
        output_path: Path,
        export_format: ExportFormat,
        quality: int = 95,
        **kwargs,
    ) -> Path:
        pil_format = ExportService._FORMAT_MAP[export_format]
        output_path = output_path.with_suffix(f".{export_format.value}")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        save_kwargs = {}
        if pil_format in ("JPEG", "WEBP"):
            save_kwargs["quality"] = quality
            save_kwargs["optimize"] = True
        if pil_format == "TIFF":
            save_kwargs["compression"] = "tiff_lzw"
        if pil_format == "PNG":
            save_kwargs["optimize"] = True
        if pil_format == "PDF":
            save_kwargs["save_all"] = True

        if "exif" in image.info:
            save_kwargs["exif"] = image.info["exif"]
        if "icc_profile" in image.info:
            save_kwargs["icc_profile"] = image.info["icc_profile"]

        if image.mode == "RGBA" and pil_format == "JPEG":
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background

        if image.mode not in ("RGB", "RGBA", "L", "CMYK") and pil_format in ("JPEG", "WEBP"):
            image = image.convert("RGB")

        image.save(str(output_path), pil_format, **save_kwargs)
        logger.info("Saved %s as %s", output_path.name, pil_format)
        return output_path

    @staticmethod
    def save_pdf_multipage(
        images: list[Image.Image],
        output_path: Path,
        quality: int = 95,
    ) -> Path:
        output_path = output_path.with_suffix(".pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        rgb_images = []
        for img in images:
            if img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                rgb_images.append(bg)
            elif img.mode != "RGB":
                rgb_images.append(img.convert("RGB"))
            else:
                rgb_images.append(img)

        first = rgb_images[0]
        rest = rgb_images[1:] if len(rgb_images) > 1 else None
        first.save(
            str(output_path),
            "PDF",
            save_all=rest is not None,
            append_images=rest,
            quality=quality,
        )
        logger.info("Saved multipage PDF: %s", output_path.name)
        return output_path
