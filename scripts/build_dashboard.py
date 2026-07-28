"""Build the full profile dashboard (banner + stats + snake + badges) as one SVG.

Reuses the banner's header/portrait/info-panel markup from build_banner.py and
appends stat cards, a contribution-snake panel, social badges, and a tech-stack
row below it, all inside one continuous frame.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from build_banner import DARK, LIGHT, Theme, banner_body, banner_defs
from image_processor import load_portrait
from morph import FLUTTER, logo_group_markup
from optimize_svg import optimize

ROOT = Path(__file__).resolve().parent.parent

WIDTH = 1180
BANNER_H = 610
GAP = 18
ROW2_H = 210
ROW3_H = 230
ROW4_H = 110
FOOTER_H = 48
MARGIN = 20

ROW2_Y = BANNER_H + GAP
ROW3_Y = ROW2_Y + ROW2_H + GAP
ROW4_Y = ROW3_Y + ROW3_H + GAP
FOOTER_Y = ROW4_Y + ROW4_H + GAP
HEIGHT = FOOTER_Y + FOOTER_H + MARGIN

CONTENT_X = MARGIN
CONTENT_W = WIDTH - MARGIN * 2
CARD_GAP = 18
CARD_W = (CONTENT_W - CARD_GAP * 2) // 3

LANGS = [
    ("Dart", 78.2),
    ("Kotlin", 8.7),
    ("Python", 6.4),
    ("JavaScript", 4.8),
    ("Other", 1.9),
]

WEEK = [3, 5, 4, 6, 3, 5, 8]
WEEK_LABELS = ["M", "T", "W", "T", "F", "S", "S"]


def main() -> int:
    portrait = load_portrait(str(ROOT / "assets" / "my_pic.png"))
    (ROOT / "dashboard-dark.svg").write_text(optimize(build_dashboard(DARK, portrait)), encoding="utf-8")
    (ROOT / "dashboard-light.svg").write_text(optimize(build_dashboard(LIGHT, portrait)), encoding="utf-8")
    return 0


def build_dashboard(theme: Theme, portrait: Image.Image) -> str:
    body = banner_body(theme, portrait)
    lang_color = {
        "Dart": theme.primary,
        "Kotlin": theme.secondary,
        "Python": theme.accent,
        "JavaScript": "#F59E0B",
        "Other": theme.muted,
    }

    return f"""<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Abu Huraira Ahmed profile dashboard">
{banner_defs(theme)}
<rect width="{WIDTH}" height="{HEIGHT}" rx="20" fill="url(#{theme.name}-bg)" />
<rect x="10" y="10" width="{WIDTH - 20}" height="{HEIGHT - 20}" rx="14" fill="{theme.background}" stroke="{theme.border}" />
{body}
{streak_card(CONTENT_X, ROW2_Y, CARD_W, ROW2_H, theme)}
{stats_card(CONTENT_X + CARD_W + CARD_GAP, ROW2_Y, CARD_W, ROW2_H, theme)}
{toplangs_card(CONTENT_X + (CARD_W + CARD_GAP) * 2, ROW2_Y, CARD_W, ROW2_H, theme, lang_color)}
{snake_card(CONTENT_X, ROW3_Y, CARD_W * 2 + CARD_GAP, ROW3_H, theme)}
{connect_card(CONTENT_X + CARD_W * 2 + CARD_GAP * 2, ROW3_Y, CARD_W, ROW3_H, theme)}
{techstack_card(CONTENT_X, ROW4_Y, CONTENT_W, ROW4_H, theme)}
{footer_bar(CONTENT_X, FOOTER_Y, CONTENT_W, FOOTER_H, theme)}
</svg>"""


def _panel(x: int, y: int, w: int, h: int, theme: Theme, title: str, icon: str = "") -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" class="panel" />'
        f'<text x="{x + 20}" y="{y + 32}" class="mono title" style="font-size:14px">{icon}{title}</text>'
    )


def streak_card(x: int, y: int, w: int, h: int, theme: Theme) -> str:
    cx, cy, r = x + 92, y + 118, 54
    circumference = 2 * 3.14159265 * r
    pct = 0.62
    dash = circumference * pct
    bars = []
    bar_x = x + 168
    bar_w = (w - 188) / 7
    max_bar = 56
    max_val = max(WEEK)
    for i, (val, label) in enumerate(zip(WEEK, WEEK_LABELS)):
        bh = 10 + (val / max_val) * max_bar
        bx = bar_x + i * bar_w
        by = y + 150 - bh
        fill = theme.primary if i == len(WEEK) - 1 else theme.secondary
        bars.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w * 0.5:.1f}" height="{bh:.1f}" rx="3" fill="{fill}" opacity="0.9" />')
        bars.append(f'<text x="{bx + bar_w * 0.25:.1f}" y="{y + 168}" text-anchor="middle" class="mono meta" style="font-size:10px">{label}</text>')
    return f"""{_panel(x, y, w, h, theme, "GitHub Streak", "&#128293; ")}
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{theme.border}" stroke-width="9" />
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{theme.secondary}" stroke-width="9" stroke-linecap="round"
  stroke-dasharray="{dash:.1f} {circumference:.1f}" transform="rotate(-90 {cx} {cy})" />
