"""
Downloader Service
Handles MP4 video and MP3 audio downloads via yt-dlp + FFmpeg.
"""
import os
import uuid
import shutil
import logging
import yt_dlp

from app.utils.helpers import sanitize_filename, quality_to_height, bitrate_to_int

logger = logging.getLogger(__name__)


def _ffmpeg_available(ffmpeg_location: str = None) -> bool:
    """Check if FFmpeg is accessible."""
    ffmpeg_path = ffmpeg_location or shutil.which("ffmpeg")
    return ffmpeg_path is not None


def download_mp4(url: str, quality: str, temp_dir: str, app_config: dict) -> dict:
    """
    Download a YouTube video as MP4.

    Args:
        url: YouTube URL
        quality: e.g. '720p', '1080p', 'best'
        temp_dir: directory to save file
        app_config: Flask app config dict

    Returns:
        dict with 'filepath' and 'filename'
    """
    # Unique output filename to avoid collisions
    uid = uuid.uuid4().hex[:8]
    output_template = os.path.join(temp_dir, f"%(title)s_{uid}.%(ext)s")

    height = quality_to_height(quality)

    if height == 9999:
        # Best available quality
        format_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
    else:
        # Specific height, fall back to nearest lower quality
        format_str = (
            f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
        )

    ydl_opts = {
        "format": format_str,
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "merge_output_format": "mp4",
        "postprocessors": [],
    }

    # Add FFmpeg location if configured
    if app_config.get("FFMPEG_LOCATION"):
        ydl_opts["ffmpeg_location"] = app_config["FFMPEG_LOCATION"]
    if app_config.get("COOKIES_FILE"):
        ydl_opts["cookiefile"] = app_config["COOKIES_FILE"]

    # If FFmpeg is not available, fall back to single-file download
    if not _ffmpeg_available(app_config.get("FFMPEG_LOCATION")):
        logger.warning("FFmpeg not found. Falling back to single-file MP4 download.")
        ydl_opts["format"] = f"best[height<={height}][ext=mp4]/best[ext=mp4]/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Get the actual output filepath
            filepath = ydl.prepare_filename(info)

            # Handle merged output (might have changed extension)
            if not os.path.exists(filepath):
                # Search for file with our unique suffix
                for f in os.listdir(temp_dir):
                    if uid in f:
                        filepath = os.path.join(temp_dir, f)
                        break

        if not os.path.exists(filepath):
            raise FileNotFoundError("Downloaded file not found on disk.")

        title = info.get("title", "video")
        safe_name = sanitize_filename(title)
        final_filename = f"{safe_name}.mp4"

        return {"filepath": filepath, "filename": final_filename}

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"MP4 download error: {e}")
        raise ValueError(f"Download failed: {str(e)[:300]}")
    except Exception as e:
        logger.error(f"Unexpected MP4 download error: {e}")
        raise


def download_mp3(url: str, bitrate: str, temp_dir: str, app_config: dict) -> dict:
    """
    Download a YouTube video as MP3 audio.

    Args:
        url: YouTube URL
        bitrate: e.g. '192kbps', '320kbps'
        temp_dir: directory to save file
        app_config: Flask app config dict

    Returns:
        dict with 'filepath' and 'filename'
    """
    if not _ffmpeg_available(app_config.get("FFMPEG_LOCATION")):
        raise EnvironmentError(
            "FFmpeg is required for MP3 conversion but was not found. "
            "Please install FFmpeg and restart the server."
        )

    uid = uuid.uuid4().hex[:8]
    output_template = os.path.join(temp_dir, f"%(title)s_{uid}.%(ext)s")
    kbps = bitrate_to_int(bitrate)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": str(kbps),
            }
        ],
    }

    if app_config.get("FFMPEG_LOCATION"):
        ydl_opts["ffmpeg_location"] = app_config["FFMPEG_LOCATION"]
    if app_config.get("COOKIES_FILE"):
        ydl_opts["cookiefile"] = app_config["COOKIES_FILE"]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "audio")

        # Find the .mp3 file (post-processed)
        mp3_file = None
        for f in os.listdir(temp_dir):
            if uid in f and f.endswith(".mp3"):
                mp3_file = os.path.join(temp_dir, f)
                break

        if not mp3_file or not os.path.exists(mp3_file):
            raise FileNotFoundError("MP3 file not found after conversion.")

        safe_name = sanitize_filename(title)
        final_filename = f"{safe_name}.mp3"

        return {"filepath": mp3_file, "filename": final_filename}

    except yt_dlp.utils.DownloadError as e:
        logger.error(f"MP3 download error: {e}")
        raise ValueError(f"Download failed: {str(e)[:300]}")
    except Exception as e:
        logger.error(f"Unexpected MP3 download error: {e}")
        raise
