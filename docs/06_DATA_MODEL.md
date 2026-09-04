# 06 — Data Model

PostgreSQL + PostGIS. Simplified for a 1-week PoC — normalize further only if a real need shows up.

## `cameras`
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| name | text | |
| department | text | Municipal / Transport / Police / Institution |
| camera_type | text | fixed / ptz / anpr-dedicated |
| location | geography(Point, 4326) | PostGIS point, powers the map |
| address | text | free text |
| stream_url | text (encrypted) | RTSP/ONVIF/HTTP url — Fernet-encrypted at rest |
| stream_protocol | text | rtsp / onvif / http-snapshot |
| ownership | text | department-owned / private / shared |
| status | text | online / offline / degraded — set by heartbeat job |
| last_seen_at | timestamptz | |
| installed_at | date | for ageing-infra gap reports |
| created_at, updated_at | timestamptz | |

## `detections`
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| camera_id | uuid fk → cameras | |
| plate_text | text | normalized (uppercase, no spaces) |
| confidence | float | OCR confidence 0-1 |
| detected_at | timestamptz | indexed — this is the sort key for route reconstruction |
| bbox | jsonb | [x,y,w,h] on the source frame |
| snapshot_url | text | MinIO/S3 object key, plate crop image |
| vehicle_type | text | nullable, if we add vehicle classification |
| created_at | timestamptz | |

Index: `(plate_text, detected_at)` — this is the hot path for `GET /vehicles/{plate}/route`.

## `watchlist`
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| plate_text | text | normalized, unique |
| category | text | stolen-vehicle / wanted-person-vehicle / blacklisted |
| description | text | free text, e.g. linked FIR/case ref |
| added_by | uuid fk → users | |
| active | bool | soft-disable without deleting |
| created_at | timestamptz | |

## `alerts`
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| detection_id | uuid fk → detections | |
| watchlist_id | uuid fk → watchlist | |
| camera_id | uuid fk → cameras | denormalized for fast alert-feed queries |
| status | text | new / acknowledged / dismissed |
| acknowledged_by | uuid fk → users, nullable | |
| created_at | timestamptz | |

## `users`
| column | type | notes |
|---|---|---|
| id | uuid pk | |
| email | text unique | |
| password_hash | text | |
| role | text | admin / operator / viewer |
| department | text | nullable, for department-scoped viewers |
| created_at | timestamptz | |

## Notes
- All geo queries (gap analysis, "cameras within radius", route line rendering) go through PostGIS functions (`ST_DWithin`, `ST_MakeLine`) rather than app-level math.
- `detections` is the append-only event log — never updated, only inserted. This makes replay/audit trivial and matches the brief's "metadata audit trail" requirement.
- Snapshot images/evidence clips live in object storage (MinIO/S3), only the reference key lives in Postgres — keeps the DB small and fast.
