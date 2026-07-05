from __future__ import annotations

from PIL import Image

from heic_converter_pro.app.core.metadata import MetadataHandler


class TestMetadataHandler:
    def setup_method(self) -> None:
        self.image = Image.new("RGB", (100, 100), (255, 0, 0))

    def test_get_exif_empty(self) -> None:
        result = MetadataHandler.get_exif(self.image)
        assert isinstance(result, dict)

    def test_get_gps_empty(self) -> None:
        result = MetadataHandler.get_gps_info(self.image)
        assert result is None

    def test_get_icc_empty(self) -> None:
        result = MetadataHandler.get_icc_profile(self.image)
        assert result is None

    def test_strip_metadata(self) -> None:
        result = MetadataHandler.strip_metadata(self.image)
        assert result.size == self.image.size

    def test_get_readable_metadata(self) -> None:
        result = MetadataHandler.get_readable_metadata(self.image)
        assert "size" in result
        assert "mode" in result
        assert result["size"] == "100 x 100"
        assert result["mode"] == "RGB"

    def test_preserve_all_roundtrip(self) -> None:
        target = Image.new("RGB", (50, 50), (0, 255, 0))
        result = MetadataHandler.preserve_all(self.image, target)
        assert result.size == (50, 50)
