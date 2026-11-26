import subprocess
import sys

import pytest


def run_cli(text, wav):
    return subprocess.run([sys.executable, "-m", "airbridge", text, str(wav)],
                          capture_output=True, text=True)


def test_cli_exact_recovery_and_existing_file(tmp_path):
    path = tmp_path / "hello.wav"
    result = run_cli("HELLO", path)
    assert result.returncode == 0, result.stderr
    assert "5 bytes | recovered hex: 48 45 4c 4c 4f" in result.stdout
    previous = path.read_bytes()
    second = run_cli("REPLACE", path)
    assert second.returncode != 0
    assert path.read_bytes() == previous


@pytest.mark.parametrize("text", ["", "A" * 257])
def test_cli_invalid_size_no_output(text, tmp_path):
    path = tmp_path / "invalid.wav"
    assert run_cli(text, path).returncode != 0
    assert not path.exists()
