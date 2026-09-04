# 05 — 7-Day Roadmap (to Sept 10-11 event)

Today: 2026-09-04. Registration closes 2026-09-07. Event: 2026-09-10 to 11.

Rule for every day: **do not start the next day's work until today's is demonstrably working**, even ugly. Logic before design, per your instruction — Phase B (visual polish) only starts once Phase A's end-to-end loop works on at least one real feed.

## Day 1 (Sep 4, today) — Skeleton + Ground Truth Schema
- [x] Docs, repo layout, tech stack decision (this session)
- [ ] `docker-compose.yml` up: Postgres+PostGIS, Redis, MinIO, backend skeleton, frontend skeleton
- [ ] DB schema migrated (see `06_DATA_MODEL.md`)
- [ ] Seed script: sample cameras (GeoJSON around Gandhinagar/Ahmedabad) + sample watchlist plates
- [ ] `GET /health`, `GET /cameras` return real DB data

## Day 2 (Sep 5) — Registry + GIS Map (Model 1)
- [ ] Camera CRUD API (create/list/update/bulk-CSV-import)
- [ ] Frontend: Leaflet map rendering camera markers from `/cameras/geojson`, colored by status
- [ ] Registry admin page: table view, filters by department/type/status
- [ ] Gap-analysis stub report (cameras offline > N hours)

## Day 3 (Sep 6) — Feed Ingestion + ANPR Pipeline (Model 2 core)
- [ ] `RTSPAdapter` + ffmpeg RTSP→HLS transcode for 1-2 test streams (use your own filmed clip looped via `ffmpeg -re -stream_loop -1` as a fake RTSP source if no live feed yet)
- [ ] Frame sampler → YOLOv8 plate/vehicle detection → PaddleOCR → `Detection` written to DB
- [ ] Frontend: Live Wall page playing HLS streams in a grid

## Day 4 (Sep 7 — registration closes today) — Watchlist + Alerts + Correlation
- [ ] Watchlist CRUD + CSV seed (your own representative stolen-vehicle/wanted-plate dataset)
- [ ] Correlation engine: every detection checked against watchlist → `Alert` row + Redis publish
- [ ] WebSocket endpoint + frontend Alert feed (toast/list, live-updating)
- [ ] Web Push wired for at least one alert type (stretch if time-tight, don't block on this)

## Day 5 (Sep 8) — Vehicle Route Reconstruction (the graded core scenario)
- [ ] `GET /vehicles/{plate}/route` — all detections for a plate, ordered by time, joined to camera coordinates
- [ ] Frontend: Vehicle Search page — enter a plate, see timestamped list + animated route line on the map
- [ ] **End-to-end dry run**: onboard a camera → feed a test clip with a known plate → confirm it appears in watchlist alert AND in route reconstruction. This is the demo script — rehearse it today, not on Day 7.

## Day 6 (Sep 9) — PWA Polish + Mobile Install (Phase B starts here, not before)
- [ ] `vite-plugin-pwa` manifest + service worker, verify "Add to Home Screen" works on an actual phone
- [ ] Responsive layout pass on Map, Live Wall, Vehicle Search, Alerts
- [ ] RBAC/login screen polish
- [ ] HLD document + architecture diagrams finalized (`docs/03_ARCHITECTURE.md` as the base)
- [ ] Record the "own feed" demo video (2-3 min) per submission requirements

## Day 7 (Sep 10 — event day 1) — Government Feed Test + Submission
- [ ] Pull government test camera credentials, onboard the ~50 cameras via bulk import
- [ ] Run the rehearsed demo script against real government feeds
- [ ] Record government-feed demo video + output report (detected plates + timestamps table/CSV)
- [ ] Finalize Solution Presentation (PPT/PDF) using `01_BLUEPRINT.md` + `08_MODEL_MAPPING_HYBRID.md` as source material
- [ ] Submit: YouTube (unlisted) or Drive links, GitHub repo link, hosted platform URL + test creds if ready

## Event days (Sep 10-11)
On-site/live evaluation against the government feed and the surprise plate-tracing test — this is why Day 5's end-to-end rehearsal matters: the exact same flow just runs against a new plate under time pressure.

## Risk list (revisit daily)
- Government feed access only lands ~Sep 7 evening at earliest → everything through Day 5 MUST work on self-provided footage so we're not blocked.
- ANPR accuracy on Indian plates (fonts, lighting, angle) is the single biggest technical risk — budget real testing time Day 3-4, don't assume it "just works."
- RTSP/ONVIF quirks per camera vendor are common — build the adapter interface generically from Day 3 so a broken vendor doesn't block the whole demo.
