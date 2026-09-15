#!/usr/bin/env python3
"""Create a LOCAL byte-bearing listing with the official JieLi toolchain.

The input is never executed or modified. Do not commit the generated listing.
"""

import argparse
from pathlib import Path
import subprocess
import tempfile


def disassemble(image: Path, toolchain: Path, output: Path) -> None:
    image, toolchain, output = image.resolve(), toolchain.resolve(), output.resolve()
    if output == image:
        raise ValueError("output must not replace the input image")
    compiler = toolchain / "pi32v2/bin/cc"
    objdump = toolchain / "common/bin/objdump"
    for executable in (compiler, objdump):
        if not executable.is_file():
            raise ValueError("incomplete JieLi toolchain")
    with tempfile.TemporaryDirectory(prefix="blackbox-decode-") as directory:
        work = Path(directory)
        (work / "image.bin").symlink_to(image)
        (work / "wrap.S").write_text(
            '.section .fw,"ax",@progbits\n.global firmware\nfirmware:\n.incbin "image.bin"\n',
            encoding="ascii",
        )
        subprocess.run([str(compiler), "-c", "wrap.S", "-o", "wrap.o"], cwd=work, check=True)
        result = subprocess.run(
            [str(objdump), "-d", "-section=.fw", "wrap.o"],
            cwd=work, check=True, capture_output=True, text=True,
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result.stdout, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("toolchain", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    disassemble(args.image, args.toolchain, args.output)


if __name__ == "__main__":
    main()
