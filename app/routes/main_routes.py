"""
Main Routes Blueprint
Serves the frontend pages.
"""
from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Render the main download page."""
    return render_template("index.html")


@main_bp.app_errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404


@main_bp.app_errorhandler(429)
def rate_limited(e):
    from flask import jsonify
    return jsonify({"error": "Too many requests. Please slow down."}), 429
