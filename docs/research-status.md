# Research status

This page summarizes findings reviewed for the public V20 documentation.

## Coverage

| Area | Established baseline | Open work |
| --- | --- | --- |
| Firmware V20 | Image landmarks and application/runtime translation | Broader function classification and future-version comparison |
| Runtime architecture | Device-object, callback, handle, and intrusive-list structures | Semantic identity of active objects and producers |
| USB Audio | Playback/capture endpoint direction and 24-bit/44.1 kHz descriptors | Internal producer/consumer mapping and runtime state |
| BLE/M-EFCS | Transport framing, selected commands, query/write surfaces | Complete command semantics and safe runtime capabilities |
| Audio/DSP | `audio_dev` anchors, output-side LIST_A lifecycle, capture-side callback family | Full graph reconstruction and object roles |
| OTA/updater | Package observations and desktop verification behavior | Recovery model, rollback guarantees, and safe update boundaries |
| Read-only tooling | Firmware landmarks, hashes, descriptors, and address translations | Additional validated signatures and reports |

## Active research threads

| Thread | Status | Detail |
| --- | --- | --- |
| Runtime object identity | Active | Label handles and objects without changing flash |
| Event producer tracing | Active | Trace producers feeding the known callback families |
| M-EFCS command map | Active | Separate verified device behavior from APK-level naming |
| Selective local monitoring | Open; no safe control found | [Dedicated research note](research/local-monitoring.md) |
| OTA/recovery | Paused for safety | No demonstrated recovery-safe write path |

## Evidence policy

The project distinguishes verified results, strong inferences, hypotheses, and
rejected interpretations. A new finding is added only when its evidence and
reproduction basis can be recorded and reviewed.

## Safety boundary

The public repository contains no vendor firmware, decrypted images, APKs,
private logs, device identifiers, or modified firmware. Current tools are
read-only. OTA and runtime-control observations are not evidence of a safe
recovery or flashing path.
