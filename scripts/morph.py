"""Logo tracing and morph layers for the profile banner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


@dataclass(frozen=True)
class Logo:
    name: str
    viewbox: str
    paths: tuple[str, ...]


def _trace_logo(source: Path, name: str) -> Logo:
    image = cv2.imread(str(source), cv2.IMREAD_COLOR)
    if image is None:
        return Logo(name=name, viewbox="0 0 128 128", paths=())

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mask = _logo_mask(rgb)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return Logo(name=name, viewbox="0 0 128 128", paths=())

    x, y, w, h = cv2.boundingRect(np.vstack(contours))
    pad = int(max(w, h) * 0.08)
    x = max(0, x - pad)
    y = max(0, y - pad)
    w = min(rgb.shape[1] - x, w + pad * 2)
    h = min(rgb.shape[0] - y, h + pad * 2)

    paths = []
    scale_x = 128 / max(w, 1)
    scale_y = 128 / max(h, 1)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 50:
            continue
        epsilon = 0.008 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        pts = [
            (
                round((point[0][0] - x) * scale_x, 2),
                round((point[0][1] - y) * scale_y, 2),
            )
            for point in approx
        ]
        if len(pts) >= 3:
            paths.append(_points_to_path(pts))

    return Logo(name=name, viewbox="0 0 128 128", paths=tuple(paths))


def _logo_mask(rgb: np.ndarray) -> np.ndarray:
    """Return a foreground mask for the raster logo image."""

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, mask = cv2.threshold(blur, 245, 255, cv2.THRESH_BINARY_INV)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8), iterations=2)
    return mask


def _points_to_path(points: list[tuple[float, float]]) -> str:
    start_x, start_y = points[0]
    segments = [f"M{start_x:.2f} {start_y:.2f}"]
    for x, y in points[1:]:
        segments.append(f"L{x:.2f} {y:.2f}")
    segments.append("Z")
    return " ".join(segments)


def _normalize_viewbox(logo: Logo) -> Logo:
    return logo


FLUTTER = _normalize_viewbox(_trace_logo(ASSETS / "flutter logo.png", "flutter"))
CODE = _normalize_viewbox(_trace_logo(ASSETS / "code logo.png", "code"))

DEVELOPER = Logo(
    name="developer",
    viewbox="0 0 128 128",
    paths=(
        "M24 24h80c6 0 12 6 12 12v56c0 6-6 12-12 12H24c-6 0-12-6-12-12V36c0-6 6-12 12-12zm6 20 18 20-18 20 8 8 26-28-26-28zm68 0-8 8 18 20-18 20 8 8 26-28z",
        "M48 92h32v10H48z",
        "M38 42h10v44H38z",
        "M80 42h10v44H80z",
    ),
)


def logo_markup(logo: Logo, fill: str) -> str:
    return logo_group_markup(logo, fill)


def logo_group_markup(logo: Logo, fill: str) -> str:
    paths = "".join(f'<path d="{path}" />' for path in logo.paths)
    return f'<g fill="{fill}">{paths}</g>'


def logo_svg(logo: Logo, fill: str) -> str:
    return f'<svg viewBox="{logo.viewbox}" xmlns="http://www.w3.org/2000/svg">{logo_group_markup(logo, fill)}</svg>'


def morph_layers(fill: str) -> str:
    """Return the centered logo animation layers."""

    return f"""
    <g class="logo-stage">
      <g class="logo logo-flutter">{logo_group_markup(FLUTTER, fill)}</g>
      <g class="logo logo-code">{logo_group_markup(CODE, fill)}</g>
      <g class="logo logo-developer">{logo_group_markup(DEVELOPER, fill)}</g>
    </g>
    """
