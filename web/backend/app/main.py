from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import DATA_DIR, SEPARATED_DIR, UPLOAD_DIR
from app.routers.download import router as download_router
from app.routers.jobs import router as jobs_router
from app.routers.upload import router as upload_router

app = FastAPI(title="Demucs Web")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(jobs_router)
app.include_router(download_router)


@app.on_event("startup")
def ensure_data_directories() -> None:
    for directory in (DATA_DIR, UPLOAD_DIR, SEPARATED_DIR):
        directory.mkdir(parents=True, exist_ok=True)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
