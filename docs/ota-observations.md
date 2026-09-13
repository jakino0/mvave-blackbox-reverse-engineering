# OTA observations

OTA work is preserved as format research, not as the current route to a local
monitor control.

## Reconstructed facts

- Outer flash payload starts at FWSC file offset `0x414` and has size
  `0xA5000` in the examined V20 package.
- SFC decryption begins at flash address `0x4000` with the observed chip key
  `0x980F`, in 32-byte blocks.
- The JLFS `app` entry header is at decrypted flash offset `0x4020`; application
  data begins at `0x4120`.
- The integrity chain includes the application CRC16, JLFS entry-header CRC16,
  outer flash CRC, flattened UFW header, header CRC, and entry-list CRC.
- The desktop updater flattens 0x30-byte FWSC slots by removing each slot's
  48th byte before serving the logical OTA image.

## Version-only experiment

The updater derives the displayed package tag from bytes at `slot + 0x2F` for
20 slots. The decoded character rule observed was:

```text
decoded_char = raw(slot + 0x2F) - slot_index - 1
```

Changing the package display from 020 to 021 allowed the original updater to
pass its desktop prechecks. Device verification then requested data through
logical address `0xA47FF`, timed out after roughly 30 seconds, and the BlackBox
returned normally as V20.

The `0xA47FF` request corresponds to physical FWSC offset `0xA4813` after the
slot flattening. The relevant `cfg` JLFS entry and its `eq_cfg_hw.bin` child had
valid observed header/data CRCs. The failure is therefore not explained by the
previous `+0x14` translation or simple CRC-corruption theories.

## Current policy

Do not flash the version-only package or any diagnostic firmware prepared
during this investigation. Recovery and rollback have not been established,
and an official firmware update may supersede V20.

Analysis of the OTA stage suggests that the loader is moved into SRAM before
the main update operation. That is not a usable snapshot of the running audio
application: its SRAM area overlaps live application structures. More
importantly, there is still no demonstrated BlackBox recovery entry that works
when the normal application cannot boot. The recovery gate remains open; a
diagnostic firmware change is an offline idea only, not a validated device test.
