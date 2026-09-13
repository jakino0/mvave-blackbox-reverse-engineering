# Methodology

## Reproducibility rules

1. Identify the exact input by SHA-256.
2. Record both application offsets and runtime addresses.
3. Validate variable-length instruction boundaries before resolving calls.
4. Cross-check static findings against descriptors, logs, or controlled tests.
5. Keep verified facts separate from hypotheses.
6. Prefer differential, read-only runtime observations.
7. Reject a candidate that cannot preserve both required USB paths.

## Safe experiment design

A useful local-monitor experiment changes one variable while checking all three
paths:

| Check | Success condition |
| --- | --- |
| BlackBox input captured by host | Still present |
| Host-generated playback at BlackBox output | Still present |
| BlackBox local DSP contribution | Absent |

Record the preset, MASTER, AMP volume, host application, USB state, and before /
after observations. A perceived reduction without independent path checks is
not sufficient.

## Offset terminology

- **File/FWSC offset**: position in the packaged updater file.
- **Flash offset**: address within the embedded flash payload.
- **Application offset**: position in the decrypted application image.
- **Runtime address**: CPU-visible address while the application is mapped.

These spaces are not interchangeable.
