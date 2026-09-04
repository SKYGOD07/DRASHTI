"""Serves locally-transcoded HLS output for browser playback.

Spike-grade: serves a fixed local directory. Production version will map
camera_id -> its own HLS output directory once the ingestion service
manages per-camera ffmpeg processes (see docs/03_ARCHITECTURE.md).
"""
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/media", tags=["media"])

HLS_DIR = Path(__file__).resolve().parents[3] / "infra" / "hls_out"


@router.get("/spike/{filename}")
async def get_hls_file(filename: str):
    path = HLS_DIR / filename
    if not path.is_file():
        raise HTTPException(404, "not found")
    media_type = "application/vnd.apple.mpegurl" if filename.endswith(".m3u8") else "video/mp2t"
    return FileResponse(
        path,
        media_type=media_type,
        headers={"Cache-Control": "no-cache"},
    )
