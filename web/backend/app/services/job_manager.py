from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.config import SEPARATED_DIR, UPLOAD_DIR
from app.schemas import JobStatus


@dataclass
class Job:
    id: str
    file_id: str
    filename: str
    status: JobStatus
    model: str
    stems: str
    created_at: datetime
    completed_at: datetime | None = None
    error: str | None = None
    output_files: list[str] = field(default_factory=list)


_jobs: dict[str, Job] = {}
_jobs_lock = Lock()


def create_job(file_id: str, filename: str, model: str, stems: str) -> Job:
    job = Job(
        id=str(uuid4()),
        file_id=file_id,
        filename=filename,
        status=JobStatus.pending,
        model=model,
        stems=stems,
        created_at=datetime.now(timezone.utc),
    )
    with _jobs_lock:
        _jobs[job.id] = job
    return job


def get_job(job_id: str) -> Job | None:
    with _jobs_lock:
        return _jobs.get(job_id)


def list_jobs() -> list[Job]:
    with _jobs_lock:
        return sorted(_jobs.values(), key=lambda job: job.created_at, reverse=True)


def update_job(job_id: str, **kwargs) -> Job | None:
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is None:
            return None

        if "status" in kwargs and isinstance(kwargs["status"], str):
            kwargs["status"] = JobStatus(kwargs["status"])

        for key, value in kwargs.items():
            if key == "output_files" and value is not None:
                value = list(value)
            setattr(job, key, value)

        if job.status in {JobStatus.completed, JobStatus.failed} and job.completed_at is None:
            job.completed_at = datetime.now(timezone.utc)

        return job


def delete_job(job_id: str) -> bool:
    with _jobs_lock:
        job = _jobs.pop(job_id, None)
        if job is None:
            return False
        other_jobs_share_upload = any(existing.file_id == job.file_id for existing in _jobs.values())

    if not other_jobs_share_upload:
        for upload_path in UPLOAD_DIR.glob(f"{job.file_id}_*"):
            if upload_path.is_file():
                upload_path.unlink(missing_ok=True)

    model_dir = SEPARATED_DIR / job.model
    if model_dir.exists():
        for separated_path in model_dir.glob(f"{job.file_id}_*"):
            _delete_path(separated_path)

    return True


def _delete_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    elif path.exists():
        path.unlink(missing_ok=True)
