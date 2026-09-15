#!/usr/bin/env python3
"""Find conservative PI32v2 function candidates in JieLi toolchain libraries."""

import argparse
import bisect
import csv
import re
from collections import defaultdict
from pathlib import Path

from build_firmware_map import BASE, INSN

LABEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_.$]*)\s*:\s*$")
ANNOTATION = re.compile(r"<[^>]*>")
NUMBER = re.compile(r"(?<![A-Za-z_])(0x[0-9a-fA-F]+|-?\d+)")


def canonical(text: str) -> str:
    text = ANNOTATION.sub("", text)
    text = NUMBER.sub("#", text)
    return re.sub(r"\s+", " ", text).strip()


def library_functions(paths: list[Path], minimum: int) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for path in paths:
        name, lines = None, []

        def save() -> None:
            if name and len(lines) >= minimum:
                result["\n".join(lines)].append((name, path.name))

        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            match = LABEL.match(line)
            if match:
                save()
                name, lines = match.group(1), []
                continue
            match = INSN.match(line)
            if match and name is not None:
                lines.append(canonical(match.group(3)))
        save()
    return result


def mapped_entries(directory: Path) -> tuple[list[int], dict[int, int]]:
    entries, ends = [], {}
    for path in sorted(directory.glob("functions_*.csv")):
        with path.open(encoding="utf-8", newline="") as source:
            for row in csv.DictReader(source):
                entry = int(row["address"], 16)
                entries.append(entry)
                ends[entry] = int(row["partition_end"], 16)
    return sorted(entries), ends


def app_functions(listing: Path, directory: Path) -> dict[int, list[str]]:
    entries, ends = mapped_entries(directory)
    result: dict[int, list[str]] = defaultdict(list)
    for line in listing.read_text(encoding="utf-8", errors="replace").splitlines():
        match = INSN.match(line)
        if not match:
            continue
        address = BASE + int(match.group(1), 16)
        index = bisect.bisect_right(entries, address) - 1
        if index < 0:
            continue
        entry = entries[index]
        if address < ends[entry]:
            result[entry].append(canonical(match.group(3)))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("listing", type=Path)
    parser.add_argument("functions", type=Path)
    parser.add_argument("library_listings", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--symbols-output", type=Path)
    parser.add_argument("--minimum-instructions", type=int, default=10)
    args = parser.parse_args()
    signatures = library_functions(sorted(args.library_listings.glob("*.txt")), args.minimum_instructions)
    prefix: dict[str, list[tuple[list[str], list[tuple[str, str]]]]] = defaultdict(list)
    for value, hits in signatures.items():
        sequence = value.split("\n")
        prefix["\n".join(sequence[:args.minimum_instructions])].append((sequence, hits))
    matches = []
    for address, sequence in sorted(app_functions(args.listing, args.functions).items()):
        if len(sequence) < args.minimum_instructions:
            continue
        hits = signatures.get("\n".join(sequence), [])
        kind, length = "exact-partition", len(sequence)
        if not hits:
            key = "\n".join(sequence[:args.minimum_instructions])
            candidates = [(len(candidate), values) for candidate, values in prefix.get(key, []) if len(candidate) <= len(sequence) and sequence[:len(candidate)] == candidate]
            if not candidates:
                continue
            length = max(size for size, _ in candidates)
            hits = [hit for size, values in candidates if size == length for hit in values]
            kind = "library-prefix"
        names = sorted({name for name, _ in hits})
        sources = sorted({source for _, source in hits})
        matches.append([f"0x{address:08X}", kind, length, len(sequence), "|".join(names), "|".join(sources)])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target, lineterminator="\n", quoting=csv.QUOTE_ALL)
        writer.writerow(["address", "match", "matched_instructions", "partition_instructions", "candidate_names", "library_sources"])
        writer.writerows(matches)
    if args.symbols_output:
        promoted = []
        for address, kind, matched, partition, names, sources in matches:
            candidates = names.split("|")
            if kind == "exact-partition" and len(candidates) == 1:
                promoted.append([address, candidates[0], "exact-toolchain-match", matched, sources])
        args.symbols_output.parent.mkdir(parents=True, exist_ok=True)
        with args.symbols_output.open("w", encoding="utf-8", newline="") as target:
            writer = csv.writer(target, lineterminator="\n", quoting=csv.QUOTE_ALL)
            writer.writerow(["address", "name", "confidence", "matched_instructions", "library_sources"])
            writer.writerows(promoted)
        print(f"unique exact symbols: {len(promoted)}")
    print(f"candidate matches: {len(matches)}; exact: {sum(row[1] == 'exact-partition' for row in matches)}")


if __name__ == "__main__":
    main()
