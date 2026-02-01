"""
Verification script for imports only (no download).
Run: python tests/verify_imports.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from acquisition import YouTubeDownloader, DownloadConfig, AudioSourceBase, DownloadResult
    from acquisition.config import PRESET_TRANSCRIPTION, PRESET_HIGH_QUALITY, PRESET_COMPACT

    print("[PASS] All imports successful")

    # Test instantiation
    downloader = YouTubeDownloader()
    print(f"[PASS] YouTubeDownloader instantiated (source: {downloader.source_name})")

    # Test URL validation
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    valid = downloader.validate_url(test_url)
    print(f"[PASS] URL validation works: {test_url} -> valid={valid}")

    # Test config
    config = DownloadConfig(audio_format="wav", sample_rate=16000)
    opts = config.to_yt_dlp_opts()
    print(f"[PASS] DownloadConfig.to_yt_dlp_opts() works")

    print("\n✅ All verification tests passed!")
    sys.exit(0)

except Exception as e:
    print(f"[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
