# 01 — Project Blueprint

## The name

**DRASHTI (દ્રષ્ટિ)** — "vision / sight" (Gujarati & Sanskrit). Backronym: **D**igital **R**egistry **A**nd **S**urveillance **T**racking **H**ub for **I**nvestigation.

Say it in the pitch as: *"Every department has cameras. Nobody has drashti — sight across all of them. That's what we built."*

## The real problem (read between the lines of the brief)

- ~80,000 cameras statewide, owned by different departments (Municipal, Transport, Police, institutions), on different VMS platforms, different vendors, different formats.
- No single registry of what exists, where, or whether it even works.
- No way to answer "where has this vehicle been in the last 6 hours" across camera boundaries.
- No way to say "alert me the moment a watchlisted plate/person appears on any feed."

Everything in the four reference models is really in service of **one operational question**: *given a plate number, reconstruct its journey across the state's cameras, and do it in real time for watchlist matches.* The onboarding/scoring test scenario makes this explicit — that's the one thing we cannot fail at.

## What we are building (hybrid model, explicitly permitted)

We are **not** picking exactly one of Models 1–4. We're building:

- **Model 1 backbone (mandatory foundation):** a real camera registry with GIS mapping — every onboarded camera has location, department, type, status, connectivity metadata. This is the spine everything else hangs off.
- **Model 2 capability on top:** direct feed integration (RTSP/ONVIF/HTTP snapshot) from the ~50 government test cameras + our own sample feeds, ANPR extraction, event tagging, and a unified multi-camera viewing wall — **without** disturbing or replacing any department's existing VMS.
- **Cross-camera vehicle tracking**: stitch ANPR detections across camera + timestamp into a route/timeline, rendered on the GIS map (this is the single most points-dense feature — it is explicitly graded).
- **Watchlist correlation engine**: every ANPR detection is checked in real time against a watchlist DB (stolen vehicles, wanted persons' associated vehicles, blacklisted plates) → generates a real-time alert.
- **Architected for growth toward Model 3/4**: the ingestion layer is written as pluggable adapters (RTSP adapter today, ONVIF/vendor-SDK adapter tomorrow) so it can become a federation middleware without a rewrite — this is a "bonus points" talking point, not something we build in week 1.

## Non-goals for this hackathon (say "future roadmap" for these, don't build them)

- Facial recognition (mention as roadmap item; only add if time remains after core loop works — real bonus points but high effort/risk)
- Full centralized video storage/archival at scale (Model 4 territory — out of scope for a 1-week PoC on 50 cameras)
- Native iOS/Android builds — PWA covers "usable as a mobile app" per your instruction
- Multi-tenant department onboarding workflows beyond what's needed for the demo

## Success criteria (mirrors the official evaluation rubric — build to this checklist, nothing more, nothing less until it's green)

1. ✅ Onboard the ~50 government test cameras onto DRASHTI
2. ✅ Live/recorded viewing of those feeds in a unified wall
3. ✅ Given a plate number during evaluation → show full timestamped, location-wise route across cameras
4. ✅ Live correlation of feeds against a watchlist DB → automatic real-time alert on match
5. ✅ GIS map visualizing all cameras + the reconstructed vehicle route
6. ✅ Searchable event/detection history
7. ✅ HLD document + architecture diagrams
8. ✅ Own-feed demo video (2-3 min, must be a real working backend, not mockups)
9. ✅ Government-feed demo video + output report (detections + timestamps)
10. ✅ Scalability story toward 80,000 cameras (doesn't need to be built, needs to be a credible written+verbal answer)

## Sequencing philosophy (per your instruction: logic/working first, design later)

Phase A (Day 1-5): make the core loop **work end-to-end, ugly UI is fine** — onboard camera → ingest feed → detect plate → match watchlist → fire alert → show route on map.
Phase B (Day 6): PWA polish, installability, responsive layout, GIS visuals.
Phase C (Day 7): test against real government feeds, record demo videos, finalize docs, submit.

Never let Phase B start before Phase A's end-to-end loop is provably working on at least one real feed.
