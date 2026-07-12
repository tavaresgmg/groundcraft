#!/usr/bin/env python3
"""Report version drift for mutable upstream references without changing the repository."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "docs" / "sources.md"
CHECKS = (
    ("gstack", r"gstack ([0-9.]+)", "https://raw.githubusercontent.com/garrytan/gstack/main/VERSION", "text"),
    ("OpenSpec", r"OpenSpec ([0-9.]+)", "https://api.github.com/repos/Fission-AI/OpenSpec/releases/latest", "release"),
    ("GitHub Spec Kit", r"GitHub Spec Kit ([0-9.]+)", "https://api.github.com/repos/github/spec-kit/releases/latest", "release"),
)


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "groundcraft-source-check"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8")


def normalize(value: str) -> str:
    return value.strip().removeprefix("v")


def main() -> int:
    text = SOURCES.read_text(encoding="utf-8")
    stale = 0
    unavailable = 0
    for name, pattern, url, kind in CHECKS:
        match = re.search(pattern, text)
        documented = match.group(1) if match else "missing"
        try:
            raw = fetch(url)
            current = normalize(json.loads(raw)["tag_name"] if kind == "release" else raw)
        except (OSError, urllib.error.URLError, json.JSONDecodeError, KeyError) as exc:
            unavailable += 1
            print(f"unavailable\t{name}\tdocumented={documented}\t{exc}")
            continue
        status = "current" if documented == current else "stale"
        stale += status == "stale"
        print(f"{status}\t{name}\tdocumented={documented}\tcurrent={current}")
    if stale:
        return 1
    return 2 if unavailable else 0


if __name__ == "__main__":
    raise SystemExit(main())
