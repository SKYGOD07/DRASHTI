# 03 — System Architecture

## High-level flow

```
[Dept CCTV / Govt Test Cameras]                 [Watchlist DB (our own seed data)]
        │  RTSP / ONVIF / HTTP snapshot                  │
        ▼                                                │
┌───────────────────────┐                                │
│  Ingestion Layer        │  ffmpeg transcode RTSP→HLS     │
│  (adapter per protocol) │  frame sampler (1-2 fps to AI) │
└──────────┬─────────────┘                                │
           │ raw frames                                   │
           ▼                                               │
┌───────────────────────┐                                 │
│  AI Pipeline            │  YOLOv8 plate/vehicle detect    │
│  (backend/app/ai)       │  PaddleOCR plate read            │
└──────────┬─────────────┘                                 │
           │ detection event {plate, camera_id, ts, bbox, snapshot}
           ▼                                               │
┌───────────────────────┐        cross-check plate  ◄──────┘
│  Correlation Engine     │────────────────────────►  MATCH → Alert
│ (backend/app/services)  │
└──────────┬─────────────┘
           │ stores
           ▼
┌───────────────────────┐        ┌─────────────────────┐
│ PostgreSQL + PostGIS    │◄──────│ Camera Registry (GIS)│
│ (cameras, detections,   │       │ onboarding, metadata │
│  alerts, watchlist)     │       └─────────────────────┘
└──────────┬─────────────┘
           │ REST + WebSocket
           ▼
┌───────────────────────┐
│  FastAPI Backend         │
└──────────┬─────────────┘
           │
           ▼
┌───────────────────────┐
│  React PWA (frontend)    │  Map view · Live wall · Vehicle search ·
│  installable on mobile   │  Alert feed · Registry admin
└───────────────────────┘
```

## Core modules

### 1. Camera Registry & GIS (Model 1 backbone)
- CRUD for camera metadata: id, department, lat/lon, type (fixed/PTZ/ANPR-dedicated), ownership, connectivity status, stream URL/credentials (encrypted), install date, last-seen heartbeat.
- Bulk CSV import + manual entry + (later) API onboarding.
- PostGIS backs a `/cameras/geojson` endpoint the map consumes directly.
- Heartbeat job pings each stream URL periodically → drives "online/offline/degraded" status and the gap-analysis report.

### 2. Ingestion Layer (Model 2 capability)
- One adapter per protocol: `RTSPAdapter`, `ONVIFAdapter`, `HTTPSnapshotAdapter` — all implement a common `FeedAdapter` interface (`start()`, `stop()`, `get_frame()`). This is the seam that lets us claim "extensible toward Model 3 federation" without lying.
- `ffmpeg` transcodes each active RTSP feed to HLS segments served statically for browser playback (`hls.js` on the frontend). We do **not** store 24/7 raw video — only short rolling buffers + AI-triggered evidence clips (mirrors Model 2's "no centralized storage" framing, keeps storage cost near zero for the demo).
- A frame sampler pulls 1-2 frames/sec per camera for AI inference — full framerate isn't needed for ANPR and keeps compute bounded for a 50-camera PoC.

### 3. AI Pipeline
- YOLOv8 detects vehicles + plate regions on each sampled frame.
- Plate crop → PaddleOCR → normalized plate string.
- Emits a `Detection` event: `{camera_id, plate_text, confidence, timestamp, bbox, snapshot_url}` onto Redis pub/sub channel `detections`.

### 4. Correlation Engine
- Subscribes to `detections`.
- (a) Writes every detection to Postgres (this is what powers vehicle-route reconstruction — query by plate, order by timestamp, join camera lat/lon).
- (b) Checks plate against `watchlist` table → on match, writes an `Alert` row and publishes to Redis channel `alerts`.
- Backend WebSocket endpoint subscribes to `alerts` and `detections` and pushes to connected frontend clients in real time.

### 5. Vehicle Tracking / Route Reconstruction
- `GET /vehicles/{plate}/route` → all detections for that plate, ordered by time, joined to camera GIS coordinates → GeoJSON LineString + point markers with timestamps. This single endpoint is what the evaluation's core test scenario is graded on — build and stress-test it early.

### 6. Watchlist Management
- Simple CRUD + CSV import for a representative watchlist (stolen vehicle plates, wanted-person-linked plates). Own, self-created dataset — no external dependency needed.

## Security / RBAC
- JWT auth; roles: `admin` (full registry + watchlist edit), `operator` (view feeds, receive alerts), `viewer` (read-only registry + map).
- Camera credentials encrypted at rest (Fernet symmetric, key from env var — see API keys doc).
- All routes behind auth except health check.

## Why this scales toward 80,000 cameras (the written answer, not built)
- Ingestion adapters are horizontally scalable — one ingestion worker pool per N cameras, orchestrated by Kubernetes with autoscaling on queue depth.
- AI inference is the real bottleneck at scale → batch inference on GPU nodes, frame sampling rate tunable per camera priority (ANPR-critical corridors get higher fps).
- Redis pub/sub → Kafka migration path documented (topic-per-region) once throughput exceeds a single Redis instance.
- Storage: object storage (S3/MinIO) with lifecycle policies — hot (7 days), warm (30 days), cold/archive (90+ days) — only for AI-flagged evidence clips, not full raw video, keeping storage cost sub-linear in camera count.