<text x="{cx}" y="{cy - 4}" text-anchor="middle" class="mono value" style="font-size:26px" fill="{theme.primary}">32</text>
<text x="{cx}" y="{cy + 16}" text-anchor="middle" class="mono meta" style="font-size:10px">Day Streak</text>
{"".join(bars)}
<text x="{x + 20}" y="{y + h - 16}" class="mono label" fill="{theme.accent}" style="font-size:12px">Keep it going!</text>"""


def stats_card(x: int, y: int, w: int, h: int, theme: Theme) -> str:
    rows = [
        ("&#9733;", "Total Stars", "42"),
        ("&#128279;", "Total Commits", "612"),
        ("&#8645;", "Pull Requests", "38"),
        ("&#128193;", "Repositories", "26"),
        ("&#128200;", "Contributions", "320"),
    ]
    lines = []
    ry = y + 58
    value_x = x + w - 112
    for icon, label, value in rows:
        lines.append(f'<text x="{x + 20}" y="{ry}" class="mono label" style="font-size:12px">{icon} {label}</text>')
        lines.append(f'<text x="{value_x}" y="{ry}" text-anchor="end" class="mono value" style="font-size:12px" fill="{theme.primary}">{value}</text>')
        ry += 24
    ring_cx, ring_cy, ring_r = x + w - 54, y + h // 2 + 12, 40
    circumference = 2 * 3.14159265 * ring_r
    dash = circumference * 0.92
    return f"""{_panel(x, y, w, h, theme, "GitHub Stats", "&#128202; ")}
{"".join(lines)}
<circle cx="{ring_cx}" cy="{ring_cy}" r="{ring_r}" fill="none" stroke="{theme.border}" stroke-width="7" />
<circle cx="{ring_cx}" cy="{ring_cy}" r="{ring_r}" fill="none" stroke="{theme.secondary}" stroke-width="7" stroke-linecap="round"
  stroke-dasharray="{dash:.1f} {circumference:.1f}" transform="rotate(-90 {ring_cx} {ring_cy})" />
