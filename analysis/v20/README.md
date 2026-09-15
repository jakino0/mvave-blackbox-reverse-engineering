# V20 generated firmware map

This directory contains a reproducible structural map of the V20 application
image. It deliberately excludes the application image, instruction bytes, and
the full disassembly.

## Coverage

| Measurement | Result |
| --- | ---: |
| Application size | 655,712 bytes |
| Runtime range | `0x02000120`–`0x020A027F` |
| Recognized instructions | 222,490 |
| Bytes covered by recognized instructions | 617,960 (94.2426%) |
| Unrecognized bytes | 37,752 (5.7574%) |
| Direct call sites | 12,152 |
| Unique direct-call targets | 2,163 |
| Function entries including reviewed seeds | 2,167 |
| Printable ASCII candidates | 6,790 |
| Raw in-image pointer targets | 1,506 |

The decoder was run linearly across the entire image. Coverage therefore means
that the PI32v2 decoder recognized an instruction at those byte ranges; it does
not prove that every recognized range executes. Conversely, gaps may be data,
alignment, instruction forms unsupported by this objdump build, or genuine
decoding failures.

## Generated data

| Path | Content |
| --- | --- |
| `generated/manifest.json` | Input identity, decoder, counts, shards, limitations |
| `generated/functions/` | Mechanical function partitions, call relationships, tags, string references |
| `generated/strings/` | Printable ASCII candidates and addresses |
| `generated/gaps/` | Byte ranges not recognized by the linear decoder |
| `generated/pointers/` | Aligned and halfword-aligned in-image pointer candidates |
| `generated/string_tables/` | Nearby runs of pointers to printable strings |
| `generated/landmarks.json` | Manually reviewed functions and data locations |
| `generated/library-candidates.csv` | Conservative standard-library signature candidates |
| `generated/library-symbols.csv` | Exact, uniquely named toolchain-library matches |

An entry named `FUN_...` is an address boundary, not a semantic identification.
Its end is the next known direct-call target, so `partition_size` must not be
treated as a proven compiler function size. Indirectly reached callbacks remain
one of the largest sources of missing entry points.

## Reproduce locally

The official JieLi PI32v2 compiler and objdump are required. Use a V20
application image that you obtained lawfully:

```bash
python3 tools/disassemble_pi32v2.py \
  path/to/application.bin path/to/jieli-toolchain work/v20.disassembly.txt

python3 tools/build_firmware_map.py \
  path/to/application.bin work/v20.disassembly.txt \
  --symbols analysis/v20/known-symbols.json \
  --output analysis/v20/generated
```

Optional standard-library matching:

```bash
python3 tools/disassemble_toolchain_libs.py \
  path/to/jieli-toolchain work/toolchain-libraries

python3 tools/match_toolchain_libs.py \
  work/v20.disassembly.txt analysis/v20/generated/functions \
  work/toolchain-libraries analysis/v20/generated/library-candidates.csv \
  --symbols-output analysis/v20/generated/library-symbols.csv
```

Keep `work/v20.disassembly.txt` and all toolchain-library listings local. They
contain third-party instruction bytes or code and are excluded from this
repository.
