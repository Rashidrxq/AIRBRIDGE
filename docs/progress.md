# Engineering session · 26 November 2026

## Starting evidence

Reviewed both available copies of AB-PROP-001 v0.1 (six pages, matching extracted text). GitHub reported that Rashidrxq/AIRBRIDGE had no commits or branches at the start of this session. The first repository commit records the M1 acceptance criteria. The proposal's later milestones remain pending.

## Milestone 1 test report

The validation run used Linux x86_64, CPython 3.12.14, NumPy 2.3.5 and pytest 8.4.2. The restricted development environment ran pytest from its upstream release tag. The standard installation instructions are in the README. Run the full suite from the project root with `python -m pytest -q`.

| Gate | Evidence |
| --- | --- |
| M1-01 | 100/100 deterministic binary payloads survived encoding, WAV write/close/reopen and decode with byte-for-byte equality. Each fixture has its own pytest seed ID. Length is 1 + (73 × seed mod 256). Content comes from Python 3.12 random.Random(seed).randbytes(length). |
| M1-02 | An independent zero-crossing count found the expected cycle counts for the eight symbols in 0x41. |
| M1-03 | A separate cosine-wave generator with a phase offset decoded to 0xA3 without calling the transmitter. |
| M1-04 | The WAV test checked the header, sample count and little-endian sample values. A separate HELLO run yielded 19,200 frames and recovered hex 48 45 4c 4c 4f. |
| M1-05 | Tests cover the size limits, all 256 byte values, Malayalam UTF-8 bytes, invalid PCM, unsupported formats, malformed WAV fixtures, and a silent symbol. A valid tone substitution demonstrates the missing integrity check. |
| M1-06 | CLI tests cover a fresh file, exact output, invalid input and preservation of an existing output. A simulated write failure removes the incomplete file. |

Full suite result at this checkpoint: **132 passed**. This is software-only evidence from generated samples. No real device measurements of range, noise tolerance, goodput, error rate or latency exist in this session.

## Reproduce or investigate

Start with the HELLO experiment in the README. If a seeded case fails, keep the seed ID and first traceback. For example, from the project root run `python -m pytest -q "tests/test_wav.py::test_seeded_wav_roundtrip[17]"` to reproduce seed 17. If the independent transmitter test fails, inspect tone generation and bit order first. If the receiver vector fails, inspect window length and FFT bins. If both pass and the WAV tests fail, inspect the header, byte order and sample count.

## Open items and handoff

The immediate user action is to reproduce HELLO on the target laptop. Use a fresh filename on repeat runs. Record OS, Python version and full error text if it fails. The second device and its capture format still need confirmation before the two-device milestone. The product payload limit, public release license and security requirements remain open. The next proposal gate is physical text transfer, with a target of at least 95 successes from 100 transfers of 32 bytes at 1 m in a quiet room, counting retries. Those are planned trials.
