"""
YouTube audio downloader using yt-dlp.
"""
import re
from pathlib import Path
from typing import Callable, Optional

import yt_dlp

from .base import AudioSourceBase, DownloadResult
from .config import DownloadConfig, PRESET_TRANSCRIPTION


class YouTubeDownloader(AudioSourceBase):
    """
    Download audio from YouTube videos using yt-dlp.

    Example:
        >>> downloader = YouTubeDownloader()
        >>> result = downloader.download(
        ...     "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        ...     Path("./data")
        ... )
        >>> print(result.file_path)
    """

    # Regex patterns for YouTube URLs
    YOUTUBE_PATTERNS = [
        r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
        r"(?:https?://)?(?:www\.)?youtube\.com/live/([a-zA-Z0-9_-]{11})",
    ]

    def __init__(self, config: DownloadConfig | None = None):
        """
        Initialize YouTube downloader.

        Args:
            config: Download configuration. Defaults to PRESET_TRANSCRIPTION.
        """
        self.config = config or PRESET_TRANSCRIPTION
        self._progress_callback: Optional[Callable[[float, str], None]] = None

    @property
    def source_name(self) -> str:
        return "YouTube"

    def validate_url(self, url: str) -> bool:
        """Check if URL is a valid YouTube video URL."""
        return any(re.match(pattern, url) for pattern in self.YOUTUBE_PATTERNS)

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL."""
        for pattern in self.YOUTUBE_PATTERNS:
            match = re.match(pattern, url)
            if match:
                return match.group(1)
        return None

    def download(
        self,
        url: str,
        output_dir: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> DownloadResult:
        """
        Download audio from a YouTube video.

        Args:
            url: YouTube video URL
            output_dir: Directory to save the audio file
            progress_callback: Optional callback(progress: 0-100, status: str)

        Returns:
            DownloadResult with file path and metadata
        """
        self._progress_callback = progress_callback

        # Validate URL
        if not self.validate_url(url):
            return DownloadResult(
                success=False,
                source_url=url,
                error_message=f"Invalid YouTube URL: {url}",
            )

        # Ensure output directory exists
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build yt-dlp options
        ydl_opts = self.config.to_yt_dlp_opts()
        ydl_opts["outtmpl"] = str(output_dir / ydl_opts["outtmpl"])
        ydl_opts["progress_hooks"] = [self._progress_hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                self._report_progress(0, "Extracting video info...")
                info = ydl.extract_info(url, download=False)

                if info is None:
                    return DownloadResult(
                        success=False,
                        source_url=url,
                        error_message="Failed to extract video info",
                    )

                # Check duration limit
                duration = info.get("duration", 0)
                if self.config.max_duration and duration > self.config.max_duration:
                    return DownloadResult(
                        success=False,
                        source_url=url,
                        error_message=f"Video duration ({duration}s) exceeds limit ({self.config.max_duration}s)",
                    )

                # Download
                self._report_progress(5, "Downloading audio...")
                ydl.download([url])

                # Find the downloaded file
                title = info.get("title", "unknown")
                safe_title = ydl.prepare_filename(info).rsplit(".", 1)[0]
                expected_path = Path(f"{safe_title}.{self.config.audio_format}")

                if not expected_path.exists():
                    # Try to find the file by pattern
                    possible_files = list(
                        output_dir.glob(f"*.{self.config.audio_format}")
                    )
                    if possible_files:
                        expected_path = max(possible_files, key=lambda p: p.stat().st_mtime)
                    else:
                        return DownloadResult(
                            success=False,
                            source_url=url,
                            error_message="Downloaded file not found",
                        )

                self._report_progress(100, "Download complete!")

                return DownloadResult(
                    success=True,
                    file_path=expected_path,
                    title=title,
                    duration=duration,
                    source_url=url,
                    metadata={
                        "video_id": info.get("id"),
                        "uploader": info.get("uploader"),
                        "upload_date": info.get("upload_date"),
                        "view_count": info.get("view_count"),
                        "description": info.get("description", "")[:500],
                    },
                )

        except yt_dlp.utils.DownloadError as e:
            return DownloadResult(
                success=False,
                source_url=url,
                error_message=f"Download error: {str(e)}",
            )
        except Exception as e:
            return DownloadResult(
                success=False,
                source_url=url,
                error_message=f"Unexpected error: {str(e)}",
            )

    def _progress_hook(self, d: dict) -> None:
        """yt-dlp progress hook."""
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                progress = 5 + (downloaded / total) * 85  # 5-90%
                speed = d.get("speed", 0) or 0
                speed_str = f"{speed / 1024 / 1024:.1f} MB/s" if speed else "..."
                self._report_progress(progress, f"Downloading... {speed_str}")

        elif d["status"] == "finished":
            self._report_progress(90, "Converting audio...")

    def _report_progress(self, progress: float, status: str) -> None:
        """Report progress to callback if set."""
        if self._progress_callback:
            self._progress_callback(progress, status)
