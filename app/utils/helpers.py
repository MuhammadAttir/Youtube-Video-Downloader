"""
General helper utilities
"""
import re
import os
import unicodedata


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Sanitize a string to be safe as a filename.
    - Normalize unicode
    - Strip illegal characters
    - Truncate to max_length
    """
    # Normalize unicode characters
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")

    # Replace problematic chars with underscores
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r"\s+", "_", name.strip())

    # Remove leading/trailing dots/spaces
    name = name.strip(". ")

    # Fallback name
    if not name:
        name = "download"

    return name[:max_length]


def format_duration(seconds: int) -> str:
    """Convert seconds to HH:MM:SS or MM:SS string."""
    if not seconds:
        return "Unknown"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_filesize(size_bytes: int) -> str:
    """Human-readable file size."""
    if not size_bytes:
        return "Unknown"
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def quality_to_height(quality: str) -> int:
    """Map quality string like '720p' to pixel height integer."""
    mapping = {
        "144p": 144,
        "240p": 240,
        "360p": 360,
        "480p": 480,
        "720p": 720,
        "1080p": 1080,
        "best": 9999,
    }
    return mapping.get(quality, 720)


def bitrate_to_int(bitrate: str) -> int:
    """Map bitrate string like '320kbps' to integer kbps."""
    mapping = {
        "128kbps": 128,
        "192kbps": 192,
        "320kbps": 320,
        "best": 320,
    }
    return mapping.get(bitrate, 192)
