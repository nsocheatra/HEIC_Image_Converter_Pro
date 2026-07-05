from __future__ import annotations

import logging
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter as PILFilter, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class FlipMode(Enum):
    NONE = auto()
    HORIZONTAL = auto()
    VERTICAL = auto()
    BOTH = auto()


class ResizeMode(Enum):
    FIT = auto()
    FILL = auto()
    STRETCH = auto()
    CROP = auto()


class ImageProcessor:
    @staticmethod
    def resize(
        image: Image.Image,
        target_width: int,
        target_height: int,
        keep_aspect: bool = True,
        mode: ResizeMode = ResizeMode.FIT,
        resample: int = Image.LANCZOS,
    ) -> Image.Image:
        if not keep_aspect or mode == ResizeMode.STRETCH:
            return image.resize((target_width, target_height), resample)

        orig_w, orig_h = image.size
        aspect = orig_w / orig_h
        target_aspect = target_width / target_height

        if mode == ResizeMode.CROP:
            if aspect > target_aspect:
                new_h = target_height
                new_w = int(target_height * aspect)
            else:
                new_w = target_width
                new_h = int(target_width / aspect)
            resized = image.resize((new_w, new_h), resample)
            left = (new_w - target_width) // 2
            top = (new_h - target_height) // 2
            return resized.crop((left, top, left + target_width, top + target_height))

        if aspect > target_aspect:
            new_w = target_width
            new_h = int(target_width / aspect)
        else:
            new_h = target_height
            new_w = int(target_height * aspect)
        return image.resize((new_w, new_h), resample)

    @staticmethod
    def resize_by_percentage(
        image: Image.Image, percentage: float, resample: int = Image.LANCZOS
    ) -> Image.Image:
        w, h = image.size
        nw = int(w * percentage / 100)
        nh = int(h * percentage / 100)
        return image.resize((nw, nh), resample)

    @staticmethod
    def rotate(image: Image.Image, degrees: int, expand: bool = True) -> Image.Image:
        return image.rotate(degrees, resample=Image.BICUBIC, expand=expand)

    @staticmethod
    def flip(image: Image.Image, mode: FlipMode) -> Image.Image:
        if mode == FlipMode.HORIZONTAL:
            return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif mode == FlipMode.VERTICAL:
            return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        elif mode == FlipMode.BOTH:
            image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        return image

    @staticmethod
    def crop(image: Image.Image, left: int, top: int, right: int, bottom: int) -> Image.Image:
        return image.crop((left, top, right, bottom))

    @staticmethod
    def adjust_brightness(image: Image.Image, factor: float) -> Image.Image:
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(max(0.0, factor))

    @staticmethod
    def adjust_contrast(image: Image.Image, factor: float) -> Image.Image:
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(max(0.0, factor))

    @staticmethod
    def adjust_sharpness(image: Image.Image, factor: float) -> Image.Image:
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(max(0.0, factor))

    @staticmethod
    def adjust_saturation(image: Image.Image, factor: float) -> Image.Image:
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(max(0.0, factor))

    @staticmethod
    def apply_blur(image: Image.Image, radius: int = 3) -> Image.Image:
        return image.filter(PILFilter.GaussianBlur(radius=radius))

    @staticmethod
    def apply_sharpen(image: Image.Image, factor: float = 2.0) -> Image.Image:
        return image.filter(PILFilter.UnsharpMask(radius=2, percent=int(factor * 100), threshold=0))

    @staticmethod
    def adjust_gamma(image: Image.Image, gamma: float) -> Image.Image:
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGBA")
        elif image.mode != "RGB":
            image = image.convert("RGB")

        if image.mode == "RGBA":
            r, g, b, a = image.split()
            r = r.point(lambda v: int(255 * (v / 255) ** (1 / max(gamma, 0.01))))
            g = g.point(lambda v: int(255 * (v / 255) ** (1 / max(gamma, 0.01))))
            b = b.point(lambda v: int(255 * (v / 255) ** (1 / max(gamma, 0.01))))
            return Image.merge("RGBA", (r, g, b, a))
        else:
            inv_gamma = 1.0 / max(gamma, 0.01)
            table = [int(255 * (i / 255) ** inv_gamma) for i in range(256)]
            return image.point(table * 3)

    @staticmethod
    def apply_watermark(
        image: Image.Image,
        text: str,
        position: str = "bottom_right",
        opacity: int = 128,
        font_size: int = 36,
        color: Tuple[int, int, int] = (255, 255, 255),
    ) -> Image.Image:
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (IOError, OSError):
            try:
                font = ImageFont.truetype("segoeui.ttf", font_size)
            except (IOError, OSError):
                font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        margin = 20

        positions = {
            "top_left": (margin, margin),
            "top_right": (image.width - tw - margin, margin),
            "bottom_left": (margin, image.height - th - margin),
            "bottom_right": (image.width - tw - margin, image.height - th - margin),
            "center": ((image.width - tw) // 2, (image.height - th) // 2),
        }
        xy = positions.get(position, positions["bottom_right"])
        draw.text(xy, text, font=font, fill=(*color, opacity))
        return Image.alpha_composite(image, overlay)

    @staticmethod
    def add_border(
        image: Image.Image,
        border_width: int = 5,
        color: Tuple[int, int, int] = (0, 0, 0),
    ) -> Image.Image:
        if image.mode == "RGBA":
            bg = Image.new("RGBA", (image.width + border_width * 2, image.height + border_width * 2), (*color, 255))
            bg.paste(image, (border_width, border_width), image)
            return bg
        else:
            from PIL import ImageOps
            return ImageOps.expand(image, border=border_width, fill=color)

    @staticmethod
    def apply_exif_orientation(image: Image.Image) -> Image.Image:
        try:
            exif = image.getexif()
            orientation = exif.get(0x0112)
            if orientation is None:
                return image
            trans = {
                2: Image.Transpose.FLIP_LEFT_RIGHT,
                3: Image.Transpose.ROTATE_180,
                4: Image.Transpose.FLIP_TOP_BOTTOM,
                5: Image.Transpose.TRANSPOSE,
                6: Image.Transpose.ROTATE_270,
                7: Image.Transpose.TRANSVERSE,
                8: Image.Transpose.ROTATE_90,
            }
            method = trans.get(orientation)
            if method is not None:
                return image.transpose(method)
        except Exception as exc:
            logger.warning("Failed to apply EXIF orientation: %s", exc)
        return image

    @staticmethod
    def convert_to_rgb(image: Image.Image, background: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
        if image.mode == "RGBA":
            bg = Image.new("RGB", image.size, background)
            bg.paste(image, mask=image.split()[3])
            return bg
        elif image.mode != "RGB":
            return image.convert("RGB")
        return image

    @staticmethod
    def auto_enhance(image: Image.Image) -> Image.Image:
        enh = ImageEnhance.Contrast(image)
        image = enh.enhance(1.1)
        enh = ImageEnhance.Sharpness(image)
        image = enh.enhance(1.2)
        enh = ImageEnhance.Color(image)
        image = enh.enhance(1.05)
        return image
