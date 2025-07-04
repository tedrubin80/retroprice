# ================================================================
# SAVE AS: backend/app.py (REPLACE your current backend/app.py)
# Simple Flask app that works with Railway
# ================================================================

import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# Create Flask app instance
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['DEBUG'] = os.environ.get('FLASK_ENV') == 'development'

# Routes
@app.route('/')
def index():
    return jsonify({
        'message': 'Film Price Guide API',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Film Price Guide Backend'
    })

@app.route('/api/search')
def search_movies():
    query = request.args.get('q', '')
    return jsonify({
        'query': query,
        'results': [],
        'message': 'Search functionality ready'
    })

@app.route('/api/ebay/search')
def ebay_search():
    return jsonify({
        'status': 'success',
        'message': 'eBay API integration ready'
    })

# Create app function for factory pattern (optional)
def create_app():
    return app

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)