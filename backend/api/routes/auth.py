"""
Authentication routes and endpoints.
This module handles:
- User registration
- User login
- User information retrieval
"""

from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from core.security import Security
from core.config import settings

# Create blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.get_json()
    if not data or not all(k in data for k in ["email", "password", "full_name"]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if email is pre-authorized
    if settings.PRE_AUTHORIZED_EMAILS and data["email"] not in settings.PRE_AUTHORIZED_EMAILS:
        return jsonify({"error": "This email is not authorized to register"}), 403
    
    user = AuthService.register_user(data)
    return jsonify(user), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    """Login user and return tokens."""
    data = request.get_json()
    if not data or not all(k in data for k in ["email", "password"]):
        return jsonify({"error": "Missing email or password"}), 400
    
    result = AuthService.login_user(data["email"], data["password"])
    return jsonify(result)

@auth_bp.route("/me", methods=["GET"])
@Security.require_auth
def get_me():
    """Get current user info."""
    token = request.headers.get("Authorization").split(" ")[1]
    user = AuthService.get_current_user(token)
    return jsonify(user) 