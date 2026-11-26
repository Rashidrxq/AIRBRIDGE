# ADR 0001 · Start with aligned, audible BFSK in a WAV file

**Status** Accepted for milestone 1 on 26 November 2026.

**Context** Proposal AB-PROP-001 v0.1 calls for deterministic PCM loopback before device trials. A live capture combines codec errors with unknown start time, device processing and room acoustics.

**Decision** Adopt the proposal's 48 kHz, 1200/2400 Hz and 100-symbol/s starting values. Use a real 16-bit WAV as the handoff. The tones complete 12 and 24 cycles in one symbol. This allows detection by comparing two FFT bins. Use only NumPy and the Python standard library at runtime. Pin pytest for repeatable developer setup. Use a 256-byte lab maximum to bound work and memory. Keep the modem's input and output binary so future callers can choose their own payload format.

**Consequences** Failures in this milestone can be reproduced from files and seeds. The result assumes an exact sample clock and known symbol boundaries. Error detection, clock recovery, hardware audio and accommodation of lower-quality device recordings need independent gates. Future engineering choices, including SciPy filtering and SoundDevice streaming, should follow measured needs.
