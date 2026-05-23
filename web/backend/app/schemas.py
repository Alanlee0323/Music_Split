from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import AVAILABLE_MODELS, AVAILABLE_STEMS


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int


class YouTubeRequest(BaseModel):
    url: str


class JobCreate(BaseModel):
    file_id: str
    model: str = "htdemucs_ft"
    stems: str = "vocals"

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> str:
        if value not in AVAILABLE_MODELS:
            raise ValueError(f"Unsupported model: {value}")
        return value

    @field_validator("stems")
    @classmethod
    def validate_stems(cls, value: str) -> str:
        if value not in AVAILABLE_STEMS:
            raise ValueError(f"Unsupported stems option: {value}")
        return value


class JobStatus(str, Enum):
    pending = "pending"
    downloading = "downloading"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    status: JobStatus
    model: str
    stems: str
    created_at: datetime
    completed_at: datetime | None = None
    error: str | None = None
    output_files: list[str] = Field(default_factory=list)


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
