# RFC 0001 · Aligned PCM experiment

Status is implemented for digital loopback. This is the waveform profile used by the tests. An over-the-air frame specification is still open.

| Field | Value |
| --- | --- |
| Payload | 1–256 arbitrary bytes in this experiment. The CLI converts text using UTF-8. |
| Byte order on the channel | Transmit bytes in input order. In each byte transmit bit 7 first and bit 0 last. |
| Zero / one | 1200 Hz / 2400 Hz. One bit per symbol. |
| Sample format | One channel, 48,000 samples/s, signed 16-bit little-endian PCM in RIFF/WAVE. |
| Symbol duration | 10 ms, exactly 480 samples. |
| Tone construction | For n from 0 to 479, round 12000 × sin(2π × frequency × n / 48000) to the nearest integer. Reset n for every symbol. |
| Timing reference | The first sample begins the first bit. There are no gaps, leading silence or trailing samples. |
| Payload length | The WAV data frame count divided by 3840. Require an integral result in range. |
| Decoder decision | Choose the larger FFT magnitude in bins 12 and 24. Reject indistinguishable magnitudes using NumPy isclose defaults (relative tolerance 1e-5 and absolute tolerance 1e-8). |

Example vector. Input byte 0x41 produces the bit string 01000001. Its tone frequencies in Hz are 1200, 2400, 1200, 1200, 1200, 1200, 1200, 2400, for a waveform duration of 80 ms. This duration follows from the format and excludes software overhead.

## Input and integrity boundaries

The reader checks container size before parsing and checks the declared shape before buffering. Sample data is bounded to 256 × 3840 × 2 bytes. The total file-size limit allows another 65,536 bytes for headers and metadata. A clearly silent or tied symbol is rejected. A stronger tone alone does not establish that a payload is genuine or intact.

A valid tone substituted for another can decode as the wrong bit. Losing a whole byte and adjusting the WAV length can yield a different valid payload. The loopback compares against a known original. A future physical receiver will require frame synchronization and a separate integrity check.

The lab writes only to a user-specified new path. It never takes a destination filename from received bytes. Before device trials, specify preamble, frame length and version fields. CRC, forward error correction, acknowledgments, retry rules and file hashes still require a versioned frame/reliability specification.
