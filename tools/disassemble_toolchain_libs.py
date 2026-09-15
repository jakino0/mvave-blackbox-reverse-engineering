#!/usr/bin/env python3
"""Create LOCAL listings for PI32v2 libraries used as signature references."""

import argparse
from pathlib import Path
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("toolchain", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root = args.toolchain.resolve()
    objdump = root / "common/bin/objdump"
    libraries = sorted((root / "pi32v2/lib").rglob("*.a"))
    if not objdump.is_file() or not libraries:
        raise SystemExit("incomplete JieLi PI32v2 toolchain")
    args.output.mkdir(parents=True, exist_ok=True)
    for library in libraries:
        relative = library.relative_to(root / "pi32v2/lib").as_posix().replace("/", "_")
        target = args.output / f"{relative}.txt"
        result = subprocess.run([str(objdump), "-d", str(library)], check=True, capture_output=True, text=True)
        target.write_text(result.stdout, encoding="utf-8")
    print(f"library listings: {len(libraries)}")


if __name__ == "__main__":
    main()
