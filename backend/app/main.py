from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config import get_settings
from app.database import Base
from app.database import engine
from app.redis_client import get_redis_client
from app.routers import admin
from app.routers import analysis
from app.routers import auth
from app.routers import avatars
from app.routers import profiles
from app.routers import votes

settings = get_settings()
Base.metadata.create_all(bind=engine)
logger = logging.getLogger("votee")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Votee backend version %s", settings.app_version)
    yield


app = FastAPI(title="Votee API", version=settings.app_version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, settings.public_app_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(avatars.router)
app.include_router(votes.router)
app.include_router(admin.router)
app.include_router(analysis.router)

uploads_directory = Path(__file__).resolve().parents[1] / "uploads"
uploads_directory.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_directory), name="uploads")


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    redis_client = get_redis_client()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        redis_client.ping()
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Dependency check failed: {error}") from error
    return {"status": "ok", "version": settings.app_version}
