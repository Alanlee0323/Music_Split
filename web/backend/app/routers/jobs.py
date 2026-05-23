from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, Response, status

from app.config import SEPARATED_DIR, UPLOAD_DIR
from app.schemas import JobCreate, JobListResponse, JobResponse, JobStatus
from app.services.demucs_runner import run_separation
from app.services.job_manager import create_job, delete_job, get_job, list_jobs, update_job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _find_uploaded_file(file_id: str) -> Path | None:
    return next(UPLOAD_DIR.glob(f"{file_id}_*"), None)


def _job_to_response(job) -> JobResponse:
    return JobResponse.model_validate(job)


def _process_job(job_id: str, audio_path: Path, model: str, stems: str) -> None:
    update_job(job_id, status=JobStatus.processing, error=None, completed_at=None)
    try:
        output_files = run_separation(audio_path=audio_path, output_dir=SEPARATED_DIR, model=model, stems=stems)
        update_job(
            job_id,
            status=JobStatus.completed,
            output_files=output_files,
            completed_at=datetime.now(timezone.utc),
            error=None,
        )
    except Exception as exc:
        update_job(
            job_id,
            status=JobStatus.failed,
            error=str(exc),
            completed_at=datetime.now(timezone.utc),
        )


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_separation_job(job_request: JobCreate, background_tasks: BackgroundTasks) -> JobResponse:
    uploaded_path = _find_uploaded_file(job_request.file_id)
    if uploaded_path is None or not uploaded_path.is_file():
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    filename = uploaded_path.name.split("_", 1)[1] if "_" in uploaded_path.name else uploaded_path.name
    job = create_job(
        file_id=job_request.file_id,
        filename=filename,
        model=job_request.model,
        stems=job_request.stems,
    )
    background_tasks.add_task(_process_job, job.id, uploaded_path, job.model, job.stems)
    return _job_to_response(job)


@router.get("/", response_model=JobListResponse)
def get_jobs() -> JobListResponse:
    return JobListResponse(jobs=[_job_to_response(job) for job in list_jobs()])


@router.get("/{job_id}", response_model=JobResponse)
def get_single_job(job_id: str) -> JobResponse:
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_response(job)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_job(job_id: str) -> Response:
    if get_job(job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found")
    delete_job(job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
