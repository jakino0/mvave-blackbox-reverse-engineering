# Changelog

## Unreleased

- Initial public-safe repository structure.
- Added V20 memory map, USB Audio findings, `audio_dev` landmarks, LIST_A status,
  M-EFCS notes, OTA observations, and read-only inspection tools.
- Integrated findings about DSP handles and event lifecycle.
- Documented LIST_A event opcodes 1/2/4, the per-instance list-removal helper,
  and the corrected shared callback registrar at `0x42C2A`.
- Clarified the event opcodes and why raw list removal is not a safe audio stop.
- Corrected the task-creation decode: `LIST_A` belongs to `audio_encoder`;
  documented the distinct DAC client renderer and bounded V20 `DEV` reader.
- Recorded the response-buffer false-positive issue and the unresolved
  application-independent recovery requirement.
