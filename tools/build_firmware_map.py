#!/usr/bin/env python3
"""Build a reproducible, non-reconstructible PI32v2 firmware structure map."""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path

BASE = 0x02000120
INSN = re.compile(r"^\s*([0-9a-fA-F]+):\s+((?:(?:[0-9a-fA-F]{2})\s+)+)\t(.*)$")
UNKNOWN = re.compile(r"^\s*([0-9a-fA-F]+):\s+((?:(?:[0-9a-fA-F]{2})\s+)+)<unknown instruction>")
REF = re.compile(r"<[^>]*\+0x([0-9a-fA-F]+)\s*:")
CALL = re.compile(r"\bcall\b")
BRANCH = re.compile(r"\b(?:call|goto|gotoss|jmp)\b")
KEYWORDS = {
    "audio": ("audio", "dac", "adc", "pcm", "i2s", "iis", "mic", "speaker", "encoder", "decoder", "mixer", "volume", "eq", "amp", "cab", "reverb", "delay", "effect", "pitch", "gain"),
    "usb": ("usb", "uac", "udisk", "hid", "cdc"),
    "bluetooth": ("bluetooth", "bt_", "ble", "a2dp", "avrcp", "sbc", "hfp"),
    "ota": ("ota", "upgrade", "update", "uboot", "download"),
    "filesystem": ("jlfs", "fat", "flash", "nor", "nand", "sdfile", "vfs"),
    "ui": ("lcd", "screen", "font", "menu", "ui_", "key", "display"),
    "network": ("wifi", "tcp", "udp", "http", "socket", "dns"),
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            value.update(chunk)
    return value.hexdigest()


def strings(data: bytes, minimum: int = 4) -> list[dict]:
    found, start = [], None
    for offset, byte in enumerate(data + b"\0"):
        if 0x20 <= byte <= 0x7e:
            start = offset if start is None else start
        else:
            if start is not None and offset - start >= minimum:
                found.append({"offset": start, "runtime": BASE + start, "length": offset - start, "value": data[start:offset].decode("ascii")})
            start = None
    return found


def instructions(listing: Path) -> tuple[list[dict], int, int]:
    decoded, unknown_words, unknown_bytes = [], 0, 0
    for line in listing.read_text(encoding="utf-8", errors="replace").splitlines():
        bad = UNKNOWN.match(line)
        if bad:
            unknown_words += 1
            unknown_bytes += len(bad.group(2).split())
            continue
        match = INSN.match(line)
        if not match:
            continue
        offset = int(match.group(1), 16)
        text = match.group(3).rstrip()
        values = [int(value, 16) for value in REF.findall(text)]
        is_branch = bool(BRANCH.search(text))
        refs = [(BASE + value) & 0xffffffff if is_branch else value & 0xffffffff for value in values]
        decoded.append({"offset": offset, "runtime": BASE + offset, "size": len(match.group(2).split()), "text": text, "call": bool(CALL.search(text)), "branch": is_branch, "refs": refs})
    decoded.sort(key=lambda row: row["runtime"])
    if not decoded:
        raise ValueError("no instructions decoded")
    return decoded, unknown_words, unknown_bytes


def merged_ranges(rows: list[dict]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for row in rows:
        start, end = row["offset"], row["offset"] + row["size"]
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(a, b) for a, b in merged]


def gaps(ranges: list[tuple[int, int]], size: int) -> list[tuple[int, int]]:
    result, cursor = [], 0
    for start, end in ranges:
        if start > cursor:
            result.append((cursor, start))
        cursor = max(cursor, end)
    if cursor < size:
        result.append((cursor, size))
    return result


def components(entries: list[int], funcs: dict[int, dict]) -> list[list[int]]:
    edges: dict[int, set[int]] = defaultdict(set)
    for entry, func in funcs.items():
        for callee in func["callees"]:
            edges[entry].add(callee)
            edges[callee].add(entry)
    result, seen = [], set()
    for entry in entries:
        if entry in seen:
            continue
        queue, part = deque([entry]), []
        seen.add(entry)
        while queue:
            current = queue.popleft()
            part.append(current)
            for neighbor in sorted(edges[current]):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        result.append(sorted(part))
    return result


def write_csv_shards(directory: Path, stem: str, header: list[str], rows: list[list], count: int) -> list[str]:
    directory.mkdir(parents=True, exist_ok=True)
    for previous in directory.glob(f"{stem}_*.csv"):
        previous.unlink()
    names = []
    for index in range(0, len(rows), count):
        name = f"{stem}_{index // count:03d}.csv"
        names.append(name)
        with (directory / name).open("w", newline="", encoding="utf-8") as target:
            writer = csv.writer(target, lineterminator="\n", quoting=csv.QUOTE_ALL)
            writer.writerow(header)
            writer.writerows(rows[index:index + count])
    return names


def build(image: Path, listing: Path, symbols_path: Path, output: Path) -> dict:
    data = image.read_bytes()
    end = BASE + len(data)
    decoded, unknown_words, unknown_bytes = instructions(listing)
    text_items = strings(data)
    text_by_runtime = {row["runtime"]: row for row in text_items}
    symbols_doc = json.loads(symbols_path.read_text(encoding="utf-8"))
    reviewed = []
    for item in symbols_doc["symbols"]:
        item = dict(item)
        item["offset"] = int(item["offset"], 0)
        item["runtime"] = BASE + item["offset"]
        reviewed.append(item)
    reviewed_by_runtime = {row["runtime"]: row for row in reviewed}

    calls: Counter[int] = Counter()
    for insn in decoded:
        if insn["call"]:
            for ref in insn["refs"]:
                if BASE <= ref < end:
                    calls[ref] += 1
    entries = sorted({BASE, *calls, *(row["runtime"] for row in reviewed if row["kind"] == "function")})
    funcs: dict[int, dict] = {}
    for index, entry in enumerate(entries):
        partition_end = entries[index + 1] if index + 1 < len(entries) else end
        seed = reviewed_by_runtime.get(entry, {})
        funcs[entry] = {"address": entry, "offset": entry - BASE, "end": partition_end, "size": partition_end - entry,
            "name": seed.get("name", f"FUN_{entry:08X}"), "confidence": seed.get("confidence", "mechanical"),
            "tags": set(seed.get("tags", [])), "instructions": 0, "callers": set(), "callees": set(),
            "call_sites": set(), "string_refs": set(), "indirect_string_refs": set(), "image_refs": set(), "ram_refs": set()}

    def owner(address: int) -> int | None:
        index = bisect.bisect_right(entries, address) - 1
        return entries[index] if index >= 0 and address < funcs[entries[index]]["end"] else None

    for insn in decoded:
        source = owner(insn["runtime"])
        if source is None:
            continue
        func = funcs[source]
        func["instructions"] += 1
        for ref in insn["refs"]:
            if insn["call"] and ref in funcs:
                func["callees"].add(ref)
                funcs[ref]["callers"].add(source)
                funcs[ref]["call_sites"].add(insn["runtime"])
            elif not insn["branch"] and ref in text_by_runtime:
                func["string_refs"].add(ref)
            elif not insn["branch"] and BASE <= ref < end:
                func["image_refs"].add(ref)
            elif not insn["branch"] and 0x01c00000 <= ref < 0x01d00000:
                func["ram_refs"].add(ref)

    string_pointer_sites = []
    for source in range(0, len(data) - 3, 4):
        target = int.from_bytes(data[source:source + 4], "little")
        if target in text_by_runtime:
            string_pointer_sites.append((BASE + source, target))
    string_tables, current = [], []
    for source, target in string_pointer_sites:
        if current and source - current[-1][0] > 48:
            string_tables.append(current)
            current = []
        current.append((source, target))
    if current:
        string_tables.append(current)
    starts = [table[0][0] - 8 for table in string_tables]

    def table_at(address: int):
        index = bisect.bisect_right(starts, address) - 1
        if index < 0:
            return None
        table = string_tables[index]
        return table if address <= table[-1][0] + 8 else None

    for func in funcs.values():
        for reference in func["image_refs"]:
            table = table_at(reference)
            if table:
                func["indirect_string_refs"].update(target for _, target in table)
        all_refs = func["string_refs"] | func["indirect_string_refs"]
        corpus = "\n".join(text_by_runtime[value]["value"].lower() for value in all_refs)
        for tag, words in KEYWORDS.items():
            if any(word in corpus for word in words):
                func["tags"].add(tag)
    parts = components(entries, funcs)
    component_id = {entry: index for index, part in enumerate(parts) for entry in part}

    pointers: dict[int, dict] = {}
    instruction_addresses = {row["runtime"] for row in decoded}
    for source in range(0, len(data) - 3, 2):
        target = int.from_bytes(data[source:source + 4], "little")
        if not BASE <= target < end:
            continue
        item = pointers.setdefault(target, {"sources": [], "kinds": set()})
        if len(item["sources"]) < 64:
            item["sources"].append(source)
        item["kinds"].add("instruction" if target in instruction_addresses else "string" if target in text_by_runtime else "image")

    ranges = merged_ranges(decoded)
    missing = gaps(ranges, len(data))
    decoded_bytes = sum(b - a for a, b in ranges)
    output.mkdir(parents=True, exist_ok=True)
    function_rows = []
    for entry, func in funcs.items():
        function_rows.append([f"0x{entry:08X}", f"0x{func['offset']:X}", f"0x{func['end']:08X}", func["size"], func["name"], func["confidence"],
            "|".join(sorted(func["tags"])), func["instructions"], len(func["callers"]), len(func["callees"]),
            "|".join(f"0x{x:08X}" for x in sorted(func["callers"])), "|".join(f"0x{x:08X}" for x in sorted(func["callees"])),
            "|".join(f"0x{x:08X}" for x in sorted(func["string_refs"])),
            "|".join(f"0x{x:08X}" for x in sorted(func["indirect_string_refs"])), component_id[entry]])
    string_rows = [[f"0x{x['offset']:X}", f"0x{x['runtime']:08X}", x["length"], x["value"]] for x in text_items]
    gap_rows = [[f"0x{a:X}", f"0x{b:X}", b - a] for a, b in missing]
    pointer_rows = [[f"0x{target:08X}", "|".join(sorted(item["kinds"])), "|".join(f"0x{x:X}" for x in item["sources"])] for target, item in sorted(pointers.items())]
    table_rows = [[f"0x{table[0][0]:08X}", f"0x{table[-1][0] + 4:08X}", len(table),
        "|".join(f"0x{target:08X}" for _, target in table),
        "|".join(text_by_runtime[target]["value"] for _, target in table[:8])] for table in string_tables]
    files = {
        "functions": write_csv_shards(output / "functions", "functions", ["address","offset","partition_end","partition_size","name","confidence","tags","instructions","caller_count","callee_count","callers","callees","string_refs","indirect_string_refs","component"], function_rows, 75),
        "strings": write_csv_shards(output / "strings", "strings", ["offset","runtime","length","value"], string_rows, 400),
        "gaps": write_csv_shards(output / "gaps", "gaps", ["start_offset","end_offset","length"], gap_rows, 600),
        "pointers": write_csv_shards(output / "pointers", "pointers", ["target","kinds","source_offsets"], pointer_rows, 200),
        "string_tables": write_csv_shards(output / "string_tables", "string_tables", ["start","end","pointer_count","targets","sample"], table_rows, 100),
    }
    counts = {"recognized_instructions": len(decoded), "unknown_instruction_words": unknown_words,
        "unknown_instruction_bytes": unknown_bytes, "decoded_bytes": decoded_bytes,
        "decoded_byte_coverage_percent": round(100 * decoded_bytes / len(data), 4), "decoder_gaps": len(missing),
        "direct_call_sites": sum(calls.values()), "direct_call_targets": len(calls), "function_entries_with_seeds": len(funcs),
        "printable_ascii_strings": len(text_items), "string_pointer_sites": len(string_pointer_sites),
        "string_table_regions": len(string_tables),
        "functions_with_any_string_refs": sum(bool(f["string_refs"] or f["indirect_string_refs"]) for f in funcs.values()),
        "raw_image_pointer_targets": len(pointers), "weak_callgraph_components": len(parts)}
    manifest = {"schema": 1, "input": {"size": len(data), "sha256": digest(image), "runtime_base": f"0x{BASE:08X}", "runtime_end": f"0x{end:08X}"},
        "decoder": "JieLi LLVM objdump 4.0.1 / ELF32-pi32v2", "counts": counts, "shards": files,
        "limitations": ["Linear decoding does not prove every covered byte is executable code.", "Entries are direct-call targets plus reviewed seeds.", "Partition ends are mechanical.", "Indirect-only callbacks require further review."]}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    landmarks = [{**{key: value for key, value in item.items() if key != "offset"}, "offset": f"0x{item['offset']:X}", "runtime": f"0x{item['runtime']:08X}"} for item in reviewed]
    (output / "landmarks.json").write_text(json.dumps({"symbols": landmarks}, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("listing", type=Path)
    parser.add_argument("--symbols", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.image, args.listing, args.symbols, args.output)["counts"], indent=2))


if __name__ == "__main__":
    main()
