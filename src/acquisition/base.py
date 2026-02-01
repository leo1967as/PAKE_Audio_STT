"""
Base classes for Audio Acquisition module.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime


@dataclass
class DownloadResult:
    """Result of an audio download operation."""
    success: bool
    file_path: Optional[Path] = None
    title: Optional[str] = None
    duration: Optional[float] = None  # seconds
    source_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    downloaded_at: datetime = field(default_factory=datetime.now)

    def __repr__(self) -> str:
        if self.success:
            return f"DownloadResult(success=True, title='{self.title}', duration={self.duration:.1f}s)"
        return f"DownloadResult(success=False, error='{self.error_message}')"


class AudioSourceBase(ABC):
    """
    Abstract base class for audio sources.
    Extend this to add new sources (YouTube, SoundCloud, local files, etc.)
    """

    @abstractmethod
    def download(
        self,
        url: str,
        output_dir: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> DownloadResult:
        """
        Download audio from the source.

        Args:
            url: Source URL or identifier
            output_dir: Directory to save the audio file
            progress_callback: Optional callback(progress: 0-100, status: str)

        Returns:
            DownloadResult with file path and metadata
        """
        pass

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """Check if the URL is valid for this source."""
        pass

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Human-readable name of the source (e.g., 'YouTube')."""
        pass
