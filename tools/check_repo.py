#!/usr/bin/env python3
"""Fail if a public checkout contains forbidden artifacts or identifiers."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = {
    ".a", ".apk", ".bin", ".dex", ".exe", ".fwsc", ".img", ".log",
    ".o", ".pdf", ".so", ".tar", ".ufw", ".zip",
}
FORBIDDEN_NAMES = (".tar.gz", ".tar.xz")
SERIAL_PATTERN = re.compile(r"serial(?:_number)?\s*[=:]\s*[A-Za-z0-9-]{8,}", re.I)
MAC_PATTERN = re.compile(r"\b(?:[0-9A-F]{2}:){5}[0-9A-F]{2}\b", re.I)
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PRIVATE_PATH_PATTERN = re.compile(r"(?:/workspace/|/root/|[A-Z]:\\\\Users\\\\)", re.I)
PRIVATE_SOURCE_PATTERN = re.compile(
    r"(?:BLACKBOX_MASTER_SOURCE|Pasted text|Correzione-|Verifica-(?:Debug|patch))",
    re.I,
)
TEXT_SUFFIXES = {".csv", ".java", ".json", ".md", ".py", ".sh", ".txt", ".yaml", ".yml"}


def main() -> int:
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or path.name.lower().endswith(FORBIDDEN_NAMES):
            failures.append(f"forbidden artifact: {relative}")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        patterns = (("serial", SERIAL_PATTERN), ("MAC", MAC_PATTERN), ("email", EMAIL_PATTERN))
        if path.name != "check_repo.py":
            patterns += (("private path", PRIVATE_PATH_PATTERN), ("private source name", PRIVATE_SOURCE_PATTERN))
        for label, pattern in patterns:
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
