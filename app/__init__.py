"""
YouTube Downloader Flask Application Factory
"""
import os
import logging
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global rate limiter instance
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


def create_app(config_object="config.Config"):
    """Application factory pattern."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Load config
    app.config.from_object(config_object)

    # Ensure required directories exist
    os.makedirs(app.config.get("DOWNLOADS_DIR", "downloads"), exist_ok=True)
    os.makedirs(app.config.get("TEMP_DIR", "temp"), exist_ok=True)

    # Initialize extensions
    limiter.init_app(app)

    # Register blueprints
    from app.routes.main_routes import main_bp
    from app.routes.download_routes import download_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(download_bp, url_prefix="/api")

    logger.info("Application initialized successfully.")
    return app
