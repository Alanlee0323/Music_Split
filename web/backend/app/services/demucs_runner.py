import subprocess
import sys
from pathlib import Path


def run_separation(audio_path: Path, output_dir: Path, model: str, stems: str) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable,
        "-m",
        "demucs",
        "-n",
        model,
        "-o",
        str(output_dir),
    ]
    if stems != "all":
        command.append(f"--two-stems={stems}")
    command.append(str(audio_path))

    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        error_message = completed.stderr.strip() or completed.stdout.strip() or "Demucs separation failed"
        raise RuntimeError(error_message)

    separated_track_dir = output_dir / model / audio_path.stem
    if not separated_track_dir.exists():
        raise RuntimeError(f"Expected Demucs output directory was not created: {separated_track_dir}")

    output_files = sorted(file_path.name for file_path in separated_track_dir.glob("*.wav"))
    if not output_files:
        raise RuntimeError("Demucs finished without producing any wav files")

    return output_files
