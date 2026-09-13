#!/usr/bin/env python3
"""Read-only landmark inspector for a decrypted BlackBox application image."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

RUNTIME_BASE = 0x02000120

KNOWN_STRINGS = {
    "audio_dev": b"audio_dev\x00",
    "BlackBox_020": b"BlackBox_020\x00",
    "usb_update_mode": b"usb_update_mode\x00",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_all(data: bytes, needle: bytes) -> list[int]:
    offsets: list[int] = []
    start = 0
    while True:
        offset = data.find(needle, start)
        if offset < 0:
            return offsets
        offsets.append(offset)
        start = offset + 1


def app_to_runtime(offset: int) -> int:
    if offset < 0:
        raise ValueError("application offset cannot be negative")
    return RUNTIME_BASE + offset


def decode_uac_endpoints(data: bytes) -> list[dict[str, Any]]:
    """Return standard 9-byte USB endpoint descriptors with audio attributes."""
    endpoints: list[dict[str, Any]] = []
    for offset in range(0, max(0, len(data) - 8)):
        descriptor = data[offset : offset + 9]
        if descriptor[0:2] != b"\x09\x05":
            continue
        address = descriptor[2]
        attributes = descriptor[3]
        # Audio isochronous endpoints have transfer type 1.
        if attributes & 0x03 != 0x01:
            continue
        # Bits 4..6 of bEndpointAddress are reserved, and endpoint zero is the
        # default control endpoint rather than an isochronous stream.
        if address & 0x70 or address & 0x0F == 0:
            continue
        endpoints.append(
            {
                "offset": offset,
                "runtime": app_to_runtime(offset),
                "address": address,
                "direction": "IN" if address & 0x80 else "OUT",
                "endpoint_number": address & 0x0F,
                "attributes": attributes,
                "max_packet_size": int.from_bytes(descriptor[4:6], "little"),
                "interval": descriptor[6],
                "raw": descriptor.hex(" "),
            }
        )
    return endpoints


def inspect(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    strings = {
        label: [
            {"offset": offset, "runtime": app_to_runtime(offset)}
            for offset in find_all(data, value)
        ]
        for label, value in KNOWN_STRINGS.items()
    }
    return {
        "file": str(path),
        "size": len(data),
        "sha256": sha256(data),
        "runtime_base": RUNTIME_BASE,
        "strings": strings,
        "uac_isochronous_endpoints": decode_uac_endpoints(data),
    }


def format_hex(value: int) -> str:
    return f"0x{value:08X}"


def print_human(report: dict[str, Any]) -> None:
    print(f"File: {report['file']}")
    print(f"Size: {report['size']} bytes")
    print(f"SHA-256: {report['sha256']}")
    print(f"Runtime base: {format_hex(report['runtime_base'])}")
    print("\nASCII landmarks:")
    for label, locations in report["strings"].items():
        if not locations:
            print(f"  {label}: not found")
            continue
        rendered = ", ".join(
            f"app {format_hex(item['offset'])} / runtime {format_hex(item['runtime'])}"
            for item in locations
        )
        print(f"  {label}: {rendered}")
    print("\nIsochronous USB endpoint descriptors:")
    for endpoint in report["uac_isochronous_endpoints"]:
        print(
            "  "
            f"app {format_hex(endpoint['offset'])}: "
            f"EP 0x{endpoint['address']:02X} {endpoint['direction']}, "
            f"max packet {endpoint['max_packet_size']}, raw {endpoint['raw']}"
        )


def parse_int(value: str) -> int:
    return int(value, 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, help="decrypted app image")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--app-to-runtime", type=parse_int, metavar="OFFSET")
    parser.add_argument("--runtime-to-app", type=parse_int, metavar="ADDRESS")
    args = parser.parse_args()

    if args.app_to_runtime is not None:
        print(format_hex(app_to_runtime(args.app_to_runtime)))
        return 0
    if args.runtime_to_app is not None:
        if args.runtime_to_app < RUNTIME_BASE:
            parser.error("runtime address is below the application base")
        print(format_hex(args.runtime_to_app - RUNTIME_BASE))
        return 0
    if args.image is None:
        parser.error("provide an image or an address-conversion option")
    if not args.image.is_file():
        parser.error(f"not a file: {args.image}")

    report = inspect(args.image)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
