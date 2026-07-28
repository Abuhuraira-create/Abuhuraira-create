"""Floyd-Steinberg dithering utilities.

The banner renderer uses this module to turn a portrait into a stable
binary dot field that can be exported as SVG paths.
"""

from __future__ import annotations

from PIL import Image


def floyd_steinberg(image: Image.Image) -> Image.Image:
    """Return a 1-bit dithering-friendly grayscale image.

    The function keeps the work in standard Pillow primitives so it stays
    lightweight and easy to run in CI environments.
    """

    gray = image.convert("L")
    pixels = gray.load()
    width, height = gray.size

    for y in range(height):
        for x in range(width):
            old_value = pixels[x, y]
            new_value = 255 if old_value >= 128 else 0
            pixels[x, y] = new_value
            error = old_value - new_value

            if x + 1 < width:
                pixels[x + 1, y] = _clamp(pixels[x + 1, y] + error * 7 / 16)
            if x - 1 >= 0 and y + 1 < height:
                pixels[x - 1, y + 1] = _clamp(pixels[x - 1, y + 1] + error * 3 / 16)
            if y + 1 < height:
                pixels[x, y + 1] = _clamp(pixels[x, y + 1] + error * 5 / 16)
            if x + 1 < width and y + 1 < height:
                pixels[x + 1, y + 1] = _clamp(pixels[x + 1, y + 1] + error * 1 / 16)

    return gray.point(lambda value: 255 if value >= 128 else 0)


def _clamp(value: float) -> int:
    return max(0, min(255, int(round(value))))
