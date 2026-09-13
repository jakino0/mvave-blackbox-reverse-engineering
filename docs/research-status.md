# Research status

This page summarizes findings reviewed for the public V20 documentation.

## Coverage

| Area | Established baseline | Open work |
| --- | --- | --- |
| Firmware V20 | Image landmarks and application/runtime translation | Broader function classification and future-version comparison |
| Runtime architecture | Task identities, device objects, bounded DEV reads, and intrusive-list structures | Semantic identity of active DAC clients |
| USB Audio | Playback/capture endpoint direction and 24-bit/44.1 kHz descriptors | Internal producer/consumer mapping and runtime state |
| BLE/M-EFCS | Transport framing, bounded DEV reader families, controlled device reads | Complete command semantics and safe runtime capabilities |
| Audio/DSP | `audio_dev` anchors, encoder-task LIST_A lifecycle, separate DAC client renderer | Full graph reconstruction and client identities |
| OTA/updater | Package observations and desktop verification behavior | Recovery model, rollback guarantees, and safe update boundaries |
| Read-only tooling | Firmware landmarks, hashes, descriptors, and address translations | Additional validated signatures and reports |

## Active research threads

| Thread | Status | Detail |
| --- | --- | --- |
| Runtime object identity | Active | Label DAC clients without changing flash |
| Task and event semantics | Active | Distinguish `audio_encoder` and `audio_server` work from DAC rendering |
| M-EFCS command map | Active | Separate verified device behavior from APK-level naming |
| Selective local monitoring | Open; no safe control found | [Dedicated research note](research/local-monitoring.md) |
| OTA/recovery | Paused for safety | No demonstrated recovery entry independent of a bootable application |

## Evidence policy

The project distinguishes verified results, strong inferences, hypotheses, and
rejected interpretations. A new finding is added only when its evidence and
reproduction basis can be recorded and reviewed.

## Safety boundary

The public repository contains no vendor firmware, decrypted images, APKs,
private logs, device identifiers, or modified firmware. Current tools are
read-only. OTA and runtime-control observations are not evidence of a safe
recovery or flashing path.
