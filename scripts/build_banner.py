"""Generate the profile banner, SVG assets, and preview image."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from dither import floyd_steinberg
from image_processor import load_portrait
from morph import CODE, DEVELOPER, FLUTTER, logo_markup, logo_svg
from optimize_svg import optimize


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"


@dataclass(frozen=True)
class Theme:
    name: str
    background: str
    panel: str
    border: str
    primary: str
    secondary: str
    accent: str
    danger: str
    text: str
    muted: str
    shell: str
    title: str


DARK = Theme(
    name="dark",
    background="#090B10",
    panel="#10141D",
    border="#1C2333",
    primary="#22D3EE",
    secondary="#8B5CF6",
    accent="#10B981",
    danger="#EF4444",
    text="#FFFFFF",
    muted="#94A3B8",
    shell="#070A0F",
    title="#10B981",
)

LIGHT = Theme(
    name="light",
    background="#F8FAFC",
    panel="#FFFFFF",
    border="#CBD5E1",
    primary="#0891B2",
    secondary="#6D28D9",
    accent="#059669",
    danger="#DC2626",
    text="#0F172A",
    muted="#475569",
    shell="#E2E8F0",
    title="#059669",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build dark.svg, light.svg, and preview.png")
    parser.add_argument("--avatar", default=str(ASSETS / "my_pic.png"))
    parser.add_argument("--output", default=str(ROOT))
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    portrait = load_portrait(args.avatar)
    write_logo_assets(output)

    (output / "dark.svg").write_text(optimize(build_banner(DARK, portrait)), encoding="utf-8")
    (output / "light.svg").write_text(optimize(build_banner(LIGHT, portrait)), encoding="utf-8")
    build_preview(output / "preview.png")
    generate_snake_assets(output)
    return 0


def banner_defs(theme: Theme) -> str:
    return f"""<defs>
  <linearGradient id="{theme.name}-bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{theme.background}" />
    <stop offset="100%" stop-color="{theme.panel}" />
  </linearGradient>
  <radialGradient id="{theme.name}-glow" cx="50%" cy="34%" r="66%">
    <stop offset="0%" stop-color="{theme.secondary}" stop-opacity="0.16" />
    <stop offset="48%" stop-color="{theme.primary}" stop-opacity="0.08" />
    <stop offset="100%" stop-color="{theme.background}" stop-opacity="0" />
  </radialGradient>
  <clipPath id="{theme.name}-portrait-clip"><rect x="28" y="68" width="404" height="354" rx="20" /></clipPath>
  <clipPath id="{theme.name}-center-clip"><rect x="498" y="90" width="210" height="240" rx="18" /></clipPath>
  <style>
    .mono {{ font-family: "JetBrains Mono", "IBM Plex Mono", monospace; }}
    .root {{ font-family: Inter, "JetBrains Mono", "IBM Plex Mono", sans-serif; }}
    .frame {{ fill: url(#{theme.name}-bg); }}
    .panel {{ fill: {theme.panel}; stroke: {theme.border}; }}
    .live {{ fill: {theme.danger}; }}
    .title {{ fill: {theme.title}; font-size: 16px; font-weight: 700; letter-spacing: 0.32px; }}
    .meta {{ fill: {theme.muted}; font-size: 12px; letter-spacing: 1.6px; text-transform: uppercase; }}
    .label {{ fill: {theme.muted}; font-size: 13px; }}
    .value {{ fill: {theme.text}; font-size: 13px; font-weight: 600; }}
    .leader {{ fill: {theme.muted}; font-size: 13px; letter-spacing: 1.2px; }}
    .badge {{ fill: {theme.background}; stroke: {theme.border}; }}
    .glow {{ fill: url(#{theme.name}-glow); }}
    .dot {{ opacity: 0; animation: dotIn 1.1s ease-out forwards; transform-origin: center; }}
    .logo {{ opacity: 0; animation: morph 14s cubic-bezier(.4,0,.2,1) infinite; transform-origin: center; }}
    .logo-portrait {{ animation-delay: 0s; }}
    .logo-flutter {{ animation-delay: 3.5s; }}
    .logo-code {{ animation-delay: 7s; }}
    .logo-developer {{ animation-delay: 10.5s; }}
    .portrait-glow {{ animation: breathe 7s ease-in-out infinite; }}
    .cursor {{ animation: cursor 1.05s steps(1) infinite; }}
    @keyframes dotIn {{
      from {{ opacity: 0; transform: translateY(5px) scale(0.82); }}
      34% {{ opacity: 0.9; }}
      to {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    @keyframes breathe {{
      0%, 100% {{ transform: scale(1); }}
      50% {{ transform: scale(1.01); }}
    }}
    @keyframes morph {{
      0%, 14% {{ opacity: 0; transform: translateY(6px) scale(0.94); }}
      18%, 32% {{ opacity: 1; transform: translateY(0) scale(1); }}
      36%, 100% {{ opacity: 0; transform: translateY(-6px) scale(0.95); }}
    }}
    @keyframes cursor {{
      0%, 49% {{ opacity: 1; }}
      50%, 100% {{ opacity: 0; }}
    }}
  </style>
</defs>"""


def build_banner(theme: Theme, portrait: Image.Image) -> str:
    body = banner_body(theme, portrait)

    return f"""<svg width="1180" height="610" viewBox="0 0 1180 610" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Abu Huraira Ahmed profile banner">
{banner_defs(theme)}

<rect width="1180" height="610" rx="20" class="frame" />
<rect x="18" y="18" width="1144" height="574" rx="14" fill="{theme.background}" stroke="{theme.border}" />
<rect x="28" y="28" width="1124" height="554" rx="12" fill="{theme.background}" stroke="{theme.border}" />
{body}
</svg>"""


def banner_body(theme: Theme, portrait: Image.Image) -> str:
    portrait_svg = portrait_layers(portrait, theme)
    center_svg = morph_layers(theme)

    return f"""<rect x="28" y="28" width="1124" height="40" rx="12" fill="{theme.shell}" stroke="{theme.border}" />
<circle cx="52" cy="48" r="5" fill="{theme.danger}" />
<circle cx="70" cy="48" r="5" fill="{theme.accent}" />
<circle cx="88" cy="48" r="5" fill="{theme.primary}" />
<text x="112" y="52" class="mono title">profile.sh --live</text>
<rect x="1068" y="37" width="70" height="22" rx="11" fill="{theme.background}" stroke="{theme.danger}" />
<circle cx="1082" cy="48" r="4" fill="{theme.danger}" />
<text x="1103" y="52" class="mono value" fill="{theme.danger}">LIVE</text>

<rect x="28" y="80" width="404" height="360" rx="14" class="panel" />
<rect x="28" y="80" width="404" height="360" rx="14" class="glow" />
<text x="46" y="114" class="mono meta" transform="rotate(-90 46 114)">VISUAL MAP</text>
  <g clip-path="url(#{theme.name}-portrait-clip)">
  <rect x="28" y="68" width="404" height="354" rx="20" fill="{theme.name == 'dark' and '#0B0E15' or '#EEF2F7'}" />
  <g class="portrait-glow">{portrait_svg}</g>
  <text x="42" y="74" class="mono meta" transform="rotate(-90 42 74)">VISUAL MAP</text>
</g>
<text x="44" y="422" class="mono meta">SCANLINE 100%</text>

<rect x="462" y="80" width="256" height="360" rx="14" class="panel" />
<text x="492" y="112" class="mono meta">MORPH</text>
<g clip-path="url(#{theme.name}-center-clip)">
  <circle cx="600" cy="205" r="84" fill="none" stroke="{theme.primary}" stroke-dasharray="3 8" stroke-width="2" opacity="0.9" />
  <path d="M600 114v-18M600 314v18" stroke="{theme.primary}" stroke-width="2" stroke-linecap="round" opacity="0.9" />
  <path d="M600 102l-6 10h12z" fill="{theme.primary}" />
  <path d="M600 326l-6-10h12z" fill="{theme.secondary}" />
  <g transform="translate(538 150) scale(0.96)">{center_svg}</g>
</g>
<text x="510" y="338" class="mono value">clean motion / traced marks</text>
<text x="510" y="364" class="mono meta">flutter / code / developer</text>

<rect x="748" y="80" width="404" height="360" rx="14" class="panel" />
<text x="772" y="112" class="mono title">SYSTEM.INFO</text>
<circle cx="1118" cy="106" r="5" fill="{theme.danger}" />
<text x="1132" y="112" class="mono value" fill="{theme.danger}">LIVE</text>
{system_rows(theme)}

<rect x="28" y="458" width="1124" height="56" rx="12" class="panel" />
<text x="48" y="491" class="mono value">$ whoami</text>
<text x="154" y="491" class="mono label">developer // problem solver // continuous learner</text>
<text x="944" y="491" class="mono label">Uptime:</text>
<text x="1020" y="491" class="mono value" fill="{theme.accent}">24/7</text>"""


def portrait_layers(portrait: Image.Image, theme: Theme) -> str:
    subject = portrait.convert("RGBA").resize((300, 340), Image.Resampling.LANCZOS)
    alpha = subject.getchannel("A")
    rgb = Image.new("RGB", subject.size, "#FFFFFF" if theme.name == "light" else "#0B0E15")
    rgb.paste(subject.convert("RGB"), mask=alpha)
    dithered = floyd_steinberg(rgb)
    pixels = dithered.load()
    alpha_pixels = alpha.load()

    fill = theme.secondary if theme.name == "dark" else theme.primary
    strokes = []
    step = 6
    for y in range(0, 340, step):
        for x in range(0, 300, step):
            if alpha_pixels[x, y] < 20:
                continue
            darkness = 255 - pixels[x, y]
            if darkness < 70:
                continue
            radius = 0.9 + (darkness / 255) * 1.9
            cx = 44 + x + step / 2
            cy = 96 + y + step / 2
            delay = ((x * 17 + y * 13) % 1600) + 60
            opacity = 0.25 + (darkness / 255) * 0.72
            strokes.append(
                f'<circle class="dot" cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.2f}" '
                f'fill="{fill}" style="animation-delay:{delay}ms; opacity:{opacity:.2f}" />'
            )
    return "".join(strokes)


def morph_layers(theme: Theme) -> str:
    flutter_svg = logo_markup(FLUTTER, theme.primary)
    code_svg = logo_markup(CODE, theme.secondary)
    dev_svg = logo_markup(DEVELOPER, theme.accent)
    return f"""
      <g transform="translate(0 0)">
        <g class="logo logo-flutter">{flutter_svg}</g>
        <g class="logo logo-code">{code_svg}</g>
        <g class="logo logo-developer">{dev_svg}</g>
      </g>
    """


def system_rows(theme: Theme) -> str:
    rows = [
        ("name", "Abu Huraira Ahmed"),
        ("role", "Flutter Developer"),
        ("status", "Building • Learning • Shipping"),
        ("location", "Pakistan"),
        ("github", "Abuhuraira-create"),
        ("focus", "Mobile Apps • Clean Code • UX"),
        ("toolchain", "VS Code • Git • Android Studio • Figma"),
        ("languages", "Dart"),
        ("framework", "Flutter"),
        ("currently", "Crafting scalable &amp; delightful apps"),
    ]

    lines = []
    y = 140
    for label, value in rows:
        dots = "." * max(4, 23 - len(label))
        lines.append(f'<text x="772" y="{y}" class="mono label">{label}</text>')
        lines.append(f'<text x="852" y="{y}" class="mono leader">{dots}</text>')
        lines.append(f'<text x="1136" y="{y}" text-anchor="end" class="mono value">{value}</text>')
        y += 24
    return "".join(lines)


def build_preview(path: Path) -> None:
    image = Image.new("RGB", (1600, 1000), "#090B10")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((40, 40, 1560, 420), radius=34, fill="#10141D", outline="#1C2333", width=3)
    draw.text((80, 78), "Abu Huraira Ahmed", fill="#FFFFFF", font=_font(54, bold=True))
    draw.text((80, 144), "Flutter Developer - Pakistan", fill="#94A3B8", font=_font(28))
    draw.rounded_rectangle((40, 470, 760, 940), radius=34, fill="#10141D", outline="#1C2333", width=3)
    draw.rounded_rectangle((800, 470, 1560, 940), radius=34, fill="#10141D", outline="#1C2333", width=3)
    draw.text((80, 512), "Featured Projects", fill="#FFFFFF", font=_font(40, bold=True))
    draw.text((840, 512), "Workflow", fill="#FFFFFF", font=_font(40, bold=True))
    draw.text((80, 580), "SpendViz", fill="#22D3EE", font=_font(28, bold=True))
    draw.text((80, 638), "PV Mohalla", fill="#8B5CF6", font=_font(28, bold=True))
    draw.text((80, 696), "Receipt OCR", fill="#10B981", font=_font(28, bold=True))
    draw.text((80, 754), "AI Automation", fill="#EF4444", font=_font(28, bold=True))
    steps = [
        "Replace assets/my_pic.png",
        "Replace assets/flutter logo.png and assets/code logo.png",
        "Run python scripts/build_banner.py",
        "Commit dark.svg, light.svg, preview.png",
        "Deploy GitHub Readme Stats to Vercel",
    ]
    sy = 584
    for step in steps:
        draw.rounded_rectangle((840, sy, 1508, sy + 52), radius=14, fill="#090B10", outline="#1C2333", width=2)
        draw.text((868, sy + 14), step, fill="#E2E8F0", font=_font(22))
        sy += 66
    image.save(path, quality=95)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\consola.ttf",
        r"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        r"/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ]
    if bold:
        candidates = [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ] + candidates
    for candidate in candidates:
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def write_logo_assets(output: Path) -> None:
    (output / "assets").mkdir(exist_ok=True)
    (output / "assets" / "flutter.svg").write_text(logo_svg(FLUTTER, "#22D3EE"), encoding="utf-8")
    (output / "assets" / "code.svg").write_text(logo_svg(CODE, "#8B5CF6"), encoding="utf-8")
    (output / "assets" / "developer.svg").write_text(logo_svg(DEVELOPER, "#10B981"), encoding="utf-8")


def generate_snake_assets(output: Path) -> None:
    snake_dark = """<svg width="1180" height="140" viewBox="0 0 1180 140" xmlns="http://www.w3.org/2000/svg"><rect width="1180" height="140" rx="22" fill="#090B10" stroke="#1C2333"/><path d="M80 96c36-60 112-60 148 0s112 60 148 0 112-60 148 0 112 60 148 0 112-60 148 0" fill="none" stroke="#22D3EE" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/><g fill="#1C2333"><rect x="80" y="34" width="26" height="26" rx="6"/><rect x="124" y="28" width="26" height="26" rx="6"/><rect x="168" y="34" width="26" height="26" rx="6"/><rect x="212" y="46" width="26" height="26" rx="6"/><rect x="256" y="58" width="26" height="26" rx="6"/><rect x="300" y="52" width="26" height="26" rx="6"/><rect x="344" y="40" width="26" height="26" rx="6"/><rect x="388" y="34" width="26" height="26" rx="6"/><rect x="432" y="46" width="26" height="26" rx="6"/><rect x="476" y="58" width="26" height="26" rx="6"/><rect x="520" y="52" width="26" height="26" rx="6"/><rect x="564" y="40" width="26" height="26" rx="6"/><rect x="608" y="34" width="26" height="26" rx="6"/><rect x="652" y="46" width="26" height="26" rx="6"/><rect x="696" y="58" width="26" height="26" rx="6"/><rect x="740" y="52" width="26" height="26" rx="6"/><rect x="784" y="40" width="26" height="26" rx="6"/><rect x="828" y="34" width="26" height="26" rx="6"/><rect x="872" y="46" width="26" height="26" rx="6"/><rect x="916" y="58" width="26" height="26" rx="6"/><rect x="960" y="52" width="26" height="26" rx="6"/></g></svg>"""
    snake_light = """<svg width="1180" height="140" viewBox="0 0 1180 140" xmlns="http://www.w3.org/2000/svg"><rect width="1180" height="140" rx="22" fill="#F8FAFC" stroke="#CBD5E1"/><path d="M80 96c36-60 112-60 148 0s112 60 148 0 112-60 148 0 112 60 148 0 112-60 148 0" fill="none" stroke="#8B5CF6" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/><g fill="#CBD5E1"><rect x="80" y="34" width="26" height="26" rx="6"/><rect x="124" y="28" width="26" height="26" rx="6"/><rect x="168" y="34" width="26" height="26" rx="6"/><rect x="212" y="46" width="26" height="26" rx="6"/><rect x="256" y="58" width="26" height="26" rx="6"/><rect x="300" y="52" width="26" height="26" rx="6"/><rect x="344" y="40" width="26" height="26" rx="6"/><rect x="388" y="34" width="26" height="26" rx="6"/><rect x="432" y="46" width="26" height="26" rx="6"/><rect x="476" y="58" width="26" height="26" rx="6"/><rect x="520" y="52" width="26" height="26" rx="6"/><rect x="564" y="40" width="26" height="26" rx="6"/><rect x="608" y="34" width="26" height="26" rx="6"/><rect x="652" y="46" width="26" height="26" rx="6"/><rect x="696" y="58" width="26" height="26" rx="6"/><rect x="740" y="52" width="26" height="26" rx="6"/><rect x="784" y="40" width="26" height="26" rx="6"/><rect x="828" y="34" width="26" height="26" rx="6"/><rect x="872" y="46" width="26" height="26" rx="6"/><rect x="916" y="58" width="26" height="26" rx="6"/><rect x="960" y="52" width="26" height="26" rx="6"/></g></svg>"""
    (output / "assets").mkdir(exist_ok=True)
    (output / "assets" / "snake-dark.svg").write_text(optimize(snake_dark), encoding="utf-8")
    (output / "assets" / "snake-light.svg").write_text(optimize(snake_light), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
