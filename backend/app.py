#!/usr/bin/env python3
"""
Film Price Guide - Main Flask Application
Multi-API search engine for VHS, DVD, and Graded Movies
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
from werkzeug.exceptions import NotFound

# Initialize Flask app
app = Flask(__name__, 
           static_folder='../frontend',
           static_url_path='/static')

# Basic configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'mysql://root:password@localhost/film_price_guide')
app.config['EBAY_APP_ID'] = os.environ.get('EBAY_APP_ID')
app.config['EBAY_CERT_ID'] = os.environ.get('EBAY_CERT_ID')
app.config['EBAY_DEV_ID'] = os.environ.get('EBAY_DEV_ID')

# Initialize CORS
CORS(app, origins=[
    'http://localhost:3000',
    'http://localhost:5000', 
    'https://yourdomain.com',
    'https://*.dreamhost.com',
    'https://*.github.io'
])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import and register blueprints (graceful degradation)
try:
    from endpoints.ebay_api import ebay_bp
    app.register_blueprint(ebay_bp)
    logger.info("✅ Registered eBay API blueprint")
except ImportError:
    logger.warning("⚠️ eBay API blueprint not found")

try:
    from endpoints.ebay_deletion import deletion_bp
    app.register_blueprint(deletion_bp)
    logger.info("✅ Registered eBay deletion compliance blueprint")
except ImportError:
    logger.warning("⚠️ eBay deletion blueprint not found")

try:
    from endpoints.admin_api import admin_bp
    app.register_blueprint(admin_bp)
    logger.info("✅ Registered Admin API blueprint")
except ImportError:
    logger.warning("⚠️ Admin API blueprint not found")

try:
    from endpoints.auth_api import auth_bp
    app.register_blueprint(auth_bp)
    logger.info("✅ Registered Authentication blueprint")
except ImportError:
    logger.warning("⚠️ Authentication blueprint not found")

# ================================
# FRONTEND ROUTES
# ================================

@app.route('/')
def index():
    """Serve the homepage"""
    try:
        return send_from_directory('../frontend', 'index.html')
    except NotFound:
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Film Price Guide</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
                .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
            </style>
        </head>
        <body>
            <h1>🎬 Film Price Guide API</h1>
            <p>Multi-API search engine for VHS, DVD, and Graded Movies</p>
            
            <div class="warning">
                <strong>Setup Required:</strong> Frontend files not found. Place HTML files in ../frontend/ directory
            </div>
            
            <div class="success">✅ Flask application running successfully</div>
            
            <h2>🔗 Available Endpoints</h2>
            <ul>
                <li><a href="/api/health">/api/health</a> - Health check</li>
                <li><a href="/api/status">/api/status</a> - System status</li>
                <li>/api/ebay/* - eBay API endpoints</li>
                <li>/api/admin/* - Admin panel endpoints</li>
                <li>/api/auth/* - Authentication endpoints</li>
            </ul>
            
            <h2>📋 Next Steps</h2>
            <ol>
                <li>Move your HTML files to frontend/ directory</li>
                <li>Create .env file with API keys</li>
                <li>Set up MySQL database</li>
                <li>Configure admin panel</li>
            </ol>
        </body>
        </html>
        """)

@app.route('/admin')
def admin_panel():
    """Serve the admin configuration panel"""
    try:
        return send_from_directory('../frontend', 'admin-config.html')
    except NotFound:
        return jsonify({"error": "Admin panel not found"}), 404

@app.route('/dashboard')
def dashboard():
    """Serve the user dashboard"""
    try:
        return send_from_directory('../frontend', 'dashboard.html')
    except NotFound:
        return jsonify({"error": "Dashboard not found"}), 404

@app.route('/search')
def search_page():
    """Serve the search results page"""
    try:
        return send_from_directory('../frontend', 'search-results.html')
    except NotFound:
        return jsonify({"error": "Search page not found"}), 404

# ================================
# API ROUTES
# ================================

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Film Price Guide',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/status')
def system_status():
    """System status endpoint"""
    return jsonify({
        'service': 'Film Price Guide API',
        'status': 'running',
        'blueprints': list(app.blueprints.keys()),
        'environment': {
            'EBAY_APP_ID': 'configured' if app.config.get('EBAY_APP_ID') else 'missing',
            'DATABASE_URL': 'configured' if app.config.get('DATABASE_URL') else 'missing'
        },
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/config')
def get_config():
    """Get public configuration"""
    return jsonify({
        'app_name': 'Film Price Guide',
        'version': '1.0.0',
        'apis_available': {
            'ebay': bool(app.config.get('EBAY_APP_ID')),
            'omdb': bool(app.config.get('OMDB_API_KEY')),
            'tmdb': bool(app.config.get('TMDB_API_KEY'))
        }
    })

# ================================
# ERROR HANDLERS
# ================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    return render_template_string("""
    <h1>404 - Page Not Found</h1>
    <p><a href="/">← Back to Home</a></p>
    """), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template_string("""
    <h1>500 - Server Error</h1>
    <p><a href="/">← Back to Home</a></p>
    """), 500

# ================================
# MAIN EXECUTION
# ================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Film Price Guide on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )