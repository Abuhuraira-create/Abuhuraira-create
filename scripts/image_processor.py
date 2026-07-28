"""Portrait preprocessing for the GitHub profile banner.

This module removes the portrait background, preserves the subject as an
RGBA cutout, and keeps the crop focused on the head-and-shoulders region.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def load_portrait(source: str | Path, size: tuple[int, int] = (300, 340)) -> Image.Image:
    """Load, cut out, and fit the portrait into the banner frame."""

    path = Path(source)
    if not path.exists():
        return _fallback_portrait(size)

    image = Image.open(path).convert("RGB")
    image = ImageOps.exif_transpose(image)
    cutout = _remove_background(image)
    cutout = _enhance_cutout(cutout)
    return _fit_subject(cutout, size)


def _remove_background(image: Image.Image) -> Image.Image:
    """Remove the background with GrabCut and light cleanup."""

    rgb = np.array(image)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    h, w = bgr.shape[:2]

    mask = np.zeros((h, w), np.uint8)
    rect = (
        int(w * 0.08),
        int(h * 0.04),
        int(w * 0.84),
        int(h * 0.90),
    )

    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(bgr, mask, rect, bgd_model, fgd_model, 6, cv2.GC_INIT_WITH_RECT)
        alpha = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype("uint8")
    except cv2.error:
        alpha = _heuristic_alpha(rgb)

    alpha = cv2.GaussianBlur(alpha, (7, 7), 0)
    _, alpha = cv2.threshold(alpha, 24, 255, cv2.THRESH_BINARY)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8), iterations=2)

    rgba = cv2.cvtColor(rgb, cv2.COLOR_RGB2RGBA)
    rgba[:, :, 3] = alpha
    return Image.fromarray(rgba, "RGBA")


def _heuristic_alpha(rgb: np.ndarray) -> np.ndarray:
    """Fallback alpha mask for environments where GrabCut struggles."""

    h, w = rgb.shape[:2]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    border = np.concatenate(
        [
            rgb[: max(4, h // 28), :, :].reshape(-1, 3),
            rgb[-max(4, h // 28) :, :, :].reshape(-1, 3),
            rgb[:, : max(4, w // 28), :].reshape(-1, 3),
            rgb[:, -max(4, w // 28) :, :].reshape(-1, 3),
        ]
    )
    bg = np.median(border, axis=0)
    diff = np.linalg.norm(rgb.astype("float32") - bg.astype("float32"), axis=2)
    alpha = np.where((diff > 22) | (gray < 178), 255, 0).astype("uint8")
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8), iterations=2)
    return alpha


def _enhance_cutout(image: Image.Image) -> Image.Image:
    image = ImageEnhance.Color(image).enhance(0.88)
    image = ImageEnhance.Contrast(image).enhance(1.16)
    image = ImageEnhance.Sharpness(image).enhance(1.08)
    image = image.filter(ImageFilter.DETAIL)
    return image


def _fit_subject(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Crop to the visible subject and fit to the target portrait size."""

    bbox = image.getchannel("A").getbbox()
    if bbox:
        x1, y1, x2, y2 = bbox
        w = x2 - x1
        h = y2 - y1
        pad_x = int(w * 0.08)
        pad_y = int(h * 0.12)
        x1 = max(0, x1 - pad_x)
        x2 = min(image.width, x2 + pad_x)
        y1 = max(0, y1 - pad_y)
        y2 = min(image.height, y2 + pad_y)
        image = image.crop((x1, y1, x2, y2))

    return ImageOps.fit(
        image,
        size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.30),
    )


def _fallback_portrait(size: tuple[int, int]) -> Image.Image:
    """Generate a neutral studio-style fallback portrait."""

    width, height = size
    image = Image.new("RGBA", size, (9, 11, 16, 255))
    pixels = image.load()

    for y in range(height):
        mix = y / max(height - 1, 1)
        r = int(16 + 18 * mix)
        g = int(20 + 28 * mix)
        b = int(29 + 36 * mix)
        for x in range(width):
            pixels[x, y] = (r, g, b, 255)

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDrawCompat(overlay)
    draw.ellipse((30, 18, 270, 304), fill=(34, 211, 238, 18))
    draw.ellipse((48, 56, 252, 286), fill=(139, 92, 246, 18))
    draw.ellipse((73, 38, 227, 252), fill=(16, 185, 129, 12))
    draw.rounded_rectangle((62, 146, 238, 322), radius=78, fill=(13, 18, 28, 245))
    draw.ellipse((72, 42, 228, 190), fill=(245, 228, 212, 244))
    draw.ellipse((88, 58, 212, 176), fill=(226, 188, 163, 248))
    draw.rectangle((106, 130, 194, 208), fill=(226, 188, 163, 248))
    draw.polygon([(76, 124), (108, 82), (126, 150)], fill=(42, 47, 63, 220))
    draw.polygon([(224, 124), (192, 82), (174, 150)], fill=(42, 47, 63, 220))
    draw.ellipse((108, 94, 128, 110), fill=(28, 34, 49, 235))
    draw.ellipse((172, 94, 192, 110), fill=(28, 34, 49, 235))
    draw.arc((126, 102, 174, 134), 12, 168, fill=(48, 65, 82, 255), width=3)
    draw.rounded_rectangle((96, 196, 204, 320), radius=42, fill=(22, 28, 41, 246))
    draw.polygon([(96, 220), (61, 296), (115, 332), (132, 252)], fill=(18, 22, 33, 255))
    draw.polygon([(204, 220), (239, 296), (185, 332), (168, 252)], fill=(18, 22, 33, 255))
    draw.rectangle((118, 214, 182, 230), fill=(139, 92, 246, 120))
    draw.rectangle((104, 224, 196, 236), fill=(34, 211, 238, 80))

    return Image.alpha_composite(image, overlay)


class ImageDrawCompat:
    """Lazy import wrapper to keep top-level imports compact."""

    def __init__(self, image: Image.Image):
        from PIL import ImageDraw

        self._draw = ImageDraw.Draw(image, "RGBA")

    def ellipse(self, *args, **kwargs):
        return self._draw.ellipse(*args, **kwargs)

    def rounded_rectangle(self, *args, **kwargs):
        return self._draw.rounded_rectangle(*args, **kwargs)

    def rectangle(self, *args, **kwargs):
        return self._draw.rectangle(*args, **kwargs)

    def polygon(self, *args, **kwargs):
        return self._draw.polygon(*args, **kwargs)

    def arc(self, *args, **kwargs):
        return self._draw.arc(*args, **kwargs)
