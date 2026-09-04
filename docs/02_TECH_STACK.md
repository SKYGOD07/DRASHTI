# 02 — Tech Stack

Optimized for: (a) one team can build it in ~6 days, (b) it's a real working backend not a mockup, (c) "webapp usable as a mobile app" via PWA, (d) matches the suggested stacks in the official brief so it reads as credible to evaluators.

## Frontend — PWA (this IS the "mobile app")

| Layer | Choice | Why |
|---|---|---|
| Framework | **React 18 + Vite** | Fast dev loop, huge ecosystem, matches brief's suggested stack |
| PWA | `vite-plugin-pwa` (Workbox under the hood) | Service worker, offline app-shell, installable ("Add to Home Screen"), web push |
| Styling | **Tailwind CSS** | Fast to build responsive mobile-first UI without design time upfront |
| Map/GIS | **Leaflet.js** (+ `react-leaflet`) | Lightweight, mobile-friendly, plays well with GeoJSON from PostGIS. OpenLayers is heavier — skip unless we need advanced GIS ops |
| Realtime | native `WebSocket` (or SSE fallback) | Live alert push, live detection feed |
| State/data | `@tanstack/react-query` | Caching, polling, dedupes network calls |
| Video playback | `hls.js` for HLS streams, plain `<video>`/MSE for WebRTC where used | Browsers can't play raw RTSP — must transcode server-side (see architecture doc) |
| Push notifications | Web Push API (VAPID keys, service worker) | "Alert on watchlist match" reaching an officer's phone without a native app |

## Backend

| Layer | Choice | Why |
|---|---|---|
| API framework | **Python + FastAPI** | Async, auto OpenAPI docs (free API documentation deliverable), and the AI/ANPR pipeline is Python-native anyway — one language end to end on the backend |
| Task/stream workers | `asyncio` workers + **Celery** (or simple `arq`) for background jobs (ingestion, ANPR inference) | Decouple slow video/AI work from the request/response API |
| Video ingestion | `ffmpeg` (via subprocess) for RTSP→HLS transcode; `onvif-zeep` for ONVIF discovery/PTZ where available | Matches the brief's own suggested protocols |
| Realtime bus | **Redis Pub/Sub** (Kafka is overkill for a 1-week PoC at 50-camera scale; document Kafka as the scale-up path) | Simple, fast, one Docker container, good enough for demo throughput |
| Auth | **JWT** (via `fastapi-users` or hand-rolled) + role-based access control (Admin / Department Operator / Viewer) | Matches brief's explicit RBAC requirement |

## AI / Video Analytics (ANPR — the mandatory analytics deliverable)

| Stage | Choice | Why |
|---|---|---|
| Vehicle/plate detection | **YOLOv8n** (Ultralytics, fine-tuned or pretrained + a plate-detection head) | Fast, well-documented, runs on CPU acceptably for demo scale, GPU if available |
| Plate OCR | **PaddleOCR** or **EasyOCR** | Strong out-of-box accuracy on Indian plates without training a custom OCR model |
| (Stretch/bonus) Face detection | `InsightFace` / `RetinaFace` | Only if core loop is done early — matches "bonus" analytics criterion |
| Inference serving | Plain FastAPI microservice (`backend/app/ai`), or `Triton` only if we have GPU infra to justify it | Keep it simple; one Python process is enough for 50 cameras in a PoC |

## Database & Storage

| Layer | Choice | Why |
|---|---|---|
| Primary DB | **PostgreSQL 16 + PostGIS** | Matches brief's suggested stack exactly; native geo queries for GIS layer and gap-analysis |
| Cache/pubsub | **Redis** | Session cache, alert pub/sub, rate limiting |
| Object storage (clips/snapshots) | **MinIO** (S3-compatible, local Docker) for dev; note **AWS S3 / Azure Blob** as the production path | Store ANPR snapshot crops + short evidence clips, not full 24/7 raw video (matches Model 2's "no centralized storage of all feeds" framing) |
| Search (optional, if time allows) | Postgres full-text search first; Elasticsearch only if we need it for scale story | Don't add a service we don't need for a 1-week PoC |

## Infra / DevOps

| Layer | Choice | Why |
|---|---|---|
| Local orchestration | **Docker Compose** (postgres+postgis, redis, minio, backend, ai-worker, frontend) | One `docker compose up`, reproducible for judges too |
| Hosting (for judge-accessible demo URL) | Any cheap VM with GPU-optional (e.g., a single cloud VM) or Railway/Render for services, Vercel/Netlify for the PWA frontend | Needs public HTTPS URL for "hosted platform + test credentials" submission option |
| CI (optional, nice-to-have) | GitHub Actions — lint + basic test on push | Only if time remains |

## Why this beats a "just use Model X's suggested stack" approach

The brief's own suggested stacks for Model 1/2 are almost exactly this (Leaflet/PostGIS/Node-or-Python/React). We picked **Python/FastAPI over Node** specifically because the AI/ANPR pipeline is Python-native — avoids a language boundary between the API and the analytics engine, which saves real days in a 1-week build.

See [`docs/04_API_KEYS_AND_SECRETS.md`](04_API_KEYS_AND_SECRETS.md) for what you need to go acquire before Day 2.
