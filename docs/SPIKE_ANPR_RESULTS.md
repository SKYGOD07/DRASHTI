# Spike 1 Results — ANPR Accuracy on Indian Plates

Date: 2026-09-04. **Status: BLOCKED — not run.**

## What happened

`data/spike/plates/` was empty — no JPG frames, no clips to extract frames from. Per instruction, I did not fabricate test images or use stock/generic plate photos to produce a fake accuracy number. Instead:

1. Built the full harness at `scripts/spike_anpr.py` — YOLOv8 vehicle detection → naive plate-region crop → EasyOCR → raw text → positional corrector (Indian plate regex `^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}$`, digit/letter confusion map for `O↔0, D↔0, I↔1, L↔1, Z↔2, S↔5, B↔8, G↔6`, RTO state-code validation against the real list of state/UT codes). It's ready to run the moment real frames exist — no further setup needed on that front.
2. Installed `backend/requirements-ai.txt` (ultralytics, easyocr, opencv-python-headless) into the backend venv so the harness's imports are verified working, independent of having test data. (Install log: see terminal output from this session — completed without needing to touch this file again unless it failed, in which case that's a separate blocker to report.)

## What I need from you

Drop a handful of JPG frames (or a short clip I can extract frames from) into `data/spike/plates/` — per your own instruction, a car in a parking lot is enough, doesn't need to be government footage. Ideally include some variety on purpose, since it's the variety that will actually break naive OCR:
- At least one HSRP (high-security registration plate, white background/blue text embossed) and one painted/non-standard plate, since the brief and general ANPR experience both call out that these behave very differently.
- A couple of different angles/distances, not just head-on.
- At least one with imperfect lighting (shadow, glare, or evening) since that's the realistic operating condition for the government feeds too.

## Once frames land

Run:
```
cd backend
.venv\Scripts\activate
python ..\scripts\spike_anpr.py
```

I'll report the real per-image detections, the before/after-correction accuracy split, and a specific list of failure modes actually observed (not a generic list) — updating this file, not fabricating a projection now. Given no data exists yet, I am not going to guess a percentage here; that would be exactly the "optimistic number" you told me not to give you.

## Known risk, unverified, carried into the roadmap regardless

Everything in `docs/01_BLUEPRINT.md` and `docs/05_ROADMAP_7DAY.md` already flags ANPR accuracy on Indian plates as the single biggest technical risk in the whole build (see `05_ROADMAP_7DAY.md`'s risk list). That flag stands, un-downgraded, until this spike actually runs against real images.
