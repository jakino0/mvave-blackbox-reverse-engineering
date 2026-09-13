#!/usr/bin/env python3
"""Fail if a public checkout contains forbidden artifacts or identifiers."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = {".apk", ".bin", ".fwsc", ".ufw", ".img", ".log", ".pdf"}
SERIAL_PATTERN = re.compile(r"serial(?:_number)?\s*[=:]\s*[A-Za-z0-9-]{8,}", re.I)
MAC_PATTERN = re.compile(r"\b(?:[0-9A-F]{2}:){5}[0-9A-F]{2}\b", re.I)


def main() -> int:
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            failures.append(f"forbidden artifact: {relative}")
            continue
        if path.suffix.lower() not in {".md", ".txt", ".py", ".yml", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in (("serial", SERIAL_PATTERN), ("MAC", MAC_PATTERN)):
            if pattern.search(text):
                failures.append(f"possible {label} in {relative}")
    if failures:
        print("Repository hygiene check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Repository hygiene check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
