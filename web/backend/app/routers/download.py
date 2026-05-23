from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import SEPARATED_DIR
from app.schemas import JobStatus
from app.services.job_manager import get_job

router = APIRouter(prefix="/api", tags=["download"])


def _find_output_dir(file_id: str, model: str) -> Path | None:
    model_dir = SEPARATED_DIR / model
    if not model_dir.exists():
        return None
    return next(model_dir.glob(f"{file_id}_*"), None)


@router.get("/jobs/{job_id}/download/{filename}")
def download_output_file(job_id: str, filename: str) -> FileResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.completed:
        raise HTTPException(status_code=400, detail="Job is not completed")
    if Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    if filename not in job.output_files:
        raise HTTPException(status_code=404, detail="Output file not found")

    output_dir = _find_output_dir(job.file_id, job.model)
    if output_dir is None:
        raise HTTPException(status_code=404, detail="Separated output directory not found")

    file_path = output_dir / filename
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(path=file_path, filename=filename, media_type="audio/wav")
