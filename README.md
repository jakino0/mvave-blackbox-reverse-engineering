# M-VAVE ANN BlackBox reverse engineering

Independent, community-oriented documentation and read-only tooling for the
M-VAVE ANN BlackBox. This project investigates the device firmware, runtime
layout, USB Audio implementation, BLE/M-EFCS protocol, OTA behavior, and
audio/DSP architecture using reproducible evidence.

The repository is not limited to one modification or firmware version. It is
intended to grow as new firmware, protocol findings, hardware observations,
and independently reproduced results become available.

> [!WARNING]
> This project does **not** ship M-VAVE firmware, decrypted images, APKs, or
> modified firmware. The tools inspect files you already obtained lawfully.
> No firmware image produced during the investigation is recommended for
> flashing.

> [!NOTE]
> This is a research archive maintained on a best-effort basis. Individual
> technical support, device troubleshooting, and response-time guarantees are
> not provided. Findings may be corrected as the analysis progresses.

## Start here

- [Research status](docs/research-status.md): current coverage, confidence, and
  open questions across the project.
- [V20 address map](docs/address-map-v20.md): image landmarks and application to
  runtime address translation.
- [`audio_dev` and runtime lists](docs/audio-dev-and-lists.md): device objects,
  handles, callbacks, and intrusive-list lifecycle.
- [USB Audio](docs/usb-audio.md): playback/capture endpoints and formats.
- [BLE/M-EFCS protocol](docs/mefcs-protocol.md): observed framing, commands,
  transports, and access limits.
- [OTA observations](docs/ota-observations.md): updater behavior and safety
  boundaries.
- [Methodology](docs/methodology.md): evidence levels and reproducible workflow.
- [Selective local-monitoring research](docs/research/local-monitoring.md): one
  active audio-routing investigation and its rejected approaches.

## Current technical baseline

- V20 application offsets map to runtime addresses with
  `runtime = app_offset + 0x02000120`.
- The `audio_dev` string is at application offset `0x5BC1A` (runtime
  `0x0205BD3A`) with one identified code reference at `0x4332A`.
- USB Audio endpoint `0x02 OUT` carries host-to-device playback and endpoint
  `0x83 IN` carries device-to-host capture. Both descriptors specify stereo,
  24-bit, 44.1 kHz audio.
- An output-side runtime object family uses intrusive `LIST_A`, per-object
  handles, and event opcodes for add, remove, and state change.
- Callbacks at application offsets `0x40530` and `0x41EC6` are registered
  through the shared primitive at `0x42C2A`.
- BLE and USB expose related M-EFCS messaging through different transports;
  observed commands do not yet provide a complete control map.
- OTA/updater behavior has been partially characterized, but no recovery-safe
  modification or flashing procedure has been established.

These statements summarize the present evidence, not a finished semantic map
of the firmware. The linked documents separate verified results from strong
inferences, hypotheses, and rejected interpretations.

## Research areas

| Area | Current coverage | Status |
| --- | --- | --- |
| Firmware V20 | Image landmarks, offsets, runtime translation | Documented; expanding |
| Runtime architecture | Objects, handles, callbacks, lists, event lifecycle | Partially reconstructed |
| USB Audio | Endpoint direction, descriptors, formats, host observations | Core facts verified |
| BLE/M-EFCS | Framing, transport behavior, selected commands and memory spaces | Partial protocol map |
| OTA/updater | Package and desktop-updater observations | Experimental; not recovery-safe |
| Audio/DSP routing | Output/capture structures and lifecycle candidates | Active research |
| Selective local monitoring | Separate DSP-local contribution while retaining both USB paths | Open question |
| Tooling | Read-only inspection and synthetic regression tests | Available |

Selective local monitoring is one application of the broader architecture
research. Its detailed target, evidence matrix, and current next steps live in
the dedicated [research note](docs/research/local-monitoring.md), rather than
defining the scope of the repository.

## Repository layout

| Path | Purpose |
| --- | --- |
| `docs/` | Architecture, protocol notes, research threads, and status |
| `tools/` | Read-only firmware inspection utilities |
| `tests/` | Synthetic tests containing no vendor data |

## Reproduce

Run from the repository root:

```bash
python3 tools/blackbox_inspect.py path/to/BlackBox_app_decrypted.bin
python3 tools/blackbox_inspect.py --json path/to/BlackBox_app_decrypted.bin
python3 -m unittest discover -s tests -v
python3 tools/check_repo.py
```

The inspector never writes to the input image. It reports hashes, known ASCII
landmarks, USB Audio endpoint descriptors, and application/runtime address
translations.

## Evidence policy

Technical statements use four confidence levels:

- **Verified**: reproduced from bytes, logs, or controlled device tests.
- **Strong inference**: multiple observations agree, but identity or semantics
  remain incomplete.
- **Hypothesis**: a useful lead requiring a discriminating test.
- **Rejected**: contradicted, unsafe, or too broad for the intended operation.

No claim is made that this project is affiliated with or endorsed by M-VAVE,
JieLi, Sinco Audio, or their partners. Product names are used only for
identification and interoperability research.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Do not submit copyrighted firmware,
APKs, device serial numbers, private logs, credentials, or instructions to
flash unreviewed images.

## License

Original documentation and tools in this repository are released under the
MIT License. This does not grant rights to third-party firmware, applications,
trademarks, or other vendor material.
