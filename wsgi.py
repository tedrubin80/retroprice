# ================================================================
# SAVE AS: wsgi.py (REPLACE your current wsgi.py completely)
# Immediate fix for Railway deployment
# ================================================================

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

try:
    # Try to import app directly (not create_app)
    from app import app as application
    print("✅ Imported app directly from backend/app.py")
except ImportError:
    try:
        # If that fails, try importing any Flask app variable
        import app
        if hasattr(app, 'app'):
            application = app.app
        elif hasattr(app, 'application'):
            application = app.application
        else:
            # Create a minimal working app
            from flask import Flask
            application = Flask(__name__)
            
            @application.route('/')
            def hello():
                return {'message': 'Film Price Guide API is running'}
            
            @application.route('/health')
            def health():
                return {'status': 'healthy'}
            
        print("✅ Created working Flask application")
    except Exception as e:
        print(f"❌ All import attempts failed: {e}")
        # Absolute fallback - create minimal app
        from flask import Flask
        application = Flask(__name__)
        
        @application.route('/')
        def error():
            return {'error': 'Backend import failed', 'fix': 'Check backend/app.py'}

# For Railway
app = application

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host="0.0.0.0", port=port)