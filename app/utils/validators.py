"""
Input validation utilities
"""
import re
from urllib.parse import urlparse


# Regex patterns for YouTube URLs
YOUTUBE_PATTERNS = [
    r"^(https?://)?(www\.)?(youtube\.com/watch\?v=)[a-zA-Z0-9_-]{11}",
    r"^(https?://)?(www\.)?(youtu\.be/)[a-zA-Z0-9_-]{11}",
    r"^(https?://)?(www\.)?(youtube\.com/shorts/)[a-zA-Z0-9_-]{11}",
    r"^(https?://)?(www\.)?(youtube\.com/embed/)[a-zA-Z0-9_-]{11}",
    r"^(https?://)?(www\.)?(m\.youtube\.com/watch\?v=)[a-zA-Z0-9_-]{11}",
]


def is_valid_youtube_url(url: str) -> bool:
    """Return True if URL is a recognized YouTube URL."""
    if not url or not isinstance(url, str):
        return False

    url = url.strip()

    # Basic URL structure check
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https", ""):
            return False
    except Exception:
        return False

    # Match against known patterns
    for pattern in YOUTUBE_PATTERNS:
        if re.search(pattern, url, re.IGNORECASE):
            return True

    return False


def is_valid_format(fmt: str) -> bool:
    """Validate requested format (mp4 or mp3)."""
    return fmt in ("mp4", "mp3")


def is_valid_quality(quality: str) -> bool:
    """Validate quality string."""
    valid_video = {"144p", "240p", "360p", "480p", "720p", "1080p", "best"}
    valid_audio = {"128kbps", "192kbps", "320kbps", "best"}
    return quality in valid_video | valid_audio
