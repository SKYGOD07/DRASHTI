# 10 — Demo Script & Evaluation Mapping

## The rehearsed end-to-end demo script (build this on Day 5, run it identically on Day 7 with govt feeds)

1. **Registry**: show the GIS map with all onboarded cameras, color-coded by status/department. Click a camera → metadata panel.
2. **Onboarding**: bulk-import a CSV of cameras live, or show one already-onboarded — demonstrates Model 1 deliverable.
3. **Live wall**: open 2-4 camera feeds simultaneously in a grid, playing via HLS.
4. **Inject/point to a known plate** appearing on camera feed → show the detection appear in real time in the detections feed with plate text + confidence + snapshot.
5. **Watchlist match**: the same or a different plate is on the watchlist → alert fires in real time, visible in the Alerts panel (and ideally a phone push notification if the PWA is installed).
6. **Vehicle search**: type that plate into Vehicle Search → full timestamped route across every camera it appeared on, drawn as a line on the GIS map.
7. **Close with the scale/security talking points** from `03_ARCHITECTURE.md`'s last section and `08_MODEL_MAPPING_HYBRID.md`'s pitch paragraph.

Total demo time target: **under 3 minutes** for the "own feed" video, matching the submission requirement exactly.

## Mapping to the official evaluation rubric

| Rubric item | Where we address it |
|---|---|
| Successful Test Case (govt feed) | Day 7 — same rehearsed script, real cameras |
| Solution Presentation | `01_BLUEPRINT.md` + `08_MODEL_MAPPING_HYBRID.md` → slides |
| Solution Architecture (HLD) | `03_ARCHITECTURE.md` + `06_DATA_MODEL.md` + `07_API_SPEC.md` → HLD document |
| Working Platform & Demonstration | Day 5 rehearsal video + Day 7 govt-feed video |
| Video Analytics Output | ANPR detections table/CSV with camera, plate, timestamp — export from `/detections` |
| Scalability & PoC Readiness | Architecture doc's "why this scales" section + written infra-sizing answers |
| Submission Completeness | Track against the checklist below before Sep 10 |

## Submission checklist (fill in as completed)
- [ ] Solution Presentation (PPT/PDF)
- [ ] High-Level Design document
- [ ] Own-feed demo video (unlisted YouTube or Drive, 2-3 min, real backend)
- [ ] Government-feed demo video + output report (CSV/table of detections+timestamps)
- [ ] GitHub repo link (public or access-granted)
- [ ] Hosted platform URL + test login credentials (optional but recommended)
- [ ] All links verified as viewable by someone outside the team (test in an incognito window / different account)
