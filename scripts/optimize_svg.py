"""Tiny SVG optimizer used after banner generation."""

from __future__ import annotations

import re
import sys
from pathlib import Path


_WS = re.compile(r">\s+<")
_MULTISPACE = re.compile(r"\s{2,}")


def optimize(content: str) -> str:
    content = re.sub(r"<!--.*?-->", "", content, flags=re.S)
    content = _WS.sub("><", content)
    content = _MULTISPACE.sub(" ", content)
    content = content.replace("\n", "").replace("\t", "")
    return content.strip()


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python scripts/optimize_svg.py <file> [<file> ...]")
        return 1

    for entry in argv[1:]:
        path = Path(entry)
        if path.exists() and path.suffix.lower() == ".svg":
            path.write_text(optimize(path.read_text(encoding="utf-8")), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
