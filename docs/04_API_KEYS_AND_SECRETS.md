# 04 — API Keys & Accounts Needed From You

Nothing here is needed to start coding (Day 1-2 works entirely offline/local with sample data). This is your **shopping list** — get the "Required before Day X" items done by that day so nothing blocks the build.

## Required before Day 1 (blocks nothing today, but do these first — they're free/instant)

| # | What | Where to get it | Why | Cost |
|---|---|---|---|---|
| 1 | **Sentinel Hackathon portal login** | https://sentinel.gujarat.gov.in/register (you likely already have this) | Needed to reach the Resources page for the 50 government test camera feeds + credentials | Free |
| 2 | **GitHub account/repo** | github.com | Source code submission requirement | Free |
| 3 | **Google Drive or YouTube (unlisted)** | existing Google account is fine | Required submission method for demo videos | Free |

## Required before Day 3-4 (feed ingestion + AI)

| # | What | Where to get it | Why | Cost |
|---|---|---|---|---|
| 4 | **Government test camera credentials** (RTSP URLs / API keys / VMS creds for the ~50 cameras) | Sentinel portal → Resources page, released after registration closes / shortlisting | This is the actual integration test data — everything before this uses your own sample feeds/videos | Free (provided by organizers) |
| 5 | **A few sample public/dashcam CCTV RTSP feeds or recorded clips with visible number plates** (for your OWN dev/demo, independent of govt feeds) | You can: (a) film your own test footage of a vehicle+plate, (b) use royalty-free traffic footage from YouTube/Pexels for local testing only — **do not use unlicensed footage in the actual submission video**, only for dev | Needed Day 1-3 before govt feeds are available, to build/test the ANPR pipeline | Free |

## Optional — only if we want cloud hosting for the judge-facing demo URL

| # | What | Where to get it | Why | Cost |
|---|---|---|---|---|
| 6 | **A cloud VM or PaaS account** — pick ONE: Railway, Render, or a basic AWS/GCP/Azure free-tier VM | railway.app / render.com / cloud.google.com free tier / aws.amazon.com free tier | To host a public HTTPS URL for the platform (brief allows submitting "hosted platform + test credentials" as an alternative/addition to video) | Free tier usually sufficient for demo scale |
| 7 | **Domain name (optional, not required)** | Any registrar, or just use the platform's free subdomain | Cosmetic only — not required by the brief | Optional |
| 8 | **Vercel or Netlify account** (if hosting frontend separately from backend) | vercel.com / netlify.com | Easiest way to host the PWA with free HTTPS + auto-deploy from GitHub | Free tier |

## Optional — only if you want push notifications to actually reach a phone screen

| # | What | Where to get it | Why | Cost |
|---|---|---|---|---|
| 9 | **VAPID keypair for Web Push** | Generated locally (`web-push generate-vapid-keys` — no account needed, just a CLI command) | Enables the "alert reaches officer's phone" demo via the PWA's service worker | Free, self-generated |

## Explicitly NOT needed (common traps — don't waste time signing up for these)

- ❌ No paid ANPR/OCR API (Google Vision, AWS Rekognition, etc.) — we use open-source YOLOv8 + PaddleOCR locally, zero cost, zero API key, and it's more defensible in the "no vendor lock-in" architecture principle the brief explicitly asks for.
- ❌ No Kafka Cloud / Confluent account — Redis Pub/Sub is enough for 50-camera PoC scale.
- ❌ No VAHAN/SARTHI/eGujCop/AFIS/NAFIS integration keys — brief says "integration readiness," not actual integration. We just need a documented adapter interface + a paragraph in the HLD, not real credentials.
- ❌ No commercial VMS/vendor SDK license — we integrate via open RTSP/ONVIF only.
- ❌ No GPU cloud credits required for the PoC — YOLOv8n runs acceptably on CPU at 50-camera/1-2fps sampling scale. Only get GPU access if inference is visibly too slow during testing (then: a single cheap GPU VM, e.g. a Lambda Labs or RunPod on-demand instance, billed hourly).

## Internal secrets you (or I) generate, not sign up for

These go in `backend/.env` (see `.env.example`), never committed:

- `SECRET_KEY` — JWT signing key, generate with `openssl rand -hex 32`
- `FERNET_KEY` — for encrypting camera credentials at rest, generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `DATABASE_URL`, `REDIS_URL`, `MINIO_*` — local Docker Compose defaults, no external account needed for dev

## Action items for you right now, in order

1. ✅ Confirm you can log into the Sentinel portal.
2. ⬜ Start filming/collecting 1-2 short own test clips with a visible number plate (for Day 3 ANPR testing) — a car in a parking lot is enough.
3. ⬜ Create a GitHub repo (empty is fine, I'll set up the remote and push once you say go — I will NOT push anywhere without asking first).
4. ⬜ Decide hosting later (Day 5-6 decision, not urgent) — Railway is the simplest single choice if you want a public URL.
5. ⬜ Watch the Resources page after registration closes (Sept 7) for the 50-camera credentials — this is the one item genuinely outside our control and on the critical path.
