#!/usr/bin/env python3
"""
FILE LOCATION: /flask_backend/passenger_wsgi.py
SAVE AS: passenger_wsgi.py (in the flask_backend/ directory)

Dreamhost Passenger WSGI entry point for Flask backend
"""

import sys
import os
from pathlib import Path

# Add the flask_backend directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variables
os.environ.setdefault('FLASK_ENV', 'production')

try:
    # Import your Flask application
    from app import app as application
    
    # Configure for production
    application.config['DEBUG'] = False
    
    print("✅ Flask backend loaded successfully for Dreamhost")
    
except ImportError as e:
    print(f"❌ Failed to import Flask app: {e}")
    
    # Create a minimal error app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return {
            'error': 'Flask backend import failed',
            'message': str(e),
            'status': 'error'
        }
    
    @application.route('/api/health')
    def health_error():
        return {
            'status': 'error',
            'message': 'Flask backend not properly configured'
        }, 503

if __name__ == "__main__":
    application.run(debug=False)