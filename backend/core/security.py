"""
Security utilities.
This module handles:
- Authentication middleware
- Token validation
- Security headers
"""

from functools import wraps
from flask import request, abort
from supabase import create_client, Client
from core.config import settings

# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)

class Security:
    """Security utilities class."""
    
    @staticmethod
    def require_auth(f):
        """Decorator to require authentication."""
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                abort(401, "Missing or invalid authorization header")
            
            token = auth_header.split(" ")[1]
            try:
                auth = supabase.auth
                result = auth.get_user(token)
                if not result.user:
                    abort(401, "Invalid token")
                return f(*args, **kwargs)
            except Exception as e:
                abort(401, str(e))
        return decorated

    @staticmethod
    def get_user_id_from_token(token: str) -> str:
        """Get user ID from JWT token."""
        try:
            auth = supabase.auth
            result = auth.get_user(token)
            if not result.user:
                raise ValueError("Invalid token")
            return result.user.id
        except Exception as e:
            raise ValueError(f"Failed to get user ID from token: {str(e)}")

    @staticmethod
    def add_security_headers(response):
        """Add security headers to response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response 