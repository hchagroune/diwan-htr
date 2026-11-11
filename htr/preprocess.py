"""Image preparation applied identically to examples, new pages and fine-tuning data."""
from __future__ import annotations

import io

from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = 400_000_000  # archive scans can be very large


def prepare_image(data: bytes, max_side: int = 3072, grayscale: bool = True,
                  autocontrast: bool = True, quality: int = 92) -> bytes:
    im = Image.open(io.BytesIO(data))
    im = ImageOps.exif_transpose(im)
    im = im.convert("L") if grayscale else im.convert("RGB")
    if autocontrast:
        im = ImageOps.autocontrast(im, cutoff=1)
    scale = max_side / max(im.size)
    if scale < 1:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.Resampling.LANCZOS)
    out = io.BytesIO()
    im.save(out, format="JPEG", quality=quality, optimize=True)
    return out.getvalue()


def prepare_from_settings(data: bytes, settings) -> bytes:
    p = settings.preprocess
    return prepare_image(data, p.max_side, p.grayscale, p.autocontrast)
