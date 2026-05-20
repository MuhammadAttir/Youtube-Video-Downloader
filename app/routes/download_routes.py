"""
Download API Routes Blueprint
Handles /api/info and /api/download endpoints.
"""
import os
import logging
from flask import Blueprint, request, jsonify, send_file, current_app

from app import limiter
from app.services.youtube_service import get_video_info
from app.services.downloader import download_mp4, download_mp3
from app.utils.validators import is_valid_youtube_url, is_valid_format, is_valid_quality
from app.utils.cleanup import cleanup_old_files, delete_file_after_delay

logger = logging.getLogger(__name__)
download_bp = Blueprint("download", __name__)


@download_bp.route("/info", methods=["POST"])
@limiter.limit("20 per minute")
def fetch_info():
    """
    Fetch video metadata and available formats.
    Body: { "url": "https://youtube.com/..." }
    Returns: video info + quality options JSON
    """
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "URL is required."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid or unsupported YouTube URL."}), 400

    try:
        info = get_video_info(url, current_app.config)
        return jsonify({"success": True, "data": info})
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        logger.exception("Unexpected error in /api/info")
        return jsonify({"error": "Failed to fetch video information. Try again later."}), 500


@download_bp.route("/download", methods=["POST"])
@limiter.limit("10 per minute")
def download():
    """
    Download video or audio.
    Body: { "url": "...", "format": "mp4|mp3", "quality": "720p|192kbps|..." }
    Returns: File response (browser download)
    """
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    fmt = (data.get("format") or "").strip().lower()
    quality = (data.get("quality") or "best").strip().lower()

    # --- Input validation ---
    if not url:
        return jsonify({"error": "URL is required."}), 400
    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400
    if not is_valid_format(fmt):
        return jsonify({"error": "Format must be 'mp4' or 'mp3'."}), 400
    if not is_valid_quality(quality):
        return jsonify({"error": "Invalid quality selection."}), 400

    temp_dir = current_app.config["TEMP_DIR"]

    # Clean up old temp files before starting
    cleanup_old_files(temp_dir, max_age_seconds=current_app.config.get("TEMP_FILE_TTL", 600))

    try:
        if fmt == "mp4":
            result = download_mp4(url, quality, temp_dir, current_app.config)
        else:
            result = download_mp3(url, quality, temp_dir, current_app.config)

        filepath = result["filepath"]
        filename = result["filename"]

        if not os.path.exists(filepath):
            return jsonify({"error": "Download failed: file not found."}), 500

        # Schedule auto-deletion after 3 minutes (enough time for browser transfer)
        delete_file_after_delay(filepath, delay=180)

        logger.info(f"Serving download: {filename} ({fmt}, {quality})")

        # Send file with proper headers for browser download
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype="video/mp4" if fmt == "mp4" else "audio/mpeg",
        )

    except EnvironmentError as e:
        # FFmpeg missing, etc.
        return jsonify({"error": str(e)}), 503
    except ValueError as e:
        return jsonify({"error": str(e)}), 422
    except Exception as e:
        logger.exception("Unexpected error in /api/download")
        return jsonify({"error": "Download failed. Please try again."}), 500
