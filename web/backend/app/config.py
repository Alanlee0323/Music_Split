import os
from pathlib import Path

DATA_DIR = Path(os.getenv("DATA_DIR", "/app/data"))
UPLOAD_DIR = DATA_DIR / "uploads"
SEPARATED_DIR = DATA_DIR / "separated"

SUPPORTED_AUDIO_FORMATS = [".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac"]
AVAILABLE_MODELS = {
    "htdemucs_ft": "Hybrid Transformer Demucs FT (推薦)",
    "htdemucs": "Hybrid Transformer Demucs",
    "htdemucs_6s": "Hybrid Transformer Demucs 6s",
    "hdemucs_mmi": "Hybrid Demucs MMI",
}
AVAILABLE_STEMS = ["vocals", "drums", "bass", "other", "all"]

for directory in (DATA_DIR, UPLOAD_DIR, SEPARATED_DIR):
    directory.mkdir(parents=True, exist_ok=True)
