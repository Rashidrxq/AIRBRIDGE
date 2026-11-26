"""Bounded WAV file adapter for the aligned modem."""

import os
from pathlib import Path
import wave

import numpy as np

from .modem import MAX_BYTES, SAMPLE_RATE, SAMPLES_PER_BYTE, demodulate, modulate

MAX_FRAMES = MAX_BYTES * SAMPLES_PER_BYTE
# Allow ordinary WAV headers and small ancillary chunks.
MAX_CONTAINER_BYTES = MAX_FRAMES * 2 + 65_536


def encode_wav(payload: bytes, path: Path) -> None:
    """Create a new PCM WAV, refusing to overwrite any existing path."""
    pcm = modulate(payload).astype("<i2", copy=False)
    stream = path.open("xb")
    try:
        with stream, wave.open(stream, "wb") as writer:
            writer.setparams((1, 2, SAMPLE_RATE, 0, "NONE", "not compressed"))
            writer.writeframes(pcm.tobytes())
    except OSError:
        path.unlink(missing_ok=True)
        raise


def decode_wav(path: Path) -> bytes:
    """Read a WAV and recover the payload without consulting the sender."""
    with path.open("rb") as stream:
        if os.fstat(stream.fileno()).st_size > MAX_CONTAINER_BYTES:
            raise ValueError("WAV file exceeds the experiment size limit")
        try:
            with wave.open(stream, "rb") as reader:
                audio_format = (
                    reader.getnchannels(), reader.getsampwidth(),
                    reader.getframerate(), reader.getcomptype(),
                )
                if audio_format != (1, 2, SAMPLE_RATE, "NONE"):
                    raise ValueError("expected mono 16-bit PCM at 48000 Hz")
                frames = reader.getnframes()
                if not 1 <= frames <= MAX_FRAMES or frames % SAMPLES_PER_BYTE:
                    raise ValueError("WAV frame count must describe 1 to 256 whole bytes")
                # One extra frame exposes a stray partial 16-bit sample.
                raw = reader.readframes(frames + 1)
        except (wave.Error, EOFError) as exc:
            raise ValueError("invalid or unsupported WAV container") from exc

    if len(raw) != frames * 2:
        raise ValueError("WAV data length disagrees with its declared frame count")
    return demodulate(np.frombuffer(raw, dtype="<i2"))
