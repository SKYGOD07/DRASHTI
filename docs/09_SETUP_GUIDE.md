# 09 — Local Dev Setup

## Prerequisites
- Docker Desktop (Windows) — for Postgres/PostGIS, Redis, MinIO
- Node.js 20+ (frontend)
- Python 3.11+ (backend) — a virtualenv is created under `backend/.venv`
- `ffmpeg` on PATH (for RTSP→HLS transcode) — Windows: `winget install ffmpeg` or download from ffmpeg.org

## One-time setup

```bash
# 1. copy env template and fill in generated secrets (see docs/04_API_KEYS_AND_SECRETS.md)
cp backend/.env.example backend/.env

# 2. start infra (Postgres+PostGIS, Redis, MinIO)
docker compose -f infra/docker-compose.yml up -d

# 3. backend
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
alembic upgrade head           # run migrations (once models exist)
python scripts/seed.py         # seed sample cameras + watchlist
uvicorn app.main:app --reload --port 8000

# 4. frontend (separate terminal)
cd frontend
npm install
npm run dev
```

- Backend API docs (auto-generated): http://localhost:8000/docs
- Frontend dev server: http://localhost:5173
- MinIO console: http://localhost:9001

## Testing the PWA install on a real phone
1. Run `npm run build && npm run preview` (PWA service worker only activates on a production build, not `npm run dev`).
2. Expose it to your phone on the same Wi-Fi: note the "Network" URL Vite prints, or use `ngrok http 4173` for a public HTTPS tunnel (installability requires HTTPS or localhost).
3. Open the URL on your phone's Chrome → menu → "Add to Home Screen."

## Faking an RTSP source before you have real camera access
```bash
ffmpeg -re -stream_loop -1 -i sample_clip.mp4 -c copy -f rtsp rtsp://localhost:8554/test
```
(requires a lightweight RTSP server like `mediamtx` running locally — add to `infra/docker-compose.yml` as `rtsp-simulator` when we get to Day 3).
