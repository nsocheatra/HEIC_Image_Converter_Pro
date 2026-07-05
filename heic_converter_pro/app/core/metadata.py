from __future__ import annotations

import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from PIL import Image

logger = logging.getLogger(__name__)


class MetadataHandler:
    @staticmethod
    def get_exif(image: Image.Image) -> dict[str, Any]:
        result = {}
        try:
            import piexif
            exif_bytes = image.info.get("exif")
            if exif_bytes:
                exif_dict = piexif.load(exif_bytes)
                for ifd_name in ("0th", "Exif", "GPS", "Interop", "1st"):
                    ifd = exif_dict.get(ifd_name, {})
                    for tag, value in ifd.items():
                        tag_name = piexif.TAGS.get(ifd_name, {}).get(tag, {}).get("name", str(tag))
                        result[tag_name] = value
        except ImportError:
            exif_data = image.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = Image.ExifTags.TAGS.get(tag_id, str(tag_id))
                    result[tag_name] = value
        except Exception as exc:
            logger.warning("Failed to read EXIF: %s", exc)
        return result

    @staticmethod
    def get_gps_info(image: Image.Image) -> Optional[dict[str, Any]]:
        try:
            import piexif
            exif_bytes = image.info.get("exif")
            if exif_bytes:
                exif_dict = piexif.load(exif_bytes)
                gps = exif_dict.get("GPS", {})
                if gps:
                    result = {}
                    for tag, value in gps.items():
                        tag_name = piexif.GPS_TAGS.get(tag, str(tag))
                        result[tag_name] = value
                    return result
        except ImportError:
            exif = image.getexif()
            gps_ifd = exif.get_ifd(0x8825) if exif else None
            if gps_ifd:
                return {
                    Image.ExifTags.GPSTAGS.get(k, str(k)): v
                    for k, v in gps_ifd.items()
                }
        except Exception as exc:
            logger.warning("Failed to read GPS: %s", exc)
        return None

    @staticmethod
    def get_icc_profile(image: Image.Image) -> Optional[bytes]:
        return image.info.get("icc_profile")

    @staticmethod
    def get_exif_bytes(image: Image.Image) -> Optional[bytes]:
        try:
            import piexif
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}}
            exif_bytes = piexif.dump(exif_dict)
            return exif_bytes
        except ImportError:
            exif_data = image.getexif()
            if exif_data:
                return exif_data.tobytes()
        except Exception:
            pass
        return image.info.get("exif")

    @staticmethod
    def strip_metadata(image: Image.Image) -> Image.Image:
        clean = Image.new(image.mode, image.size)
        clean.putdata(list(image.getdata()))
        if "exif" in clean.info:
            del clean.info["exif"]
        if "icc_profile" in clean.info:
            del clean.info["icc_profile"]
        if "dpi" in clean.info:
            del clean.info["dpi"]
        return clean

    @staticmethod
    def preserve_exif(
        source: Image.Image, target: Image.Image, exif_bytes: Optional[bytes] = None
    ) -> Image.Image:
        try:
            if exif_bytes is None:
                exif_bytes = source.info.get("exif")
            if exif_bytes:
                target.info["exif"] = exif_bytes
        except Exception as exc:
            logger.warning("Failed to preserve EXIF: %s", exc)
        return target

    @staticmethod
    def preserve_icc(
        source: Image.Image, target: Image.Image, icc_bytes: Optional[bytes] = None
    ) -> Image.Image:
        try:
            if icc_bytes is None:
                icc_bytes = source.info.get("icc_profile")
            if icc_bytes:
                target.info["icc_profile"] = icc_bytes
        except Exception as exc:
            logger.warning("Failed to preserve ICC: %s", exc)
        return target

    @staticmethod
    def preserve_all(
        source: Image.Image,
        target: Image.Image,
        preserve_exif: bool = True,
        preserve_icc: bool = True,
    ) -> Image.Image:
        if preserve_exif:
            MetadataHandler.preserve_exif(source, target)
        if preserve_icc:
            MetadataHandler.preserve_icc(source, target)
        return target

    @staticmethod
    def overwrite_exif(image: Image.Image, datetime_original: Optional[str] = None) -> Image.Image:
        try:
            import piexif
            exif_bytes = image.info.get("exif")
            if exif_bytes:
                exif_dict = piexif.load(exif_bytes)
            else:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "Interop": {}, "1st": {}}
            if datetime_original:
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = datetime_original
            else:
                now = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = now
            image.info["exif"] = piexif.dump(exif_dict)
        except ImportError:
            pass
        except Exception as exc:
            logger.warning("Failed to overwrite EXIF: %s", exc)
        return image

    @staticmethod
    def get_readable_metadata(image: Image.Image) -> dict[str, Any]:
        meta = {}
        exif = MetadataHandler.get_exif(image)
        if exif:
            meta["exif"] = {}
            for k, v in exif.items():
                if isinstance(v, bytes):
                    try:
                        v = v.decode("utf-8", errors="replace")
                    except Exception:
                        v = str(v)
                meta["exif"][k] = str(v)[:100]
        gps = MetadataHandler.get_gps_info(image)
        if gps:
            meta["gps"] = {}
            for k, v in gps.items():
                if isinstance(v, bytes):
                    try:
                        v = v.decode("utf-8", errors="replace")
                    except Exception:
                        v = str(v)
                meta["gps"][k] = str(v)[:100]
        icc = MetadataHandler.get_icc_profile(image)
        if icc:
            meta["icc_profile"] = f"{len(icc)} bytes"
        meta["size"] = f"{image.width} x {image.height}"
        meta["mode"] = image.mode
        return meta
