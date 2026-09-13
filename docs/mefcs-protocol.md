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

## Important boundary

A successful read in logical memory type 4 (`DEV`) is not evidence that the
address is a direct physical SRAM address. No clean logical-DEV-to-physical-RAM
mapping has been established for BlackBox V20. Treating `0x20000000` as an
arbitrary RAM mailbox is therefore rejected.

The available AOT caller extracts mix product-specific code (Tank, SP100, and
generic UI). A special-address query observed in one product must not be assumed
valid for the BlackBox without a BlackBox-specific call path or device response.

## Research preference

Use existing, read-only queries to expose runtime identity if possible. Any
future protocol documentation should include a captured request/response pair,
transport, firmware version, and checksum validation, with device identifiers
redacted.
