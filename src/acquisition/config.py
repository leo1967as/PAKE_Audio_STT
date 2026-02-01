"""
Configuration for audio downloads.
"""
from dataclasses import dataclass
from typing import Literal


@dataclass
class DownloadConfig:
    """Configuration for audio download settings."""

    # Audio format: wav for quality, mp3 for size
    audio_format: Literal["wav", "mp3", "m4a", "opus"] = "wav"

    # Audio quality (kbps for lossy formats)
    audio_quality: int = 192

    # Sample rate in Hz (None = keep original)
    sample_rate: int | None = 16000  # 16kHz is standard for speech processing

    # Mono or stereo
    mono: bool = True

    # Maximum duration in seconds (None = no limit)
    max_duration: float | None = None

    # Filename template (available: {title}, {id}, {uploader})
    filename_template: str = "{title}"

    # Whether to embed metadata
    embed_metadata: bool = True

    # Use cookies from browser to avoid 403 errors (chrome, firefox, edge, etc.)
    # Set to None to disable, or "chrome"/"edge"/"firefox" (browser must be closed)
    cookies_from_browser: str | None = None

    def to_yt_dlp_opts(self) -> dict:
        """Convert config to yt-dlp options dict."""
        postprocessor_args = []

        if self.sample_rate:
            postprocessor_args.extend(["-ar", str(self.sample_rate)])

        if self.mono:
            postprocessor_args.extend(["-ac", "1"])

        opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format,
                    "preferredquality": str(self.audio_quality),
                }
            ],
            "outtmpl": f"{self.filename_template}.%(ext)s",
            "quiet": True,
            "no_warnings": True,
            # Fix 403 errors
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            },
        }

        if self.cookies_from_browser:
            opts["cookiesfrombrowser"] = (self.cookies_from_browser,)

        if postprocessor_args:
            opts["postprocessor_args"] = {"ffmpeg": postprocessor_args}

        if self.embed_metadata:
            opts["postprocessors"].append({"key": "FFmpegMetadata"})

        return opts


# Preset configurations
PRESET_TRANSCRIPTION = DownloadConfig(
    audio_format="wav",
    sample_rate=16000,
    mono=True,
)

PRESET_HIGH_QUALITY = DownloadConfig(
    audio_format="wav",
    sample_rate=44100,
    mono=False,
)

PRESET_COMPACT = DownloadConfig(
    audio_format="mp3",
    audio_quality=128,
    sample_rate=16000,
    mono=True,
)
