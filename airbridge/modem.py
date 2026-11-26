"""Aligned binary frequency-shift keying (BFSK) for the M1 WAV experiment."""

import numpy as np

SAMPLE_RATE = 48_000
SYMBOL_RATE = 100
SAMPLES_PER_BIT = SAMPLE_RATE // SYMBOL_RATE
SAMPLES_PER_BYTE = 8 * SAMPLES_PER_BIT
MAX_BYTES = 256
ZERO_HZ = 1_200
ONE_HZ = 2_400
AMPLITUDE = 12_000


def modulate(payload: bytes) -> np.ndarray:
    """Turn 1..256 bytes into mono signed 16-bit PCM."""
    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    if not 1 <= len(payload) <= MAX_BYTES:
        raise ValueError(f"payload must contain 1 to {MAX_BYTES} bytes")

    time = np.arange(SAMPLES_PER_BIT) / SAMPLE_RATE
    frequencies = np.array([ZERO_HZ, ONE_HZ])[:, None]
    tones = np.rint(AMPLITUDE * np.sin(2 * np.pi * frequencies * time))
    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8), bitorder="big")
    return tones.astype(np.int16)[bits].reshape(-1)


def demodulate(samples: np.ndarray) -> bytes:
    """Decode whole bytes beginning at sample zero, with an exact symbol clock."""
    if not isinstance(samples, np.ndarray) or samples.ndim != 1:
        raise ValueError("expected a one-dimensional mono PCM array")
    if samples.dtype.kind != "i" or samples.dtype.itemsize != 2:
        raise ValueError("expected signed 16-bit PCM")
    if not 1 <= samples.size <= MAX_BYTES * SAMPLES_PER_BYTE:
        raise ValueError("PCM length is outside the experiment bounds")
    if samples.size % SAMPLES_PER_BYTE:
        raise ValueError("PCM length must contain only whole bytes")

    symbols = samples.reshape(-1, SAMPLES_PER_BIT)
    # Each FFT bin spans 100 Hz in a 480-sample window.
    spectrum = np.fft.rfft(symbols, axis=1)
    zero_magnitude = np.abs(spectrum[:, ZERO_HZ // SYMBOL_RATE])
    one_magnitude = np.abs(spectrum[:, ONE_HZ // SYMBOL_RATE])
    if np.any(np.isclose(zero_magnitude, one_magnitude)):
        raise ValueError("ambiguous symbol (silence or equal tone magnitudes)")
    bits = one_magnitude > zero_magnitude
    return np.packbits(bits, bitorder="big").tobytes()
