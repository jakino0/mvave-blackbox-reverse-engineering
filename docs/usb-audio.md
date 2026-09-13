# USB Audio observations

## Descriptor evidence

The decrypted V20 application contains two Audio Streaming endpoint
descriptors:

| App offset | Endpoint | Direction | Interpreted role |
| ---: | ---: | --- | --- |
| `0x5C3F0` | `0x02` | OUT, host to device | USB playback |
| `0x5C424` | `0x83` | IN, device to host | USB capture |

The adjacent format descriptors encode:

- 2 channels;
- 3-byte subframe;
- 24-bit resolution;
- one discrete sample rate, `44 AC 00` = 44,100 Hz.

Relevant descriptor sequences:

```text
09 05 02 09 20 01 01 00 00
09 05 83 05 20 01 01 00 00
```

Host observations identify the composite interface as `S24_3LE` at 44.1 kHz,
consistent with the descriptors.

## Routing consequence

Endpoint direction must be read from the USB host's point of view:

- OUT `0x02`: samples leave the host and arrive at the BlackBox;
- IN `0x83`: samples leave the BlackBox and arrive at the host.

A global speaker/DAC mute is therefore not a selective solution: it would also
silence the return received on endpoint `0x02`.
