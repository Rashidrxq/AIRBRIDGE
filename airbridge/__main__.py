"""Create and verify one digital WAV loopback from the command line."""

import argparse
from pathlib import Path
import sys

from .wav_io import decode_wav, encode_wav


def main() -> int:
    parser = argparse.ArgumentParser(description="Run an AIRBRIDGE digital WAV loopback.")
    parser.add_argument("text", help="message to encode (1 to 256 UTF-8 bytes)")
    parser.add_argument("wav", type=Path, help="new WAV file to create")
    args = parser.parse_args()
    try:
        original = args.text.encode("utf-8")
        encode_wav(original, args.wav)
        recovered = decode_wav(args.wav)
    except (ValueError, OSError) as exc:
        print(f"Loopback failed: {exc}", file=sys.stderr)
        return 1
    if recovered != original:
        print("Loopback failed: decoded bytes differ", file=sys.stderr)
        return 1
    print(f"PASS | {len(recovered)} bytes | recovered hex: {recovered.hex(' ')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
