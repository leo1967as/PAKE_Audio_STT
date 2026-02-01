# Audio Acquisition Module
from .youtube import YouTubeDownloader
from .config import DownloadConfig
from .base import AudioSourceBase, DownloadResult

__all__ = ["YouTubeDownloader", "DownloadConfig", "AudioSourceBase", "DownloadResult"]
