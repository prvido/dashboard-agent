"""
Simple authentication service using Supabase.
Handles user registration and login.
"""

from flask import abort
from supabase import create_client, Client
from core.config import settings

# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_API_KEY)

class AuthService:
    """Simple authentication service."""
    
    @staticmethod
    def register_user(user_data: dict) -> dict:
        """Register a new user."""
        required_fields = ["email", "password", "full_name"]
        if not all(field in user_data for field in required_fields):
            abort(400, f"Missing required fields: {', '.join(required_fields)}")
        try:
            # First sign up the user
            sign_up_result = supabase.auth.sign_up({
                "email": user_data["email"],
                "password": user_data["password"],
                "options": {
                    "data": {
                        "full_name": user_data["full_name"]
                    }
                }
            })
            
            if not sign_up_result or not sign_up_result.user:
                abort(400, "Failed to create user")
            
            # Then sign in the user to get the session
            sign_in_result = supabase.auth.sign_in_with_password({
                "email": user_data["email"],
                "password": user_data["password"]
            })
            
            return {
                "user": sign_up_result.user.model_dump(),
                "access_token": sign_in_result.session.access_token,
                "token_type": "bearer"
            }
        except Exception as e:
            abort(400, f"Registration error: {str(e)}")

    @staticmethod
    def login_user(email: str, password: str) -> dict:
        """Login user and return tokens."""
        try:
            result = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            return {
                "access_token": result.session.access_token,
                "token_type": "bearer",
                "user": result.user.model_dump()
            }
        except Exception as e:
            if "Invalid login credentials" in str(e):
                abort(401, "Invalid email or password")
            abort(400, str(e))

    @staticmethod
    def get_current_user(token: str) -> dict:
        """Get current user from token."""
        try:
            result = supabase.auth.get_user(token)
            if not result.user:
                abort(401, "Invalid token")
            user_data = result.user.model_dump()
            return user_data
        except Exception as e:
            print(f"Error getting current user: {str(e)}")
            abort(401, str(e)) 