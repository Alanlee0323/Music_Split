import re
from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import SUPPORTED_AUDIO_FORMATS, UPLOAD_DIR
from app.schemas import UploadResponse, YouTubeRequest
from app.services.ytdlp import download_youtube

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/file", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    original_name = Path(file.filename or "").name
    if not original_name:
        raise HTTPException(status_code=400, detail="A filename is required")

    extension = Path(original_name).suffix.lower()
    if extension not in SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format: {extension}")

    file_id = str(uuid4())
    stored_path = UPLOAD_DIR / f"{file_id}_{original_name}"
    size = 0

    try:
        async with aiofiles.open(stored_path, "wb") as output_file:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                await output_file.write(chunk)
    except Exception as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to save uploaded file") from exc
    finally:
        await file.close()

    return UploadResponse(file_id=file_id, filename=original_name, size=size)


@router.post("/youtube", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_youtube(request: YouTubeRequest) -> UploadResponse:
    try:
        title, downloaded_path = await download_youtube(request.url, UPLOAD_DIR)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    file_id = str(uuid4())
    safe_title = re.sub(r"[^A-Za-z0-9._ -]", "_", title).strip().rstrip(".") or downloaded_path.stem
    stored_path = UPLOAD_DIR / f"{file_id}_{safe_title}{downloaded_path.suffix}"

    try:
        downloaded_path.rename(stored_path)
    except OSError as exc:
        raise HTTPException(status_code=500, detail="Failed to finalize YouTube download") from exc

    return UploadResponse(
        file_id=file_id,
        filename=f"{title}{stored_path.suffix}",
        size=stored_path.stat().st_size,
    )
