"""
Logging configuration and utilities.
This module handles:
- Logging setup and configuration
- Custom log formatters
- Log levels and handlers
- Request logging middleware
- Error tracking and reporting
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime
from flask import request, g

from core.config import settings

class CustomFormatter(logging.Formatter):
    """Custom log formatter with colors and detailed information."""
    
    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt: str):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logging(app) -> None:
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not log_dir.exists():
        log_dir.mkdir(parents=True)

    # Set up file handler
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(CustomFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(CustomFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Configure Flask logger
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

def log_request_info() -> None:
    """Log information about incoming requests."""
    logger = logging.getLogger("request")
    timestamp = datetime.now().isoformat()
    
    # Get request details
    method = request.method
    path = request.path
    ip = request.remote_addr
    user_agent = request.user_agent.string
    
    # Get user info if authenticated
    user_id = getattr(g, "user", {}).get("user_id", "anonymous")
    
    # Log the request
    logger.info(
        f"Request: {method} {path} | "
        f"IP: {ip} | "
        f"User: {user_id} | "
        f"Agent: {user_agent} | "
        f"Time: {timestamp}"
    )

def log_error(error: Exception, context: Optional[str] = None) -> None:
    """Log error with context."""
    logger = logging.getLogger("error")
    logger.error(
        f"Error: {str(error)} | "
        f"Context: {context} | "
        f"Type: {type(error).__name__}",
        exc_info=True
    )

# Request logging middleware
def log_requests(app) -> None:
    """Add request logging middleware to the app."""
    @app.before_request
    def before_request():
        log_request_info()

    @app.after_request
    def after_request(response):
        # Log response status
        logger = logging.getLogger("response")
        logger.info(f"Response: {response.status}")
        return response 