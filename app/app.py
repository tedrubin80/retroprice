# backend/app.py
"""
Film Price Guide - Main Flask Application
Entry point for the backend API server
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from datetime import datetime
import logging

# Import configuration
from config.config import Config

# Import blueprints
from endpoints.ebay_api import ebay_bp
from endpoints.ebay_deletion import deletion_bp
# from endpoints.omdb_api import omdb_bp  # Add when created
# from endpoints.tmdb_api import tmdb_bp  # Add when created
# from endpoints.admin_api import admin_bp  # Add when created
# from endpoints.user_api import user_bp  # Add when created

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app, origins=['http://localhost:3000', 'https://yourdomain.com'])

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/film_price_guide.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Register blueprints
app.register_blueprint(ebay_bp)
app.register_blueprint(deletion_bp)
# app.register_blueprint(omdb_bp)  # Uncomment when created
# app.register_blueprint(tmdb_bp)  # Uncomment when created
# app.register_blueprint(admin_bp)  # Uncomment when created
# app.register_blueprint(user_bp)  # Uncomment when created

# Import models (after db initialization)
from models.user import User
from models.film import Film
from models.price_history import PriceHistory
from models.watchlist import Watchlist

@app.route('/')
def index():
    """
    Root endpoint - API status
    """
    return jsonify({
        'service': 'Film Price Guide API',
        'version': '1.0.0',
        'status': 'active',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'ebay_api': '/api/ebay/',
            'deletion_notifications': '/api/ebay/deletion/',
            'health_check': '/health'
        }
    })

@app.route('/health')
def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = 'unhealthy'
    
    health_data = {
        'service': 'Film Price Guide',
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {
            'database': db_status,
            'api_keys_configured': {
                'ebay': bool(app.config.get('EBAY_APP_ID')),
                'omdb': bool(app.config.get('OMDB_API_KEY')),
                'tmdb': bool(app.config.get('TMDB_API_KEY'))
            }
        }
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code

@app.route('/api/status')
def api_status():
    """
    Detailed API status including database statistics
    """
    try:
        # Get database statistics
        film_count = Film.query.count()
        price_count = PriceHistory.query.count()
        user_count = User.query.count()
        
        return jsonify({
            'api_version': '1.0.0',
            'status': 'operational',
            'database_stats': {
                'total_films': film_count,
                'total_price_records': price_count,
                'total_users': user_count
            },
            'available_endpoints': [
                'GET /api/ebay/search - Search sold movie items',
                'GET /api/ebay/categories - Get movie categories',
                'GET /api/ebay/price-history/<id> - Get price history',
                'GET /api/ebay/trending - Get trending movies',
                'POST /api/ebay/deletion/notifications - Handle deletions'
            ],
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in API status: {str(e)}")
        return jsonify({
            'api_version': '1.0.0',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Global error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': [
            'GET / - API information',
            'GET /health - Health check',
            'GET /api/status - Detailed status',
            'GET /api/ebay/* - eBay API endpoints'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    db.session.rollback()
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'message': 'Invalid request format or parameters'
    }), 400

# Request logging middleware
@app.before_request
def log_request_info():
    """Log incoming requests for debugging"""
    if request.endpoint not in ['health_check']:  # Skip health check logs
        logger.info(f"{request.method} {request.url} - {request.remote_addr}")

@app.after_request
def log_response_info(response):
    """Log response status for debugging"""
    if request.endpoint not in ['health_check']:  # Skip health check logs
        logger.info(f"Response: {response.status_code}")
    return response

# Database initialization
@app.before_first_request
def create_tables():
    """Create database tables on first request"""
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

# CLI commands for database management
@app.cli.command('init-db')
def init_db_command():
    """Initialize the database with tables"""
    try:
        db.create_all()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")

@app.cli.command('seed-db')
def seed_db_command():
    """Seed the database with sample data"""
    try:
        # Add sample films
        sample_films = [
            Film(title="Jurassic Park", format="VHS", year=1993),
            Film(title="Jurassic Park", format="DVD", year=1993),
            Film(title="Jurassic Park", format="Blu-ray", year=1993),
            Film(title="The Matrix", format="DVD", year=1999),
            Film(title="Star Wars", format="VHS", year=1977)
        ]
        
        for film in sample_films:
            existing = Film.query.filter_by(
                title=film.title, 
                format=film.format
            ).first()
            if not existing:
                db.session.add(film)
        
        db.session.commit()
        print("Database seeded with sample data!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {str(e)}")

if __name__ == '__main__':
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Film Price Guide API on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )