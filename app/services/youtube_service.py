"""
YouTube Metadata Service
Fetches video info, formats, and thumbnails using yt-dlp.
"""
import logging
import yt_dlp

from app.utils.helpers import format_duration, format_filesize

logger = logging.getLogger(__name__)


def _base_ydl_opts(app_config: dict) -> dict:
    """Build base yt-dlp options from app config."""
    opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,  # Only download single video
    }
    if app_config.get("FFMPEG_LOCATION"):
        opts["ffmpeg_location"] = app_config["FFMPEG_LOCATION"]
    if app_config.get("COOKIES_FILE"):
        opts["cookiefile"] = app_config["COOKIES_FILE"]
    return opts


def get_video_info(url: str, app_config: dict) -> dict:
    """
    Fetch video metadata and available formats.
    Returns a dict with title, thumbnail, duration, formats_mp4, formats_mp3.
    """
    ydl_opts = _base_ydl_opts(app_config)
    ydl_opts["skip_download"] = True

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as e:
        logger.error(f"yt-dlp DownloadError for {url}: {e}")
        raise ValueError(f"Could not fetch video info: {str(e)[:200]}")
    except Exception as e:
        logger.error(f"Unexpected error fetching info for {url}: {e}")
        raise ValueError("Unexpected error while fetching video information.")

    # Available video qualities we support
    supported_heights = [144, 240, 360, 480, 720, 1080]
    formats_raw = info.get("formats", [])

    # Collect available MP4 qualities
    available_heights = set()
    for fmt in formats_raw:
        h = fmt.get("height")
        if h and fmt.get("vcodec") != "none":
            available_heights.add(h)

    # Map to our quality labels, only include available ones
    mp4_qualities = []
    for h in supported_heights:
        if any(ah >= h for ah in available_heights):
            mp4_qualities.append(f"{h}p")
    mp4_qualities.append("best")  # Always offer "best"

    # MP3 bitrate options (always available if ffmpeg is present)
    mp3_qualities = ["128kbps", "192kbps", "320kbps"]

    # Estimate best file size for display
    best_size = None
    for fmt in reversed(formats_raw):
        if fmt.get("filesize"):
            best_size = fmt["filesize"]
            break

    return {
        "title": info.get("title", "Unknown Title"),
        "thumbnail": info.get("thumbnail", ""),
        "duration": format_duration(info.get("duration")),
        "duration_raw": info.get("duration", 0),
        "uploader": info.get("uploader", "Unknown"),
        "view_count": info.get("view_count", 0),
        "upload_date": info.get("upload_date", ""),
        "description": (info.get("description") or "")[:200],
        "mp4_qualities": mp4_qualities,
        "mp3_qualities": mp3_qualities,
        "estimated_size": format_filesize(best_size) if best_size else "~Varies",
    }
