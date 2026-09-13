# Selective local-monitoring research

This is one active research thread within the wider BlackBox reverse-
engineering project. It does not define the scope of the repository.

## Target invariant

| Path | Required state |
| --- | --- |
| BlackBox DSP to USB capture | Keep |
| BlackBox DSP to local DAC/output | Disable |
| USB playback to local DAC/output | Keep |

## Evidence matrix

| Finding | Level | Basis |
| --- | --- | --- |
| The unwanted contribution is normal local DSP output, not fixed analog dry | Verified experimentally | Android and Reaper reproduce it; preset/AMP/MASTER tests affect it |
| USB playback remains audible at MASTER=0 | Verified experimentally | Drum-loop test |
| MASTER=0 also removes usable input/capture to the host app | Verified experimentally | G-Core/NAM test |
| Application runtime base is `0x02000120` | Verified | Image/header analysis and address consistency |
| `audio_dev` at app `0x5BC1A`, unique code xref `0x4332A` | Verified | Direct byte/string and code-reference analysis |
| EP `0x02 OUT` is playback and EP `0x83 IN` is capture | Verified | UAC descriptors at app `0x5C3F0` and `0x5C424` |
| Both UAC streams are stereo, 24-bit, 44.1 kHz | Verified | Descriptor bytes and host ALSA observation |
| `0x425B6` is a shared per-instance feeder | Strong inference | Multiple call sites and argument flow |
| LIST_A is an output-side client list | Rejected | Task-creation decode associates its worker with `audio_encoder` |
| One LIST_A entry is the local-DSP contributor | Rejected as an assumption | Encoder-task association provides no local-output identity |
| `0x40530` dispatches per-object opcodes 1, 2, and 4 | Verified | Opcode comparisons and object field accesses in the instruction stream |
| Opcode 1 adds `object+0x24`; opcode 2 removes it | Verified | Calls to decoded list helpers `0x40122` and `0x40192` |
| `0x40192` is a safe monitor-off primitive | Rejected | It may only update bookkeeping after the real detach |
| `0x40530` / `0x41EC6` are task entries for `audio_encoder` / `audio_server` | Strong inference | Corrected call decode and task-name table |
| The shared call is a per-client event registrar | Rejected | Corrected task-creation decode |
| DAC renderer `0x4A698` walks a separate client list at `0x01C0DC3C` | Verified in binary | List traversal and per-client PCM callback call |
| Stock `DEV` reads reveal the DAC client list | Rejected | Defined bounded families do not cover its address |
| CMD05/06/07 already operate on LIST_A's `object+0x14` | Rejected | No static site combines those commands with that concrete field access |
| First LIST_A entry has stable meaning | Rejected | Insertion is push-front |
| Global DAC/I2S or UAC speaker mute solves the target | Rejected | Would also cut USB playback |
| MASTER is a selective monitor control | Rejected | It also cuts capture/input |

## Current model

`LIST_A` is a circular intrusive list at runtime address `0x01C0BBF4`
used by the `audio_encoder` task. Its connection to the desired local-output
path is not established.

```text
node = object + 0x24
object = node - 0x24
object + 0x14 = concrete device/audio handle
```

Routine `0x40530` walks the list. At `0x405D4` it conceptually performs:

```c
dev_ioctl(object->handle_14, 0x80044103, temporary_descriptor);
```

The descriptor is temporary stack state. An earlier theory that
`descriptor + 4` was a persistent node is rejected.

The same callback also handles lifecycle notifications:

```c
switch (event->opcode) {
case 1: list_add_after(event->object + 0x24, LIST_A); break;
case 2: list_remove(event->object + 0x24); break;
case 4: event->object->byte_00 = 6; break;
}
release_or_ack(event->payload_ref); /* call 0x675A8 */
```

This pseudocode records observed data flow; the semantic names of opcode 4 and
`0x675A8` remain provisional.

## Immediate next target

Identify the active clients of the separate DAC renderer. A controlled
comparison with and without USB playback could help distinguish contributors
if a safe observation route is found. Stock `DEV` reads cannot inspect those
client records. No selective control has been verified. Do not call `0x40192`
as an audio stop.

## Closed or paused leads

- fixed analog dry path;
- MASTER as a selective control;
- global DAC/I2S/UAC-speaker mute;
- global patches to CMD02, CMD03, graph splice, `0x425B6`, or the audio backend;
- blind skip of LIST_A entry 0;
- `0x01C0BC04` as a third list head or a single concrete-object pointer (the
  area is a seven-record, eight-byte-stride table; its connection to LIST_A is
  still unproven);
- DSP logical IDs 1/3/5 and the AMP callback family as local-vs-USB labels;
- `descriptor + 4` as persistent state;
- raw M-EFCS DEV-space access as arbitrary physical SRAM;
- TGlob mailbox without a demonstrated logical-to-physical mapping;
- MIDI-route telemetry;
- loopback `0xD0000001`, `rightOutputMode`, `usbRecType`, `usbRecVol`;
- package-version-only OTA bypass;
- FWSC `+0x14` translation-bug theory;
- corrupted `cfg` or `eq_cfg_hw.bin` CRC theory.
