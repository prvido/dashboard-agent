"""
Main application module.
This module:
- Creates the Flask application
- Registers blueprints
- Configures middleware
- Sets up error handlers
"""

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from api.routes.auth import auth_bp
from api.routes.warehouses import warehouses_bp
from api.routes.datasets import datasets_bp
from api.routes.chats import chats_bp
from api.routes.tools import tools_bp
from api.routes.exports import exports_bp
from core.security import Security
from core.config import settings

# Load environment variables
load_dotenv()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure CORS with more specific settings
    CORS(app, 
         resources={
             r"/*": {
                 "origins": ["http://localhost:5173", "http://localhost:3000"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True,
                 "max_age": 3600
             }
         })

    # Add security headers middleware
    app.after_request(Security.add_security_headers)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(warehouses_bp)
    app.register_blueprint(datasets_bp)
    app.register_blueprint(chats_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(exports_bp)
    
    # Health check endpoint
    @app.route("/api/health")
    def health():
        return {"status": "ok"}
    
    return app

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app = create_app()
    app.run(host='0.0.0.0', port=port, debug=True) 