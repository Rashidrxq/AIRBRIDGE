import math

import numpy as np
import pytest

from airbridge.modem import demodulate, modulate


def test_transmitter_byte_a_and_tone_order():
    # Independent oracle: count rising zero crossings, without the decoder or an FFT.
    pcm = modulate(b"A")
    assert pcm.dtype == np.int16
    assert pcm.shape == (3840,)
    assert np.max(np.abs(pcm.astype(np.int32))) == 12_000
    cycles = []
    for symbol in pcm.reshape(8, 480):
        cycles.append(np.count_nonzero((symbol[:-1] <= 0) & (symbol[1:] > 0)))
    assert cycles == [12, 24, 12, 12, 12, 12, 12, 24]


def test_receiver_reads_an_independent_phase_shifted_vector():
    # 10100011 = 0xa3. The fixture shares no encoder code or parameters.
    frequencies = [2400, 1200, 2400, 1200, 1200, 1200, 2400, 2400]
    pcm = [round(8000 * math.cos(2 * math.pi * hz * n / 48000 + 0.37))
           for hz in frequencies for n in range(480)]
    assert demodulate(np.array(pcm, dtype=np.int16)) == bytes([0xa3])


@pytest.mark.parametrize("payload", [b"\x00", b"\xff", bytes(range(256)), "നമസ്കാരം".encode("utf-8")])
def test_byte_extremes_and_text(payload):
    assert demodulate(modulate(payload)) == payload


@pytest.mark.parametrize("payload", [b"", bytes(257)])
def test_payload_size_rejected(payload):
    with pytest.raises(ValueError):
        modulate(payload)


def test_requires_an_explicit_byte_payload():
    with pytest.raises(TypeError):
        modulate("A")


@pytest.mark.parametrize("pcm", [
    np.zeros(0, dtype=np.int16),
    np.zeros(3840, dtype=np.float32),
    np.zeros(3840, dtype=np.uint16),
    np.zeros((3840, 1), dtype=np.int16),
    np.zeros(3839, dtype=np.int16),
    np.zeros(7 * 480, dtype=np.int16),
    np.zeros(257 * 3840, dtype=np.int16),
])
def test_invalid_pcm_rejected(pcm):
    with pytest.raises(ValueError):
        demodulate(pcm)


def test_single_silent_symbol_rejected():
    pcm = modulate(b"A")
    pcm[480:960] = 0
    with pytest.raises(ValueError, match="ambiguous"):
        demodulate(pcm)


def test_valid_tone_substitution_documents_integrity_limit():
    # A different valid tone is a different bit. M1 has no checksum.
    pcm = modulate(b"A")
    pcm[:480] = modulate(b"\xff")[:480]
    assert demodulate(pcm) == b"\xc1"
