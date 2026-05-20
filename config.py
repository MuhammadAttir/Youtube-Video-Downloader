"""
Application Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask core
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production-please")
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

    # File paths
    DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
    TEMP_DIR = os.path.join(BASE_DIR, "temp")

    # Download limits
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 2 GB max upload size

    # Temp file TTL in seconds (auto-delete after 10 minutes)
    TEMP_FILE_TTL = 600

    # Rate limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "100 per day;30 per hour;5 per minute"

    # yt-dlp / ffmpeg
    FFMPEG_LOCATION = os.environ.get("FFMPEG_LOCATION", None)  # None = auto-detect
    COOKIES_FILE = os.environ.get("COOKIES_FILE", None)  # Optional cookies.txt path


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
