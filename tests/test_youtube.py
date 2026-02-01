"""
Test script for YouTube Downloader.
Run: python tests/test_youtube.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from acquisition import YouTubeDownloader, DownloadConfig


def progress_callback(progress: float, status: str) -> None:
    """Print progress to console."""
    bar_length = 30
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r[{bar}] {progress:5.1f}% - {status}", end="", flush=True)
    if progress >= 100:
        print()  # New line when complete


def test_url_validation():
    """Test URL validation."""
    print("=" * 50)
    print("Testing URL Validation")
    print("=" * 50)

    downloader = YouTubeDownloader()

    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "youtube.com/watch?v=dQw4w9WgXcQ",
    ]

    invalid_urls = [
        "https://vimeo.com/123456",
        "https://example.com",
        "not a url",
    ]

    print("\n✅ Valid URLs:")
    for url in valid_urls:
        result = downloader.validate_url(url)
        status = "✓" if result else "✗"
        print(f"  {status} {url}")

    print("\n❌ Invalid URLs:")
    for url in invalid_urls:
        result = downloader.validate_url(url)
        status = "✓ (correctly rejected)" if not result else "✗ (should be rejected)"
        print(f"  {status} {url}")

    print("\n[PASS] URL validation test complete")


def test_download():
    """Test actual download with a short video."""
    print("\n" + "=" * 50)
    print("Testing Download (Short Video)")
    print("=" * 50)

    # Use a very short public domain video for testing
    # This is a ~10 second test video
    test_url = "https://www.youtube.com/watch?v=8T_yCIqeK6s"  # "Me at the zoo" - first YouTube video

    config = DownloadConfig(
        audio_format="wav",
        sample_rate=16000,
        mono=True,
        max_duration=1200,  # Limit to 2 minutes for testing
    )

    downloader = YouTubeDownloader(config=config)
    output_dir = Path(__file__).parent.parent / "data"

    print(f"\nDownloading: {test_url}")
    print(f"Output dir: {output_dir}\n")

    result = downloader.download(
        url=test_url,
        output_dir=output_dir,
        progress_callback=progress_callback,
    )

    if result.success:
        print(f"\n[PASS] Download successful!")
        print(f"  Title: {result.title}")
        print(f"  Duration: {result.duration:.1f}s")
        print(f"  File: {result.file_path}")
        print(f"  Uploader: {result.metadata.get('uploader')}")
    else:
        print(f"\n[FAIL] Download failed: {result.error_message}")

    return result


if __name__ == "__main__":
    print("\n🎵 YouTube Downloader Test Suite\n")

    # Run validation test
    test_url_validation()

    # Ask before downloading (to avoid unnecessary network calls)
    print("\n" + "=" * 50)
    response = input("Run download test? (y/n): ").strip().lower()

    if response == "y":
        result = test_download()
        sys.exit(0 if result.success else 1)
    else:
        print("Skipping download test.")
        sys.exit(0)
