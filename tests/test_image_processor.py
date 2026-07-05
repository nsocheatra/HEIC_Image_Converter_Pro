from __future__ import annotations

from PIL import Image

from heic_converter_pro.app.core.image_processor import ImageProcessor, FlipMode, ResizeMode


class TestImageProcessor:
    def setup_method(self) -> None:
        self.image = Image.new("RGB", (200, 100), (255, 0, 0))

    def test_resize_fit(self) -> None:
        result = ImageProcessor.resize(self.image, 100, 100, keep_aspect=True)
        assert result.size == (100, 50)

    def test_resize_stretch(self) -> None:
        result = ImageProcessor.resize(self.image, 100, 100, keep_aspect=False)
        assert result.size == (100, 100)

    def test_resize_by_percentage(self) -> None:
        result = ImageProcessor.resize_by_percentage(self.image, 50)
        assert result.size == (100, 50)

    def test_rotate_90(self) -> None:
        result = ImageProcessor.rotate(self.image, 90)
        assert result.size == (100, 200)

    def test_flip_horizontal(self) -> None:
        result = ImageProcessor.flip(self.image, FlipMode.HORIZONTAL)
        assert result.size == (200, 100)

    def test_flip_vertical(self) -> None:
        result = ImageProcessor.flip(self.image, FlipMode.VERTICAL)
        assert result.size == (200, 100)

    def test_brightness(self) -> None:
        result = ImageProcessor.adjust_brightness(self.image, 2.0)
        assert result.size == (200, 100)

    def test_contrast(self) -> None:
        result = ImageProcessor.adjust_contrast(self.image, 1.5)
        assert result.size == (200, 100)

    def test_sharpness(self) -> None:
        result = ImageProcessor.adjust_sharpness(self.image, 2.0)
        assert result.size == (200, 100)

    def test_saturation(self) -> None:
        result = ImageProcessor.adjust_saturation(self.image, 1.5)
        assert result.size == (200, 100)

    def test_gamma(self) -> None:
        result = ImageProcessor.adjust_gamma(self.image, 1.5)
        assert result.size == (200, 100)

    def test_blur(self) -> None:
        result = ImageProcessor.apply_blur(self.image, 5)
        assert result.size == (200, 100)

    def test_watermark(self) -> None:
        result = ImageProcessor.apply_watermark(self.image, "Test", opacity=64)
        assert result.size == (200, 100)

    def test_border(self) -> None:
        result = ImageProcessor.add_border(self.image, 10)
        assert result.size == (220, 120)

    def test_crop(self) -> None:
        result = ImageProcessor.crop(self.image, 0, 0, 100, 50)
        assert result.size == (100, 50)

    def test_convert_to_rgb_rgba(self) -> None:
        rgba = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        result = ImageProcessor.convert_to_rgb(rgba)
        assert result.mode == "RGB"

    def test_auto_enhance(self) -> None:
        result = ImageProcessor.auto_enhance(self.image)
        assert result.size == (200, 100)
