# Firmware V20 address map

All offsets below refer to the V20 application image examined during this
research. They are not guaranteed to apply to another firmware release.

## Translation

```text
runtime = application_offset + 0x02000120
application_offset = runtime - 0x02000120
```

## Confirmed landmarks

| Item | Application offset | Runtime address | Confidence |
| --- | ---: | ---: | --- |
| Application base | `0x00000000` | `0x02000120` | Verified |
| LIST_A walker | `0x40530` | `0x02040650` | Verified code location |
| Per-instance CMD03 point | `0x405D4` | `0x020406F4` | Verified code location |
| Graph splice/relink routine | `0x4308A` | `0x020431AA` | Strong inference |
| `audio_dev` xref | `0x4332A` | `0x0204344A` | Verified |
| `audio_dev` string | `0x5BC1A` | `0x0205BD3A` | Verified |
| DAC descriptor | `0x5B7B8` | `0x0205B8D8` | Strong inference |
| I2S/output transport descriptor | `0x5B78C` | `0x0205B8AC` | Strong inference |
| MIC/input/shared descriptor | `0x5B7FC` | `0x0205B91C` | Strong inference |
| USB endpoint 0x02 descriptor | `0x5C3F0` | `0x0205C510` | Verified |
| USB endpoint 0x83 descriptor | `0x5C424` | `0x0205C544` | Verified |
| `BlackBox_020` string A | `0x5BD67` | `0x0205BE87` | Verified string only |
| `BlackBox_020` string B | `0x5C0A7` | `0x0205C1C7` | Verified string only |

## Runtime globals and objects

| Item | Runtime address | Confidence / note |
| --- | ---: | --- |
| LIST_A head | `0x01C0BBF4` | Strong inference: output-side per-instance list |
| LIST_B head | `0x01C0BBFC` | Strong inference: capture-side list |
| UAC owner | `0x01C13CFC` | Strong inference |
| UAC speaker subobject | `0x01C28E50` | Strong inference |
| UAC microphone subobject | `0x01C28F74` | Strong inference |
| Speaker-private control/state | `0x01C2702C` | Classified; not the stream-write handle |

The `0x01C...` globals are outside the application XIP mapping above; do not
convert them by subtracting the application base.

## Instruction encodings used in the analysis

JieLi PI32v2 uses variable-length 16/32/48-bit instructions. Two call forms
encountered in V20 are:

```text
CALL rel32: 80 FF imm32
target = address_after_instruction + signed(imm32)

short call: BF EA imm16
target = instruction_offset + 4 + signed(imm16) * 2
```

These formulas must be applied only after instruction boundaries are known.
Scanning for byte prefixes alone can produce false positives.
