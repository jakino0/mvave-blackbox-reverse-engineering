# Contributing

Contributions that improve reproducibility, correct an offset, document a safe
read-only observation, or add a synthetic test are welcome.

This repository is maintained on a best-effort basis and does not provide
individual technical support. A submission may remain unanswered or be closed
if it cannot be reproduced safely.

## Before opening a pull request

1. State the exact hardware and firmware version.
2. Separate observations from interpretations.
3. Include a minimal reproduction and expected output.
4. Run `python3 -m unittest discover -s tests -v`.
5. Run `python3 tools/check_repo.py` to catch accidental vendor artifacts and
   private identifiers.

## Do not upload

- firmware, decrypted application images, updater packages, or APKs;
- modified flashable images;
- full application disassembly, instruction-byte exports, vendor source, or
  toolchain dumps;
- device serial numbers, MAC addresses, credentials, or personal paths;
- private notes or logs that have not been reviewed and redacted.

Small byte sequences needed to identify a standard descriptor or explain an
instruction encoding are acceptable when they are necessary for commentary and
interoperability research.

Derived maps may contain addresses, names, counts, call relationships, and
string references. They must omit instruction bytes and enough ordered content
to reconstruct the original application image.

## Finding format

Use this compact structure in pull requests:

```text
Firmware: V20
Evidence: verified | strong inference | hypothesis
Artifact SHA-256: ...
Application offset: ...
Runtime address: ...
Observation: ...
Reproduction: ...
Safety impact: ...
```

Do not encourage a write or flash operation unless recovery and rollback have
been independently demonstrated and the change has been reviewed.
