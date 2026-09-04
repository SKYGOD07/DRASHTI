from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import cameras, health, media
from app.core.config import settings

app = FastAPI(
    title="DRASHTI API",
    description="Digital Registry And Surveillance Tracking Hub for Investigation "
    "— Gujarat Police Innovation Hackathon 2026",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(cameras.router, prefix="/api/v1")
app.include_router(media.router, prefix="/api/v1")
