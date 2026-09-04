"""Camera registry endpoints.

Stubbed with in-memory sample data for Day 1 scaffolding. Swap for real
SQLAlchemy/PostGIS queries once app/models + DB session are wired up
(see docs/05_ROADMAP_7DAY.md, Day 1-2).
"""
from fastapi import APIRouter

router = APIRouter(prefix="/cameras", tags=["cameras"])

_SAMPLE_CAMERAS = [
    {
        "id": "cam-001",
        "name": "Gandhinagar Sector 18 Junction",
        "department": "Police",
        "camera_type": "anpr-dedicated",
        "lat": 23.2156,
        "lon": 72.6369,
        "status": "online",
    },
    {
        "id": "cam-002",
        "name": "Ahmedabad Ring Road - Vastrapur",
        "department": "Municipal Corporation",
        "camera_type": "fixed",
        "lat": 23.0395,
        "lon": 72.5296,
        "status": "online",
    },
    {
        "id": "cam-003",
        "name": "Surat Ring Road - Adajan",
        "department": "Transport",
        "camera_type": "ptz",
        "lat": 21.1959,
        "lon": 72.7933,
        "status": "offline",
    },
]


@router.get("")
async def list_cameras():
    return _SAMPLE_CAMERAS


@router.get("/geojson")
async def cameras_geojson():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [c["lon"], c["lat"]]},
                "properties": {k: v for k, v in c.items() if k not in ("lat", "lon")},
            }
            for c in _SAMPLE_CAMERAS
        ],
    }
