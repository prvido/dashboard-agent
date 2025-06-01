"""
Common validation utilities for services.
This module contains shared validation functions and constants used across different services.
"""

# Common constants
MAX_NAME_LENGTH = 255
BUCKET_NAME = "uploads"
STORAGE_PATH = "warehouses"

def validate_user_id(user_id: str) -> None:
    """Validate user_id is not empty."""
    if not user_id:
        raise ValueError("User ID cannot be empty")

def validate_warehouse_id(warehouse_id: str) -> None:
    """Validate warehouse_id is not empty."""
    if not warehouse_id:
        raise ValueError("Warehouse ID cannot be empty")

def validate_agent_id(agent_id: str) -> None:
    """Validate agent_id is not empty."""
    if not agent_id:
        raise ValueError("Agent ID cannot be empty")

def validate_name(name: str, entity_type: str = "entity") -> None:
    """
    Validate name is not empty and within length limits.
    
    Args:
        name: The name to validate
        entity_type: The type of entity (e.g., "warehouse", "dataset") for error messages
    """
    if not name:
        raise ValueError(f"{entity_type.capitalize()} name cannot be empty")
    if len(name) > MAX_NAME_LENGTH:
        raise ValueError(f"{entity_type.capitalize()} name cannot exceed {MAX_NAME_LENGTH} characters")

def validate_bucket_exists(supabase_client) -> None:
    """Validate that the storage bucket exists and is accessible."""
    try:
        supabase_client.storage.from_(BUCKET_NAME).list()
    except Exception:
        raise ValueError(f"Storage bucket '{BUCKET_NAME}' does not exist or is not accessible") 