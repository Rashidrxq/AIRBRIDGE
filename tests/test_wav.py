import random
import struct
import wave

import pytest

from airbridge.wav_io import decode_wav, encode_wav


@pytest.mark.parametrize("seed", range(100))
def test_seeded_wav_roundtrip(seed, tmp_path):
    length = 1 + (73 * seed) % 256
    payload = random.Random(seed).randbytes(length)
    path = tmp_path / "signal.wav"
    encode_wav(payload, path)
    assert decode_wav(path) == payload


def test_wav_header_and_sample_endianness(tmp_path):
    path = tmp_path / "a.wav"
    encode_wav(b"A", path)
    with wave.open(str(path), "rb") as reader:
        assert reader.getparams()[:5] == (1, 2, 48000, 3840, "NONE")
        first_two = reader.readframes(2)
    assert struct.unpack("<hh", first_two) == (0, 1877)


@pytest.mark.parametrize("channels,width,rate", [(2, 2, 48000), (1, 1, 48000), (1, 2, 44100)])
def test_wrong_audio_format(tmp_path, channels, width, rate):
    path = tmp_path / "wrong.wav"
    with wave.open(str(path), "wb") as writer:
        writer.setparams((channels, width, rate, 0, "NONE", "not compressed"))
        writer.writeframes(b"\x00" * 3840 * channels * width)
    with pytest.raises(ValueError, match="mono 16-bit"):
        decode_wav(path)


@pytest.mark.parametrize("damage", ["bad_magic", "partial_header", "truncate", "odd_sample", "huge_frames", "excess_container"])
def test_malformed_wav(tmp_path, damage):
    path = tmp_path / "broken.wav"
    encode_wav(b"A", path)
    raw = bytearray(path.read_bytes())
    if damage == "bad_magic":
        raw[0:4] = b"JUNK"
    elif damage == "partial_header":
        raw = raw[:7]
    elif damage == "truncate":
        raw = raw[:-10]
    elif damage == "odd_sample":
        raw.extend(b"\x01\x00")  # data byte plus RIFF padding
        struct.pack_into("<I", raw, 4, len(raw) - 8)
        struct.pack_into("<I", raw, 40, 7681)
    elif damage == "huge_frames":
        struct.pack_into("<I", raw, 40, 0xfffffff0)
    elif damage == "excess_container":
        raw.extend(bytes(2_100_000))
    path.write_bytes(raw)
    with pytest.raises(ValueError):
        decode_wav(path)


def test_write_failure_leaves_no_incomplete_wav(monkeypatch, tmp_path):
    path = tmp_path / "failed.wav"

    def fail_write(writer, data):
        raise OSError("simulated disk write failure")

    monkeypatch.setattr(wave.Wave_write, "writeframes", fail_write)
    with pytest.raises(OSError, match="simulated"):
        encode_wav(b"A", path)
    assert not path.exists()
