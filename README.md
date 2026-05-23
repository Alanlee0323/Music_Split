# Demucs Toolkit

Production-ready toolkit for music source separation using **Demucs**, with:

- Command-line workflows (Windows / Bash)
- Web UI (Vue + FastAPI)
- Docker deployment for desktop GPU and Jetson Xavier NX

---

## What this project provides

This repository packages Demucs into a practical workflow for creators and developers:

1. **Local script workflow** for quick separation jobs
2. **Web application** for upload, task tracking, preview, and download
3. **Containerized deployment** for reproducible operation on different devices

Supported separation targets:

- `vocals`
- `drums`
- `bass`
- `all` (full stem separation)

Supported models:

- `htdemucs_ft` (recommended quality)
- `htdemucs`
- `htdemucs_6s`
- `hdemucs_mmi`

---

## Repository layout

```text
demucs-main/
├── split_drums.py
├── batch_process_songs.bat
├── batch_process_songs.sh
├── original_songs/                    # local input audio (gitignored)
├── separated/                         # local outputs (gitignored)
└── web/
    ├── backend/                       # FastAPI service
    ├── frontend/                      # Vue 3 + Vite UI
    ├── docker-compose.yml             # desktop deployment
    ├── docker-compose.jetson.yml      # Jetson deployment
    └── backend/Dockerfile.jetson      # Jetson backend image
```

---

## Quick start

### A) CLI separation

Extract vocals from a local file:

```bash
python -m demucs -n htdemucs_ft --two-stems=vocals "original_songs/your_song.mp3"
```

Output path:

```text
separated/htdemucs_ft/<track_name>/
├── vocals.wav
└── no_vocals.wav
```

---

### B) Web UI (desktop GPU)

```bash
cd web
docker compose up --build -d
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

---

### C) Web UI (Jetson Xavier NX, L4T r35.6.x / JetPack 5.x)

```bash
cd web
docker compose -f docker-compose.jetson.yml up --build -d
```

If your Jetson uses a different valid L4T PyTorch image tag:

```bash
export JETSON_PYTORCH_IMAGE=<your-valid-tag>
docker compose -f docker-compose.jetson.yml up --build -d
```

---

## API overview

- `POST /api/upload/file` — upload audio file
- `POST /api/upload/youtube` — download from YouTube URL
- `POST /api/jobs/` — create separation job
- `GET /api/jobs` — list jobs
- `GET /api/jobs/{id}` — get job status
- `GET /api/jobs/{id}/download/{filename}` — download output stem
- `DELETE /api/jobs/{id}` — delete job and related files

---

## Security and publication notes

This repository is configured to avoid publishing local/private runtime data.  
The following paths are gitignored:

- `original_songs/`
- `separated/`
- `downloads/`
- `web/data/uploads/`
- `web/data/separated/`
- `web/frontend/node_modules/`
- `web/frontend/dist/`

Do not force-add ignored files (`git add -f`) before publishing.

---

## Attribution (model origin)

This project uses Demucs as the underlying source separation model.  
All core model credit belongs to the original Demucs authors and maintainers.

- Original repository (Meta / Facebook Research):  
  https://github.com/facebookresearch/demucs
- Maintained fork (Alexandre Défossez):  
  https://github.com/adefossez/demucs

---

## Citation

If you use this project in research or public work, please cite the Demucs papers:

```bibtex
@inproceedings{rouard2022hybrid,
  title={Hybrid Transformers for Music Source Separation},
  author={Rouard, Simon and Massa, Francisco and D{\'e}fossez, Alexandre},
  booktitle={ICASSP 23},
  year={2023}
}

@inproceedings{defossez2021hybrid,
  title={Hybrid Spectrogram and Waveform Source Separation},
  author={D{\'e}fossez, Alexandre},
  booktitle={Proceedings of the ISMIR 2021 Workshop on Music Source Separation},
  year={2021}
}
```

---

## License

Demucs core code and model ecosystem follow upstream licensing and notices in this repository.  
For your own public release, keep the upstream `LICENSE` and attribution section intact.
