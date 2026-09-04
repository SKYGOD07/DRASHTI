# Spike 2 Results — RTSP → Browser Playback

Date: 2026-09-04. Environment: Windows 11, ffmpeg 8.0.1 (chocolatey `essentials` build), Chrome (via claude-in-chrome automation).

## Verdict: works end-to-end, with one dependency swap and one open question

## What was actually run (reproducible via `scripts/spike_hls.ps1` / `spike_hls.sh`)

1. **RTSP server**: MediaMTX v1.20.1 (`infra/mediamtx/mediamtx.exe`), listening on `:8554`.
2. **Publisher**: `ffmpeg` reading a synthetic `testsrc` pattern with a wall-clock timestamp burned into every frame (`drawtext=%{localtime}`), publishing to MediaMTX over RTSP/TCP as a client.
3. **Consumer**: a second `ffmpeg` process pulling that RTSP stream and transcoding to HLS (`-f hls -hls_time 1 -hls_list_size 5 -hls_flags delete_segments+append_list`), writing segments to `infra/hls_out/`.
4. **Backend**: FastAPI (`backend/app/api/media.py`) serves `infra/hls_out/*.m3u8` and `*.ts` as static files under `/api/v1/media/spike/`.
5. **Frontend**: `frontend/public/spike-hls.html` using hls.js from CDN, plus direct-navigation testing in real Chrome.

Confirmed with real command output: `infra/hls_out/` filled with sequential `.ts` segments and a rolling `stream.m3u8` manifest while the pipeline ran; `curl` against the FastAPI-served manifest returned `200 OK` with correct content.

## Finding 1 — ffmpeg's own RTSP "server" mode does not work here (real blocker, worked around)

The obvious approach — `ffmpeg -f rtsp -rtsp_flags listen rtsp://localhost:8554/x` acting as its own RTSP server so a second ffmpeg can push/pull against it — **did not work** in this environment. Verbose logs show it entering `tcp_open` and printing `"Starting connection attempt to 127.0.0.1 port 8554"` and then hanging indefinitely — i.e. it behaves as a *client* trying to connect out, not a server binding and listening, despite `-rtsp_flags listen` being accepted as a valid option. Confirmed independently that raw socket bind/listen on port 8554 works fine at the OS level (a plain Python `socket.bind()` succeeded), so this is specific to this ffmpeg build's RTSP muxer, not an environment/sandbox network restriction. Tried both `-rtsp_flags listen` and the legacy `?listen` URL-suffix syntax — same hang both times.

**Workaround, and the better long-term choice anyway**: use a real RTSP server (MediaMTX) as the source, with ffmpeg only ever acting as a client (publish or pull). This is also **more representative of production** — real CCTV cameras/NVRs run their own RTSP server; our ingestion layer only ever needs to be an RTSP *client*. Net effect: this finding changed nothing about the target architecture, it just ruled out one implementation shortcut for local testing.

**Action item**: don't budget any time on Day 3 for "get ffmpeg to act as an RTSP server" — go straight to treating every camera as a client target, exactly like this spike ended up doing.

## Finding 2 — glass-to-glass latency: ~5 seconds measured, but the measurement is confounded (report the honest number, not a clean one)

Method: burned a real wall-clock (`YYYY-MM-DD HH:MM:SS`) into the video at encode time, then screenshotted the playing video in Chrome and compared the overlay time to actual system time at capture (bracketed before/after the screenshot call to bound round-trip error).

**Measured: ~5 seconds between encode time and what appeared on screen.**

