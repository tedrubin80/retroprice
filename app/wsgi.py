# ================================================================
# SAVE AS: wsgi.py (in your ROOT directory, not backend/)
# Film Price Guide - Fixed WSGI Entry Point for Railway
# ================================================================

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Import the application
try:
    from app import create_app
    application = create_app()
    
    # Configure for production
    application.config['DEBUG'] = False
    print("✅ Flask application loaded successfully")
    
except ImportError as e:
    print(f"❌ Failed to import Flask app: {e}")
    # Create minimal fallback app
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def error():
        return {'error': 'Flask import failed', 'message': str(e)}, 500

# For Railway deployment
app = application

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port)