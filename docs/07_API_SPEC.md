# 07 — API Spec (v0, will grow — FastAPI auto-generates OpenAPI at `/docs`)

Base URL (dev): `http://localhost:8000/api/v1`. All routes except `/health` and `/auth/*` require `Authorization: Bearer <JWT>`.

## Auth
- `POST /auth/login` → `{email, password}` → `{access_token, role}`
- `POST /auth/register` → admin-only, creates a user

## Camera Registry (Model 1)
- `GET /cameras` — list, filterable by `?department=&status=&type=`
- `POST /cameras` — create (admin/operator)
- `POST /cameras/bulk-import` — multipart CSV upload
- `GET /cameras/{id}` — detail
- `PATCH /cameras/{id}` — update metadata
- `GET /cameras/geojson` — FeatureCollection for the map layer
- `GET /cameras/gap-report` — offline/degraded/ageing cameras summary

## Live Feeds (Model 2)
- `GET /cameras/{id}/stream` — returns HLS manifest URL for playback
- `GET /cameras/{id}/status` — heartbeat/connectivity detail

## Detections
- `GET /detections` — filterable by `?camera_id=&plate=&from=&to=`
- `GET /detections/{id}` — includes snapshot URL

## Vehicle Tracking (the graded core scenario)
- `GET /vehicles/{plate}/route` → `{plate, detections: [{camera_id, camera_name, lat, lon, detected_at, snapshot_url}, ...], geojson_line}`

## Watchlist
- `GET /watchlist` / `POST /watchlist` / `PATCH /watchlist/{id}` / `DELETE /watchlist/{id}`
- `POST /watchlist/bulk-import` — CSV

## Alerts
- `GET /alerts` — filterable by `?status=&from=&to=`
- `PATCH /alerts/{id}` — acknowledge/dismiss
- `WS /ws/alerts` — live push of new alerts (and optionally live detections on a separate channel/topic)

## Health
- `GET /health` — `{status: "ok", db: bool, redis: bool}`
