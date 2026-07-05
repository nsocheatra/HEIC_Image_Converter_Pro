from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Callable, Optional

from PIL import Image

from heic_converter_pro.app.core.image_processor import ImageProcessor
from heic_converter_pro.app.core.metadata import MetadataHandler
from heic_converter_pro.app.media.ffmpeg_converter import FfmpegConverter
from heic_converter_pro.app.models.conversion_task import ConversionTask, TaskStatus
from heic_converter_pro.app.models.settings import AppSettings, ExportFormat
from heic_converter_pro.app.services.export_service import ExportService
from heic_converter_pro.app.services.file_service import FileService

logger = logging.getLogger(__name__)


class HeicConverter:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._metadata_handler = MetadataHandler()
        self._image_processor = ImageProcessor()
        self._ffmpeg = FfmpegConverter()

    def convert(
        self,
        task: ConversionTask,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> ConversionTask:
        start_time = time.time()
        task.status = TaskStatus.PROCESSING
        try:
            task.original_size = FileService.get_file_size(task.source_path)
            self._report(progress_callback, 0.05)

            image = self._open_image(task.source_path)
            self._report(progress_callback, 0.25)

            if self._settings.preserve_orientation:
                image = self._image_processor.apply_exif_orientation(image)
            self._report(progress_callback, 0.35)

            image = self._apply_transformations(image)
            self._report(progress_callback, 0.55)

            image = self._metadata_handler.preserve_all(
                image, image,
                preserve_exif=self._settings.preserve_exif,
                preserve_icc=self._settings.preserve_icc,
            )
            self._report(progress_callback, 0.75)

            output_path = FileService.generate_output_path(
                source=task.source_path,
                output_format=self._settings.export_format.value,
                template=self._settings.filename_template,
                output_dir=self._resolve_output_dir(task.source_path),
                overwrite=self._settings.overwrite_existing,
            )
            task.output_path = output_path

            ExportService.save(
                image, output_path, self._settings.export_format,
                quality=self._get_quality(),
            )
            self._report(progress_callback, 0.95)

            if not output_path.exists():
                self._ffmpeg_fallback(task, progress_callback)

            task.output_size = FileService.get_file_size(output_path)
            task.elapsed_time = time.time() - start_time
            task.status = TaskStatus.COMPLETED
            task.metadata_preserved = (
                self._settings.preserve_exif or self._settings.preserve_icc
            )
            self._report(progress_callback, 1.0)
            logger.info(
                "Converted %s -> %s in %.2fs",
                task.source_path.name, output_path.name, task.elapsed_time,
            )

        except Exception as exc:
            task.status = TaskStatus.FAILED
            task.error_message = str(exc)
            task.elapsed_time = time.time() - start_time
            logger.exception("Failed to convert %s: %s", task.source_path.name, exc)

        return task

    def _open_image(self, path: Path) -> Image.Image:
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except ImportError:
            logger.debug("pillow-heif not available")

        try:
            image = Image.open(str(path))
        except Exception as exc:
            logger.warning("Pillow failed to open %s, trying FFmpeg: %s", path.name, exc)
            return self._open_via_ffmpeg(path)

        if self._settings.export_format in (ExportFormat.JPG, ExportFormat.TIFF):
            image = self._image_processor.convert_to_rgb(image)
        elif image.mode not in ("RGB", "RGBA", "L", "CMYK"):
            image = image.convert("RGB")
        return image

    def _open_via_ffmpeg(self, path: Path) -> Image.Image:
        if not self._ffmpeg.available:
            raise RuntimeError("Cannot open file: Pillow and FFmpeg both failed")
        import tempfile
        tmp = Path(tempfile.mktemp(suffix=".png"))
        try:
            self._ffmpeg.convert(path, tmp, quality=95, output_format="png")
            image = Image.open(str(tmp))
            return image
        finally:
            if tmp.exists():
                tmp.unlink()

    def _ffmpeg_fallback(
        self, task: ConversionTask,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> None:
        if not self._ffmpeg.available:
            return
        logger.info("FFmpeg fallback for %s", task.source_path.name)
        try:
            output_path = FileService.generate_output_path(
                source=task.source_path,
                output_format=self._settings.export_format.value,
                template=self._settings.filename_template,
                output_dir=self._resolve_output_dir(task.source_path),
                overwrite=True,
            )
            self._ffmpeg.convert(
                task.source_path, output_path,
                quality=self._get_quality(),
                output_format=self._settings.export_format.value,
            )
            task.output_path = output_path
        except Exception as exc:
            logger.error("FFmpeg fallback also failed: %s", exc)

    def _apply_transformations(self, image: Image.Image) -> Image.Image:
        if self._settings.resize_enabled:
            image = self._image_processor.resize(
                image, self._settings.resize_width,
                self._settings.resize_height,
                self._settings.resize_keep_aspect,
            )

        if self._settings.auto_enhance:
            image = self._image_processor.auto_enhance(image)

        if self._settings.brightness != 1.0:
            image = self._image_processor.adjust_brightness(image, self._settings.brightness)
        if self._settings.contrast != 1.0:
            image = self._image_processor.adjust_contrast(image, self._settings.contrast)
        if self._settings.sharpness != 1.0:
            image = self._image_processor.adjust_sharpness(image, self._settings.sharpness)
        if self._settings.saturation != 1.0:
            image = self._image_processor.adjust_saturation(image, self._settings.saturation)
        if self._settings.gamma != 1.0:
            image = self._image_processor.adjust_gamma(image, self._settings.gamma)
        if self._settings.blur_radius > 0:
            image = self._image_processor.apply_blur(image, self._settings.blur_radius)

        if self._settings.rotation != 0:
            image = self._image_processor.rotate(image, self._settings.rotation)
        if self._settings.flip_horizontal and self._settings.flip_vertical:
            image = self._image_processor.flip(image, ImageProcessor.FlipMode.BOTH)
        elif self._settings.flip_horizontal:
            image = self._image_processor.flip(image, ImageProcessor.FlipMode.HORIZONTAL)
        elif self._settings.flip_vertical:
            image = self._image_processor.flip(image, ImageProcessor.FlipMode.VERTICAL)

        if self._settings.watermark_text:
            image = self._image_processor.apply_watermark(
                image, self._settings.watermark_text,
                self._settings.watermark_position,
                self._settings.watermark_opacity,
            )
        if self._settings.border_width > 0:
            hex_color = self._settings.border_color.lstrip("#")
            color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            image = self._image_processor.add_border(
                image, self._settings.border_width, color,
            )

        if self._settings.strip_metadata:
            image = self._metadata_handler.strip_metadata(image)

        return image

    def _resolve_output_dir(self, source_path: Path) -> Optional[Path]:
        from heic_converter_pro.app.models.settings import OutputMode
        mode = self._settings.output_mode
        if mode == OutputMode.SAME_FOLDER:
            return source_path.parent
        elif mode == OutputMode.CUSTOM_FOLDER:
            custom = self._settings.custom_output_folder
            return Path(custom) if custom else source_path.parent
        return None

    def _get_quality(self) -> int:
        if self._settings.export_format == ExportFormat.JPG:
            return self._settings.jpeg_quality
        elif self._settings.export_format == ExportFormat.WEBP:
            return self._settings.webp_quality
        return 95

    @staticmethod
    def _report(callback: Optional[Callable[[float], None]], value: float) -> None:
        if callback:
            callback(value)
