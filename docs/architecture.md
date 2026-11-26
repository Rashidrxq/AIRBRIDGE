# Digital loopback architecture

A digital loopback asks whether a receiver can reconstruct the exact input when software provides a perfect channel. Storing the generated samples in a WAV file makes the signal inspectable and gives the receiver an input independent of the transmitter's in-memory state.

## Follow the letter A

1. The CLI encodes the text as UTF-8. The letter A becomes one byte, 0x41. In binary that byte is 01000001.
2. The modulator reads the eight bits from left to right. For a zero it emits a 1200 Hz tone. For a one it emits a 2400 Hz tone. This is binary frequency-shift keying, or BFSK.
3. A sample is a number describing a waveform at one instant. Pulse-code modulation (PCM) stores those numbers. The encoder generates 48,000 samples for each second of waveform. One bit lasts 1/100 of a second, so it occupies 480 samples. One byte occupies 3840.
4. The WAV writer stores the samples and their format. The WAV reader reopens the file and checks the channel count, sample width, sample rate, and input bounds.
5. The receiver divides the samples into 480-sample windows. A fast Fourier transform (FFT) measures which frequencies are present in each window. Here 1200 Hz completes 12 cycles per window and 2400 Hz completes 24. The decoder compares the magnitudes in FFT bins 12 and 24 and picks the stronger tone. Comparing magnitude permits the reference tone to start at a different phase. Timing still has to be aligned.
6. The receiver packs the recovered bits into bytes. The CLI alone knows the original bytes and compares them with the result.

## Component boundaries

| Interface | Input | Output |
| --- | --- | --- |
| modulate(payload) | Python bytes | One-dimensional signed 16-bit NumPy array |
| demodulate(samples) | Aligned signed 16-bit array | Recovered bytes |
| encode_wav(payload, path) | Bytes and a new local path | Mono PCM WAV on disk |
| decode_wav(path) | Local WAV path alone | Recovered bytes |

The modem performs no file operations. The file adapter performs no playback or recording. The CLI handles text encoding, user-facing errors and the final comparison. NumPy supplies array operations and the FFT, Python's wave module handles the container, and pytest drives verification. Components for real devices belong to the next milestone.
