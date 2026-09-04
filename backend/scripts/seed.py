"""Seeds the drashti DB from data/camera_sample and data/watchlist_sample.

Usage (after migrations are applied):
    cd backend
    .venv\\Scripts\\python scripts\\seed.py
"""
import asyncio
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models import Camera, Watchlist

REPO_ROOT = Path(__file__).resolve().parents[2]
CAMERA_CSV = REPO_ROOT / "data" / "camera_sample" / "sample_cameras.csv"
WATCHLIST_CSV = REPO_ROOT / "data" / "watchlist_sample" / "sample_watchlist.csv"


async def seed_cameras(session) -> int:
    n = 0
    with open(CAMERA_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            existing = await session.scalar(select(Camera).where(Camera.name == row["name"]))
            if existing:
                continue
            point = WKTElement(f"POINT({row['lon']} {row['lat']})", srid=4326)
            session.add(
                Camera(
                    name=row["name"],
                    department=row["department"],
                    camera_type=row["camera_type"],
                    location=point,
                    address=row.get("address"),
                    ownership=row.get("ownership"),
                    stream_protocol=row.get("stream_protocol"),
                    status="offline",
                )
            )
            n += 1
    return n


async def seed_watchlist(session) -> int:
    n = 0
    with open(WATCHLIST_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            existing = await session.scalar(
                select(Watchlist).where(Watchlist.plate_text == row["plate_text"])
            )
            if existing:
                continue
            session.add(
                Watchlist(
                    plate_text=row["plate_text"],
                    category=row["category"],
                    description=row.get("description"),
                    active=True,
                )
            )
            n += 1
    return n


async def main() -> None:
    async with AsyncSessionLocal() as session:
        n_cams = await seed_cameras(session)
        n_watch = await seed_watchlist(session)
        await session.commit()
    print(f"Seeded {n_cams} cameras, {n_watch} watchlist entries (skipped any already present).")


if __name__ == "__main__":
    asyncio.run(main())
