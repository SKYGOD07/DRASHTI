"""Feed ingestion adapters.

Every ingestion path implements the same small interface so a camera's real
protocol (RTSP today, ONVIF/vendor-SDK later) is swappable without touching
the AI pipeline, the API, or the frontend -- see docs/03_ARCHITECTURE.md and
docs/08_MODEL_MAPPING_HYBRID.md for why this seam exists (it's what lets us
honestly claim Model 3/4 extensibility without having built it).

DRASHTI_DEMO_MODE (see docs/05_ROADMAP_7DAY.md, "Demo Mode" section) swaps
every camera's adapter for a DemoClipAdapter that loops a local recorded
clip through the same RTSP-server-in, ffmpeg-out pipeline proven in
docs/SPIKE_HLS_RESULTS.md, instead of dialing a real camera. This is a
deliberate single point of control: on Sept 10-11, if a government feed's
codec/auth/network turns out to be a problem, flipping one env var falls
back to a fully self-contained demo with zero external dependencies.
"""
from __future__ import annotations

import abc
import subprocess
from pathlib import Path

from app.core.config import settings

REPO_ROOT = Path(__file__).resolve().parents[3]
DEMO_CLIPS_DIR = REPO_ROOT / "data" / "demo_clips"


class FeedAdapter(abc.ABC):
    """Common interface every ingestion path implements."""

    def __init__(self, camera_id: str, rtsp_publish_url: str) -> None:
        self.camera_id = camera_id
        self.rtsp_publish_url = rtsp_publish_url
        self._process: subprocess.Popen | None = None

    @abc.abstractmethod
    def start(self) -> None:
        """Begin publishing this camera's feed into the local RTSP hub
        (MediaMTX) at self.rtsp_publish_url, so the same HLS-transcode +
        frame-sampling pipeline downstream never needs to know which
        adapter produced the stream."""

    def stop(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
        self._process = None

    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None


class RTSPAdapter(FeedAdapter):
    """Pulls a real camera's RTSP stream and republishes it into the local
    RTSP hub. Real production path -- see docs/SPIKE_HLS_RESULTS.md Finding 1
    for why we go through a real RTSP server (MediaMTX) rather than trying to
    have ffmpeg act as its own server."""

    def __init__(self, camera_id: str, rtsp_publish_url: str, source_rtsp_url: str) -> None:
        super().__init__(camera_id, rtsp_publish_url)
        self.source_rtsp_url = source_rtsp_url

    def start(self) -> None:
        self._process = subprocess.Popen(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "warning",
                "-rtsp_transport", "tcp", "-i", self.source_rtsp_url,
                "-c", "copy",
                "-f", "rtsp", "-rtsp_transport", "tcp", self.rtsp_publish_url,
            ]
        )


class DemoClipAdapter(FeedAdapter):
    """Loops a local recorded clip as if it were a live camera, via the same
    RTSP-client-publish pattern as RTSPAdapter. Used when
    DRASHTI_DEMO_MODE=true, or per-camera as an explicit fallback."""

    def __init__(self, camera_id: str, rtsp_publish_url: str, clip_filename: str) -> None:
        super().__init__(camera_id, rtsp_publish_url)
        self.clip_path = DEMO_CLIPS_DIR / clip_filename

    def start(self) -> None:
        if not self.clip_path.is_file():
            raise FileNotFoundError(
                f"Demo clip not found: {self.clip_path}. "
                f"Drop a clip there or disable DRASHTI_DEMO_MODE for camera {self.camera_id}."
            )
        self._process = subprocess.Popen(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "warning",
                "-re", "-stream_loop", "-1", "-i", str(self.clip_path),
                "-c", "copy",
                "-f", "rtsp", "-rtsp_transport", "tcp", self.rtsp_publish_url,
            ]
        )


def make_adapter(camera_id: str, rtsp_publish_url: str, source_rtsp_url: str | None, demo_clip: str | None) -> FeedAdapter:
    """Single decision point for which adapter a camera gets -- this is the
    function DRASHTI_DEMO_MODE gates, so falling back to demo mode on the
    day of the event is a one-line/one-env-var change, not a scramble."""
    if settings.drashti_demo_mode or source_rtsp_url is None:
        if not demo_clip:
            raise ValueError(
                f"Camera {camera_id}: DRASHTI_DEMO_MODE is on but no demo_clip was "
                "provided for this camera. Every onboarded camera needs a fallback clip."
            )
        return DemoClipAdapter(camera_id, rtsp_publish_url, demo_clip)
    return RTSPAdapter(camera_id, rtsp_publish_url, source_rtsp_url)