This number is **not clean** and I'm not rounding it down to make it look better: Chrome's native player (triggered by direct navigation to the `.m3u8` URL, since that's what actually rendered in this sandboxed browser — see Finding 3) played the growing playlist **sequentially from the earliest available segment**, not from the live edge — the on-screen playhead read `4:14` while the stream had only been running ~2 minutes, i.e. it was catching up through buffered history, not tracking "now." A proper live-edge-following player (hls.js with `liveSyncDurationCount` configured, which is what `spike-hls.html` was set up to do) would give a materially different — likely lower — number, dominated by `hls_time` (1s) × `hls_list_size` startup buffer (~2-3 segments) ≈ **2-4 seconds expected in the real build**, but that path itself hit Finding 3 before it could be measured cleanly.

**Action item for Day 3**: re-measure with hls.js properly tracking live edge (not blocked by Finding 3) once the real ANPR pipeline exists — don't trust the ~5s number as final, treat "~2-5 seconds live glass-to-glass on 1s HLS segments" as the working assumption and re-verify on real government feeds during rehearsal.

## Finding 3 — hls.js fetch failed inside this automation sandbox; direct navigation worked; needs a real-device re-check

- `curl` confirmed the backend's CORS behavior is fully correct: both the `OPTIONS` preflight and the actual `GET` (with `Origin: http://localhost:5173`) return `access-control-allow-origin: http://localhost:5173` and a `200`.
- Direct top-level navigation in the automated Chrome tab to the manifest URL **played the stream correctly** (confirmed via screenshot — moving SMPTE color bars, live-updating wall-clock overlay).
- But loading the same manifest URL via hls.js's XHR loader, from a page served at `localhost:5173`, failed with `networkError` / `manifestLoadError`, response `code: 0` (a signature usually meaning the request never reached the network — commonly a CORS block, but our server-side CORS was independently verified correct via curl).

**Most likely explanation**: the claude-in-chrome browser-automation tool itself gates cross-origin XHR/fetch behind its own "site-level permissions" (per its own tool description) in a way that doesn't apply to top-level navigation. This is a property of the *testing sandbox*, not necessarily our app.

**Honesty check — I am not calling this resolved.** It needs a real re-test on: (a) a normal desktop Chrome window outside this automation harness, (b) an actual Android/iOS phone, before Day 6's PWA polish pass. If it turns out to be a real CORS/XHR issue and not a sandbox artifact, the fix is straightforward (it would most likely be a missing `Access-Control-Expose-Headers` for byte-range requests hls.js may need, or credentials-mode mismatch) but I have not diagnosed it further because the server-side evidence points away from a genuine bug. **Flagging as open, not closing it.**

## Other notes captured for later

- **CORS**: verified working correctly server-side for both preflight and actual requests (see Finding 3). No further action needed unless Finding 3 turns out to be a real bug.
- **iOS Safari**: not device-tested (no iOS device available in this environment). Documented behavior from prior experience, not verified here: Safari plays HLS natively via `<video src="...m3u8">` without needing hls.js at all; `spike-hls.html` already branches on `video.canPlayType('application/vnd.apple.mpegurl')` to skip hls.js on Safari. **Must be verified on a real iPhone before the demo — do not assume this works untested.**
- **fontconfig warning**: this ffmpeg build threw `Fontconfig error: Cannot load default config file` when `drawtext` was used without an explicit `fontfile=`. Harmless once a `fontfile=` path is given explicitly (used `C:/Windows/Fonts/arial.ttf` throughout), but this is a sign the ffmpeg build's fontconfig is not properly set up — irrelevant to production (drawtext overlays are a testing/debug convenience, not a planned production feature) but noting in case any future filter relies on fontconfig defaults.
- **`%{pts:hms}` vs `%{localtime}` in drawtext**: `%{pts:hms}` shows time relative to stream/encoder start, not wall-clock — not useful for latency measurement unless you also record the encoder's exact start time. `%{localtime}` (no format argument) worked correctly; `%{localtime:<custom format>}` failed to parse in this ffmpeg build regardless of escaping attempts — stick to the argument-less form.

## Bottom line for the roadmap

Nothing here blocks Day 3. The pipeline works. Two follow-ups are queued, not blocking:
1. Re-measure latency with hls.js properly live-edge-tracking (should happen naturally once Day 3's live wall UI exists).
2. Re-verify hls.js playback and CORS on a real, non-sandboxed browser/device before Day 6.
