# AIRBRIDGE

AIRBRIDGE aims to move short messages and small files between consenting nearby devices using ordinary speakers and microphones. This repository starts with the digital-loopback milestone from project proposal AB-PROP-001 v0.1, dated 26 November 2026.

## Milestone 1 acceptance criteria

Write an encoder that maps bytes to generated PCM samples, save those samples as a WAV file, and give an independent decoder only the WAV file. The first sample is the beginning of the first bit. An exact round trip means that every recovered byte equals the corresponding input byte.

| ID | Check | Pass condition |
| --- | --- | --- |
| M1-01 | Digital loopback | All 100 deterministic binary fixtures (seeds 0 through 99) survive WAV write, close, reopen and decode with exact byte equality. |
| M1-02 | Transmitter conformance | An independent check of the emitted symbols for byte 0x41 finds 1200 Hz for zero and 2400 Hz for one, in most-significant-bit-first order. |
| M1-03 | Receiver conformance | An independently generated PCM vector decodes to a known byte, including a nonzero starting phase. |
| M1-04 | WAV and symbol timing | WAV is mono, signed 16-bit little-endian PCM at 48,000 samples/s. Each bit occupies 480 samples and each byte 3840 samples. |
| M1-05 | Input boundaries | Cover the 1-byte and 256-byte experiment limits, binary extremes and UTF-8 text. Reject empty, oversized, misaligned, truncated, silent-symbol and unsupported-format fixtures. |
| M1-06 | Usable experiment | One documented command writes a fresh WAV and reports equality. A failed operation exits with an error. An existing output file stays intact. |

The 256-byte limit is an experiment bound. Product payload size and the open-source license are pending decisions. Record software test results and hardware measurements separately. The next milestone introduces synchronization and two-device acoustic tests after the digital gate.