<text x="{ring_cx}" y="{ring_cy - 2}" text-anchor="middle" class="mono value" style="font-size:15px" fill="{theme.primary}">92%</text>
<text x="{ring_cx}" y="{ring_cy + 14}" text-anchor="middle" class="mono meta" style="font-size:8px">Commits</text>"""


def toplangs_card(x: int, y: int, w: int, h: int, theme: Theme, lang_color: dict) -> str:
    lines = []
    ry = y + 56
    track_x = x + 96
    track_w = w - 96 - 54
    for name, pct in LANGS:
        color = lang_color[name]
        fill_w = track_w * (pct / 100)
        lines.append(f'<text x="{x + 20}" y="{ry}" class="mono label" style="font-size:12px">{name}</text>')
        lines.append(f'<rect x="{track_x}" y="{ry - 10}" width="{track_w}" height="8" rx="4" fill="{theme.border}" />')
        lines.append(f'<rect x="{track_x}" y="{ry - 10}" width="{fill_w:.1f}" height="8" rx="4" fill="{color}" />')
        lines.append(f'<text x="{x + w - 20}" y="{ry}" text-anchor="end" class="mono value" style="font-size:12px">{pct}%</text>')
        ry += 30
    return f"""{_panel(x, y, w, h, theme, "Top Languages", "&#128187; ")}
{"".join(lines)}"""


def snake_card(x: int, y: int, w: int, h: int, theme: Theme) -> str:
    grid = []
    cols = 46
    rows = 6
    cell = 12
    gx0 = x + 20
    gy0 = y + 44
    empty = theme.border
    for r in range(rows):
        for c in range(cols):
            gx = gx0 + c * cell
            gy = gy0 + r * cell
            grid.append(f'<rect x="{gx}" y="{gy}" width="9" height="9" rx="2" fill="{empty}" opacity="0.5" />')

    amplitude = 30
    mid = gy0 + (rows * cell) / 2
    path_pts = []
    span = cols * cell
    steps = 60
    for i in range(steps + 1):
        px = gx0 + span * i / steps
        py = mid + amplitude * _sin(i / steps * 3.14159265 * 3)
        path_pts.append(f"{px:.1f} {py:.1f}")
    path_d = "M" + " L".join(path_pts)

    return f"""{_panel(x, y, w, h, theme, "Contribution Snake", "&#128034; ")}
{"".join(grid)}
<path d="{path_d}" fill="none" stroke="{theme.accent}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" opacity="0.92" />
<text x="{x + w / 2:.0f}" y="{y + h - 16}" text-anchor="middle" class="mono label" fill="{theme.accent}" style="font-size:12px">Keep contributing, keep growing!</text>"""


def _sin(theta: float) -> float:
    # tiny Taylor-series sine so this module has no extra runtime dependency
    theta = theta % (2 * 3.14159265)
    if theta > 3.14159265:
        theta -= 2 * 3.14159265
    t2 = theta * theta
    return theta * (1 - t2 / 6 * (1 - t2 / 20 * (1 - t2 / 42)))


SOCIALS = [
    ("LinkedIn", "0A66C2", "in"),
    ("Instagram", "8B5CF6", "ig"),
    ("Facebook", "1877F2", "f"),
    ("Email", "10B981", "@"),
    ("Portfolio", "22D3EE", "pf"),
]


def connect_card(x: int, y: int, w: int, h: int, theme: Theme) -> str:
    tiles = []
    tile = 52
    gap = (w - 40 - tile * 5) / 4
    tx = x + 20
    ty = y + 52
    for name, color, glyph in SOCIALS:
        tiles.append(f'<rect x="{tx:.1f}" y="{ty}" width="{tile}" height="{tile}" rx="13" fill="#{color}" />')
        tiles.append(f'<text x="{tx + tile / 2:.1f}" y="{ty + tile / 2 + 5}" text-anchor="middle" class="mono value" style="font-size:12px" fill="#FFFFFF">{glyph}</text>')
        tiles.append(f'<text x="{tx + tile / 2:.1f}" y="{ty + tile + 16}" text-anchor="middle" class="mono meta" style="font-size:7px">{name}</text>')
        tx += tile + gap
    return f"""{_panel(x, y, w, h, theme, "Connect With Me", "&#127760; ")}
{"".join(tiles)}"""


TECH = [
    ("Flutter", "22D3EE"),
    ("Dart", "0175C2"),
    ("Git", "F05032"),
    ("GitHub", "9198A1"),
    ("Android Studio", "3DDC84"),
    ("Figma", "A259FF"),
    ("VS Code", "007ACC"),
]


def _icon_dart(cx: float, cy: float, color: str) -> str:
    return (
        f'<polygon points="{cx - 13},{cy + 7} {cx + 1},{cy - 13} {cx + 15},{cy - 1} {cx + 1},{cy + 15}" fill="{color}" />'
        f'<polygon points="{cx + 1},{cy - 13} {cx + 15},{cy - 1} {cx + 1},{cy + 15}" fill="{color}" opacity="0.55" />'
    )


def _icon_git(cx: float, cy: float, color: str) -> str:
    return (
        f'<line x1="{cx - 8:.1f}" y1="{cy + 8:.1f}" x2="{cx + 8:.1f}" y2="{cy - 8:.1f}" stroke="{color}" stroke-width="2.4" />'
        f'<polygon points="{cx - 8},{cy} {cx},{cy - 8} {cx + 8},{cy} {cx},{cy + 8}" fill="{color}" />'
        f'<circle cx="{cx + 11:.1f}" cy="{cy - 11:.1f}" r="4" fill="none" stroke="{color}" stroke-width="2.2" />'
    )


def _icon_github(cx: float, cy: float, color: str) -> str:
    return (
        f'<circle cx="{cx}" cy="{cy + 1}" r="11" fill="{color}" />'
        f'<polygon points="{cx - 11},{cy - 4} {cx - 4},{cy - 4} {cx - 9},{cy - 13}" fill="{color}" />'
        f'<polygon points="{cx + 11},{cy - 4} {cx + 4},{cy - 4} {cx + 9},{cy - 13}" fill="{color}" />'
        f'<circle cx="{cx - 4.5:.1f}" cy="{cy}" r="1.6" fill="#0B0E15" />'
        f'<circle cx="{cx + 4.5:.1f}" cy="{cy}" r="1.6" fill="#0B0E15" />'
    )


def _icon_android_studio(cx: float, cy: float, color: str) -> str:
    return (
        f'<polygon points="{cx},{cy - 13} {cx - 13},{cy + 11} {cx + 13},{cy + 11}" fill="{color}" />'
        f'<polygon points="{cx},{cy - 2} {cx - 7},{cy + 11} {cx + 7},{cy + 11}" fill="#0B0E15" opacity="0.35" />'
    )


def _icon_figma(cx: float, cy: float, color: str) -> str:
    return (
        f'<circle cx="{cx}" cy="{cy - 7}" r="6" fill="#F24E1E" />'
        f'<circle cx="{cx - 7:.1f}" cy="{cy + 5}" r="6" fill="#A259FF" />'
        f'<circle cx="{cx + 7:.1f}" cy="{cy + 5}" r="6" fill="#1ABCFE" />'
    )


def _icon_vscode(cx: float, cy: float, color: str) -> str:
    return (
        f'<polygon points="{cx - 9},{cy - 13} {cx + 12},{cy} {cx - 9},{cy + 13} {cx - 3},{cy + 13} {cx + 15},{cy} {cx - 3},{cy - 13}" fill="{color}" />'
    )


TECH_ICONS = {
    "Dart": _icon_dart,
    "Git": _icon_git,
    "GitHub": _icon_github,
    "Android Studio": _icon_android_studio,
    "Figma": _icon_figma,
    "VS Code": _icon_vscode,
}


def techstack_card(x: int, y: int, w: int, h: int, theme: Theme) -> str:
    tile = 58
    n = len(TECH)
    gap = (w - 40 - tile * n) / (n - 1)
    tx = x + 20
    ty = y + h - 20 - tile
    tiles = []
    for name, color in TECH:
        tiles.append(f'<rect x="{tx:.1f}" y="{ty}" width="{tile}" height="{tile}" rx="14" fill="{theme.panel}" stroke="#{color}" stroke-width="2" />')
        cx, cy = tx + tile / 2, ty + tile / 2
        if name == "Flutter":
            tiles.append(f'<g transform="translate({tx + 13:.1f} {ty + 13:.1f}) scale(0.25)">{logo_group_markup(FLUTTER, "#" + color)}</g>')
        else:
            tiles.append(TECH_ICONS[name](cx, cy, "#" + color))
        tiles.append(f'<text x="{tx + tile / 2:.1f}" y="{ty + tile + 16}" text-anchor="middle" class="mono meta" style="font-size:9px">{name}</text>')
        tx += tile + gap
    return f"""{_panel(x, y, w, h, theme, "Tech Stack", "&#128736; ")}
{"".join(tiles)}"""


def footer_bar(x: int, y: int, w: int, h: int, theme: Theme) -> str:
    return f"""<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" class="panel" />
<text x="{x + 20}" y="{y + h / 2 + 5:.0f}" class="mono value" style="font-size:13px">&gt; Code. Learn. Build. Improve. Repeat.</text>
<text x="{x + w - 20}" y="{y + h / 2 + 5:.0f}" text-anchor="end" class="mono value" style="font-size:13px" fill="{theme.secondary}">Thanks for visiting!</text>"""


if __name__ == "__main__":
    raise SystemExit(main())
