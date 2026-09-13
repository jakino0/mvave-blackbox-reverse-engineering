# M-EFCS protocol notes

The Android M-EFCS application is a Flutter/AOT application. Analysis located
the following logical client primitives:

- `DeviceConnection::readData()`
- `DeviceConnection::writeData()`
- `CommandQueue::sendQuery()`
- query packet construction and response parsing

The query path expects a response command identifier `0x22`. Memory-style read
traffic uses operation `0x23` and serializes a memory type, little-endian
address, and requested length.

## V20 `DEV` read boundaries

The device-side `DEV` reader resolves the high address nibble as a family and
checks the offset and requested length against that family's bounds. Binary
analysis and controlled reads agree on these specific mappings:

| Family | Backing or behavior | Limit | Evidence |
| --- | --- | --- | --- |
| `0` | Preset/configuration bank at runtime `0x01C1AC70` | `0x1CCA` bytes | Binary bounds check; end-of-range device reads |
| `1` | Current patch at `0x01C18E6C` | `0x5C` bytes | Binary and live parameter changes |
| `2` | Four-byte state at `0x01C13E30` | 4 bytes | Binary and device read |
| `D` | Computer Loopback state | Exactly one byte | Binary and OFF/ON/OFF device comparison |

Families `3` through `C` have no implemented data return in this reader.
The ten final bytes of family `0` form a `PATCHEND` trailer; a one-byte read
at offset `0x1CCA` is outside the bounded region. This is a defined, narrow
mapping, **not** arbitrary SRAM access. In particular, it does not expose the
DAC client list.

The current patch data changes with some AMP/CAB controls; the physical MASTER
control did not change that 92-byte snapshot. That observation does not make
any patch field a selective local-monitor control.

**Response validity:** the transport can return a formally valid read response
even when a backend leaves the requested payload untouched. Stale request
checksums and previous buffer contents caused false positives in short `USR`
reads. A response alone does not prove a successful read: require an expected
length and coherent, independently checked data. A previously observed larger
`USR` transfer contained preset names, but it is not a general RAM reader.

The available AOT caller extracts mix product-specific code (Tank, SP100, and
generic UI). A special-address query observed in one product must not be assumed
valid for the BlackBox without a BlackBox-specific call path or device response.

## Research preference

Use bounded, previously observed read-only queries to expose runtime identity
if possible. Any
future protocol documentation should include a captured request/response pair,
transport, firmware version, and checksum validation, with device identifiers
redacted.
