# Spike: RTSP -> HLS -> browser playback, proven working end-to-end on 2026-09-04.
#
# Prereqs: ffmpeg on PATH, mediamtx.exe downloaded (see docs/SPIKE_HLS_RESULTS.md for
# the release URL) and its path set below.
#
# What this does:
#   1. Starts MediaMTX as a real RTSP server (localhost:8554) -- ffmpeg's own
#      "-rtsp_flags listen" server mode does NOT work reliably; see spike results.
#   2. Publishes a synthetic testsrc with a wall-clock burned into the frame,
#      as an RTSP *client*, into MediaMTX. Swap this for a real RTSP camera URL
#      once government feeds are available (this is the part that changes).
#   3. Pulls that RTSP stream back out and transcodes to HLS segments on disk.
#   4. Serves those segments via the FastAPI backend at /api/v1/media/spike/*.
#
# Run each block in its own terminal (or use Start-Process as below).

param(
    [string]$MediaMtxPath = "$PSScriptRoot\..\infra\mediamtx\mediamtx.exe",
    [string]$HlsOutDir    = "$PSScriptRoot\..\infra\hls_out",
    [string]$RtspUrl      = "rtsp://127.0.0.1:8554/spike"
)

if (-not (Test-Path $MediaMtxPath)) {
    Write-Error "MediaMTX not found at $MediaMtxPath. Download it first (see docs/SPIKE_HLS_RESULTS.md)."
    exit 1
}

New-Item -ItemType Directory -Force -Path $HlsOutDir | Out-Null
Get-ChildItem $HlsOutDir -File | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "Starting MediaMTX RTSP server..."
Start-Process -FilePath $MediaMtxPath -WorkingDirectory (Split-Path $MediaMtxPath) -WindowStyle Minimized

Start-Sleep -Seconds 2

Write-Host "Starting synthetic publisher (replace with a real camera RTSP URL later)..."
$publishArgs = @(
    "-hide_banner", "-loglevel", "warning",
    "-f", "lavfi", "-i", "testsrc=size=1280x720:rate=25",
    "-vf", "drawtext=fontfile='C\:/Windows/Fonts/arial.ttf':text='%{localtime}':fontcolor=white:fontsize=64:x=20:y=20:box=1:boxcolor=black@0.6",
    "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency", "-g", "25",
    "-f", "rtsp", "-rtsp_transport", "tcp", $RtspUrl
)
Start-Process -FilePath "ffmpeg" -ArgumentList $publishArgs -WindowStyle Minimized

Start-Sleep -Seconds 2

Write-Host "Starting RTSP -> HLS consumer..."
$m3u8Path = Join-Path $HlsOutDir "stream.m3u8"
$consumeArgs = @(
    "-hide_banner", "-loglevel", "warning",
    "-rtsp_transport", "tcp", "-i", $RtspUrl,
    "-c", "copy",
    "-f", "hls", "-hls_time", "1", "-hls_list_size", "5",
    "-hls_flags", "delete_segments+append_list",
    $m3u8Path
)
Start-Process -FilePath "ffmpeg" -ArgumentList $consumeArgs -WindowStyle Minimized

Write-Host "Done. Manifest will appear at: $m3u8Path"
Write-Host "Backend serves it at: http://localhost:8000/api/v1/media/spike/stream.m3u8"
Write-Host "Test page: frontend/public/spike-hls.html (npm run dev, then open /spike-hls.html)"
