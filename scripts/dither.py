"""Floyd-Steinberg dithering utilities.

The banner renderer uses this module to turn a portrait into a stable
binary dot field that can be exported as SVG paths.
"""

from __future__ import annotations

from PIL import Image


def floyd_steinberg(image: Image.Image) -> Image.Image:
    """Return a 1-bit dithering-friendly grayscale image.

    Uses serpentine (boustrophedon) scan order — alternating left-to-right
    and right-to-left per row — which avoids the directional streaking a
    single-direction scan leaves in flat tone regions like skin and walls.
    """

    gray = image.convert("L")
    pixels = gray.load()
    width, height = gray.size

    for y in range(height):
        serpentine = y % 2 == 1
        direction = -1 if serpentine else 1
        x_range = range(width - 1, -1, -1) if serpentine else range(width)

        for x in x_range:
            old_value = pixels[x, y]
            new_value = 255 if old_value >= 128 else 0
            pixels[x, y] = new_value
            error = old_value - new_value

            if 0 <= x + direction < width:
                pixels[x + direction, y] = _clamp(pixels[x + direction, y] + error * 7 / 16)
            if 0 <= x - direction < width and y + 1 < height:
                pixels[x - direction, y + 1] = _clamp(pixels[x - direction, y + 1] + error * 3 / 16)
            if y + 1 < height:
                pixels[x, y + 1] = _clamp(pixels[x, y + 1] + error * 5 / 16)
            if 0 <= x + direction < width and y + 1 < height:
                pixels[x + direction, y + 1] = _clamp(pixels[x + direction, y + 1] + error * 1 / 16)

    return gray.point(lambda value: 255 if value >= 128 else 0)


def _clamp(value: float) -> int:
    return max(0, min(255, int(round(value))))
