#!/usr/bin/env bash
# Spike: RTSP -> HLS -> browser playback. See scripts/spike_hls.ps1 for the
# Windows-native version (this session ran everything through Git Bash calling
# the same Windows ffmpeg/mediamtx binaries -- both are equally valid on Windows).
#
# Prereqs: ffmpeg on PATH, mediamtx binary downloaded to infra/mediamtx/mediamtx
# (or .exe on Windows) -- see docs/SPIKE_HLS_RESULTS.md for the release URL and
# why a real RTSP server binary is required instead of ffmpeg's own listen mode.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MEDIAMTX="${MEDIAMTX_PATH:-$REPO_ROOT/infra/mediamtx/mediamtx.exe}"
HLS_OUT="$REPO_ROOT/infra/hls_out"
RTSP_URL="rtsp://127.0.0.1:8554/spike"

if [ ! -f "$MEDIAMTX" ]; then
  echo "MediaMTX not found at $MEDIAMTX. Download it first (see docs/SPIKE_HLS_RESULTS.md)." >&2
  exit 1
fi

rm -rf "$HLS_OUT" && mkdir -p "$HLS_OUT"

echo "Starting MediaMTX RTSP server..."
"$MEDIAMTX" "$(dirname "$MEDIAMTX")/mediamtx.yml" &
MEDIAMTX_PID=$!
sleep 2

echo "Starting synthetic publisher (swap for a real camera RTSP URL later)..."
ffmpeg -hide_banner -loglevel warning \
  -f lavfi -i "testsrc=size=1280x720:rate=25" \
  -vf "drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='%{localtime}':fontcolor=white:fontsize=64:x=20:y=20:box=1:boxcolor=black@0.6" \
  -c:v libx264 -preset ultrafast -tune zerolatency -g 25 \
  -f rtsp -rtsp_transport tcp "$RTSP_URL" &
PUBLISH_PID=$!
sleep 2

echo "Starting RTSP -> HLS consumer..."
ffmpeg -hide_banner -loglevel warning \
  -rtsp_transport tcp -i "$RTSP_URL" \
  -c copy \
  -f hls -hls_time 1 -hls_list_size 5 -hls_flags delete_segments+append_list \
  "$HLS_OUT/stream.m3u8" &
CONSUME_PID=$!

echo "Manifest: $HLS_OUT/stream.m3u8"
echo "Backend serves it at: http://localhost:8000/api/v1/media/spike/stream.m3u8"
echo "PIDs: mediamtx=$MEDIAMTX_PID publisher=$PUBLISH_PID consumer=$CONSUME_PID"
echo "Ctrl+C or 'kill $MEDIAMTX_PID $PUBLISH_PID $CONSUME_PID' to stop."
wait
