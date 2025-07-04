# ================================================================
# SAVE AS: backend/app.py
# Film Price Guide - Fixed Flask Application
# ================================================================

import os
from flask import Flask, jsonify, request
from flask_cors import CORS

def create_app():
    """Application factory pattern for Flask"""
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DEBUG'] = os.environ.get('FLASK_ENV') == 'development'
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'Film Price Guide Backend',
            'version': '1.0.0'
        })
    
    # API endpoints
    @app.route('/api/search')
    def search_movies():
        query = request.args.get('q', '')
        return jsonify({
            'query': query,
            'results': [],
            'message': 'Search functionality coming soon'
        })
    
    @app.route('/api/ebay/search')
    def ebay_search():
        return jsonify({
            'status': 'success',
            'message': 'eBay API integration ready',
            'data': []
        })
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Film Price Guide API',
            'status': 'running',
            'endpoints': [
                '/health',
                '/api/search',
                '/api/ebay/search'
            ]
        })
    
    return app

# Create app instance for development
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)