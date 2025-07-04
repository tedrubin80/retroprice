# ================================================================
# SAVE AS: backend/app.py (REPLACE your current one)
# Film Price Guide - Complete Flask App with All Blueprints
# ================================================================

import os
import logging
from flask import Flask, jsonify, request, session
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this')
app.config['DEBUG'] = os.environ.get('FLASK_ENV') == 'development'

# Register blueprints with error handling
try:
    from endpoints.ebay_api import ebay_bp
    app.register_blueprint(ebay_bp)
    logger.info("✅ Registered eBay API blueprint")
except ImportError as e:
    logger.warning("⚠️ eBay API blueprint not found")

try:
    from endpoints.ebay_deletion import ebay_deletion_bp
    app.register_blueprint(ebay_deletion_bp)
    logger.info("✅ Registered eBay deletion blueprint")
except ImportError as e:
    logger.warning("⚠️ eBay deletion blueprint not found")

try:
    from endpoints.auth import auth_bp
    app.register_blueprint(auth_bp)
    logger.info("✅ Registered Authentication blueprint")
except ImportError as e:
    logger.warning("⚠️ Authentication blueprint not found")

# Try to register admin blueprint if it exists
try:
    from endpoints.admin_api import admin_bp
    app.register_blueprint(admin_bp)
    logger.info("✅ Registered Admin API blueprint")
except ImportError as e:
    logger.warning("⚠️ Admin API blueprint not found")

# Main routes
@app.route('/')
def index():
    """Main API endpoint"""
    return jsonify({
        'message': 'Film Price Guide API',
        'status': 'running',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'search': '/api/search',
            'ebay': '/api/ebay/search',
            'auth': '/api/auth/login',
            'admin': '/api/admin'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'service': 'Film Price Guide Backend',
        'environment': os.environ.get('FLASK_ENV', 'production'),
        'railway': bool(os.environ.get('RAILWAY_ENVIRONMENT'))
    })

@app.route('/api/search')
def search_movies():
    """General movie search endpoint"""
    query = request.args.get('q', '')
    format_type = request.args.get('format', 'all')  # vhs, dvd, bluray, all
    
    return jsonify({
        'query': query,
        'format': format_type,
        'results': [],
        'message': 'Search functionality ready - integrate with eBay/OMDb APIs',
        'total_results': 0
    })

@app.route('/api/status')
def api_status():
    """API configuration status"""
    return jsonify({
        'ebay_configured': bool(os.environ.get('EBAY_APP_ID')),
        'database_configured': bool(os.environ.get('DATABASE_URL')),
        'omdb_configured': bool(os.environ.get('OMDB_API_KEY')),
        'tmdb_configured': bool(os.environ.get('TMDB_API_KEY')),
        'environment': os.environ.get('FLASK_ENV', 'production')
    })

@app.route('/api/config')
def get_config():
    """Get public configuration info"""
    return jsonify({
        'app_name': 'Film Price Guide',
        'version': '1.0.0',
        'supported_formats': ['VHS', 'DVD', 'Blu-ray', 'Digital'],
        'api_endpoints': [
            '/api/search',
            '/api/ebay/search',
            '/api/auth/login',
            '/health'
        ]
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'available_endpoints': ['/health', '/api/search', '/api/ebay/search']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

# Create app function for factory pattern
def create_app():
    """Application factory function"""
    return app

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Film Price Guide on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)