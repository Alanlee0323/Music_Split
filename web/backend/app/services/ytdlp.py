import asyncio
import sys
from pathlib import Path


async def download_youtube(url: str, output_dir: Path) -> tuple[str, Path]:
    normalized_url = url.strip()
    lowered_url = normalized_url.lower()
    if "youtube.com" not in lowered_url and "youtu.be" not in lowered_url:
        raise ValueError("Only YouTube URLs are supported")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = output_dir / "%(title)s-%(id)s.%(ext)s"

    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "yt_dlp",
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--no-playlist",
        "--restrict-filenames",
        "--output",
        str(output_template),
        "--print",
        "title",
        "--print",
        "after_move:filepath",
        normalized_url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_message = stderr.decode().strip() or stdout.decode().strip() or "yt-dlp download failed"
        raise RuntimeError(error_message)

    lines = [line.strip() for line in stdout.decode().splitlines() if line.strip()]
    title = lines[-2] if len(lines) >= 2 else "YouTube Audio"

    if len(lines) >= 1:
        candidate_path = Path(lines[-1])
        if candidate_path.exists():
            return title, candidate_path

    mp3_files = sorted(output_dir.glob("*.mp3"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not mp3_files:
        raise RuntimeError("yt-dlp finished without producing an mp3 file")

    return title, mp3_files[0]
