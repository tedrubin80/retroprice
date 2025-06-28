#!/usr/bin/env python3
"""
Film Price Guide - WSGI Entry Point
Production entry point for deployment platforms
"""

import os
import sys
import logging

# Add the backend directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

try:
    # Import the Flask application
    from app import app
    
    # Configure for production if not already set
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'production'
    
    # Ensure required directories exist
    os.makedirs('logs', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    
    # Application factory pattern (if needed)
    application = app
    
    if __name__ == "__main__":
        # This allows the WSGI file to be run directly for testing
        port = int(os.environ.get("PORT", 8080))
        host = os.environ.get("HOST", "0.0.0.0")
        
        print(f"🚀 Starting Film Price Guide on {host}:{port}")
        app.run(host=host, port=port, debug=False)

except ImportError as e:
    # Fallback if main app can't be imported
    logging.error(f"Failed to import main application: {e}")
    
    # Create a minimal Flask app for error reporting
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    
    @app.route('/')
    def error_page():
        return jsonify({
            'error': 'Application startup failed',
            'message': 'Please check server logs for details',
            'status': 'error'
        }), 500
    
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'error',
            'message': 'Application not properly configured'
        }), 503
    
    application = app

except Exception as e:
    logging.error(f"Unexpected error during startup: {e}")
    raise