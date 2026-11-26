# AIRBRIDGE

AIRBRIDGE aims to move short messages and small files between consenting nearby devices using ordinary speakers and microphones. This repository starts with the digital-loopback milestone from project proposal AB-PROP-001 v0.1, dated 26 November 2026.

## First experiment on Windows

Use PowerShell with Git and 64-bit Python 3.12 installed. The first dependency installation needs internet access. After installation, the experiment and tests run offline. If you already have this checkout, start in its root at the virtual-environment command.

```powershell
git clone --branch milestone-1-digital-loopback https://github.com/Rashidrxq/AIRBRIDGE.git
cd AIRBRIDGE
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m airbridge HELLO hello.wav
```

Expected output for this message is `PASS | 5 bytes | recovered hex: 48 45 4c 4c 4f`. The command closes and reopens the WAV before checking byte equality. Use a fresh filename for a repeat run. No speaker, microphone, or second device is needed for this experiment.

Run the acceptance suite from the same folder.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

On Linux and macOS with Python 3.12, create the environment with `python3.12 -m venv .venv` and replace the Windows executable path above with `.venv/bin/python`.

## Read the implementation

| File | Purpose |
| --- | --- |
| `airbridge/modem.py` | Convert bytes to tone samples and detect bits in aligned samples. |
| `airbridge/wav_io.py` | Store the samples, validate WAV parameters and reopen the recording for decoding. |
| `airbridge/__main__.py` | Accept a text message, run the experiment and report exact byte equality. |
| `tests/test_modem.py` | Check transmitter and receiver with independent references. |
| `tests/test_wav.py` | Run the 100 fixtures and exercise malformed inputs and write failures. |
| `tests/test_cli.py` | Exercise the real command in a separate Python process. |

Read the [architecture](docs/architecture.md), [experiment protocol](docs/protocol-m1.md), [engineering decision](docs/decisions/0001-aligned-bfsk.md) and [session report](docs/progress.md).

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
