# DRASHTI (દ્રષ્ટિ) — Digital Registry & AI Surveillance Tracking Hub for Investigation

**Gujarat Police Innovation Hackathon 2026 — Sentinel Challenge submission**

> *Drashti* (દ્રષ્ટિ) is Gujarati/Sanskrit for **"vision" / "sight"** — the ability to see clearly across scattered, disconnected things. That's exactly the problem: ~80,000 cameras across Gujarat, run by different departments, on different systems, with no single "eye" watching over all of them. DRASHTI is that eye.

## What this is

A hybrid **Model 1 (Registry & GIS) + Model 2 (Unified Viewing & ANPR Analytics)** platform, architected to extend cleanly toward Model 3 (federation) and Model 4 (full central VMS) without a rewrite — per the challenge's explicit "hybrid or customised architecture" allowance.

Delivered as a **PWA (Progressive Web App)** — one React codebase, works as a normal website for judges/desks, and installs like a native app on any officer's phone (Add to Home Screen, offline shell, push alerts) — no app store, no separate mobile build.

## Start here

Read the docs in `docs/` in this order:

1. [`docs/01_BLUEPRINT.md`](docs/01_BLUEPRINT.md) — what we're building and why, mapped to the official evaluation checklist
2. [`docs/02_TECH_STACK.md`](docs/02_TECH_STACK.md) — full stack, with reasoning
3. [`docs/03_ARCHITECTURE.md`](docs/03_ARCHITECTURE.md) — system architecture & data flow
4. [`docs/04_API_KEYS_AND_SECRETS.md`](docs/04_API_KEYS_AND_SECRETS.md) — **everything you (Sahil) need to go sign up for / provide**
5. [`docs/05_ROADMAP_7DAY.md`](docs/05_ROADMAP_7DAY.md) — day-by-day build plan to the Sept 10-11 event
6. [`docs/06_DATA_MODEL.md`](docs/06_DATA_MODEL.md) — DB schema (camera registry, detections, watchlist, alerts)
7. [`docs/07_API_SPEC.md`](docs/07_API_SPEC.md) — REST/WebSocket contract between frontend and backend
8. [`docs/08_MODEL_MAPPING_HYBRID.md`](docs/08_MODEL_MAPPING_HYBRID.md) — how our hybrid maps to Models 1–4, for the justification slide
9. [`docs/09_SETUP_GUIDE.md`](docs/09_SETUP_GUIDE.md) — local dev setup, one command up
10. [`docs/10_DEMO_AND_EVALUATION.md`](docs/10_DEMO_AND_EVALUATION.md) — what we must demonstrate, mapped to submission requirements

## Repo layout

```
DRASHTI/
├── docs/                  # blueprint, all planning docs (this is the "spec")
├── backend/                # FastAPI monolith (modular, splittable later)
│   └── app/
│       ├── api/            # route handlers (cameras, detections, alerts, watchlist, tracking)
│       ├── core/           # config, security, db session, RBAC
│       ├── models/         # SQLAlchemy + Pydantic schemas
│       ├── services/       # ingestion, correlation engine, GIS/gap-analysis
│       └── ai/             # ANPR pipeline (detection + OCR), watchlist matcher
├── frontend/                # React + Vite PWA
│   └── src/
│       ├── pages/           # Map, Registry, Live Wall, Vehicle Search, Alerts, Admin
│       ├── components/
│       ├── services/         # API client, websocket client
│       └── hooks/
├── data/                    # sample camera + watchlist seed data
├── infra/                   # docker-compose, k8s manifests (later)
└── scripts/                 # onboarding scripts, seed scripts
```

## Current status

Ground-work / planning phase. No feature code yet — see `docs/05_ROADMAP_7DAY.md` for the build order. **Logic and working functionality first, design polish later**, per your instruction.
