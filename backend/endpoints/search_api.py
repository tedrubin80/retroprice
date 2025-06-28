#!/usr/bin/env python3
"""
Film Price Guide - Search API
Multi-source search endpoints for films and price data
"""

from flask import Blueprint, request, jsonify, current_app
import logging
from datetime import datetime

# Import services
try:
    from services.database_service import get_db
    from endpoints.auth_api import login_required
except ImportError:
    def get_db():
        return None
    def login_required(f):
        return f

logger = logging.getLogger(__name__)

# Create blueprint
search_bp = Blueprint('search', __name__, url_prefix='/api/search')

# ================================
# SEARCH ENDPOINTS
# ================================

@search_bp.route('/', methods=['GET'])
def search_films():
    """Search for films across multiple sources"""
    try:
        # Get search parameters
        query = request.args.get('q', '').strip()
        format_filter = request.args.get('format')  # VHS, DVD, Blu-ray, etc.
        source = request.args.get('source', 'database')  # database, ebay, omdb, tmdb
        limit = min(int(request.args.get('limit', 50)), 200)
        page = int(request.args.get('page', 1))
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        results = []
        total_count = 0
        
        if source == 'database' or source == 'all':
            # Search local database
            db = get_db()
            if db:
                db_results = db.search_films(query, format_filter, limit)
                results.extend(db_results)
                total_count += len(db_results)
        
        if source == 'ebay' or source == 'all':
            # Search eBay (if API configured)
            ebay_results = search_ebay(query, format_filter, limit)
            results.extend(ebay_results)
            total_count += len(ebay_results)
        
        if source == 'omdb' or source == 'all':
            # Search OMDb (if API configured)
            omdb_results = search_omdb(query, limit)
            results.extend(omdb_results)
            total_count += len(omdb_results)
        
        return jsonify({
            'query': query,
            'results': results,
            'total_count': total_count,
            'page': page,
            'limit': limit,
            'source': source,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500

@search_bp.route('/films/<int:film_id>', methods=['GET'])
def get_film_details(film_id):
    """Get detailed film information"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        # Get film details
        film = db.get_film_by_id(film_id)
        if not film:
            return jsonify({'error': 'Film not found'}), 404
        
        # Get price history
        price_history = db.get_price_history(film_id, limit=100)
        
        # Calculate price statistics
        if price_history:
            prices = [float(entry['price']) for entry in price_history]
            price_stats = {
                'min_price': min(prices),
                'max_price': max(prices),
                'avg_price': sum(prices) / len(prices),
                'recent_price': prices[0] if prices else None,
                'price_trend': calculate_price_trend(prices)
            }
        else:
            price_stats = None
        
        return jsonify({
            'film': film,
            'price_history': price_history,
            'price_statistics': price_stats,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Get film details error: {e}")
        return jsonify({'error': 'Failed to get film details'}), 500

@search_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    """Get autocomplete suggestions"""
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 10)), 20)
        
        if len(query) < 2:
            return jsonify({'suggestions': []}), 200
        
        db = get_db()
        if not db:
            return jsonify({'suggestions': []}), 200
        
        # Search for film titles that start with the query
        sql_query = """
        SELECT DISTINCT title, year, format
        FROM films 
        WHERE title LIKE %s 
        ORDER BY title 
        LIMIT %s
        """
        
        success, results = db.execute_query(
            sql_query, 
            (f"{query}%", limit), 
            fetch=True
        )
        
        suggestions = []
        if success and results:
            for result in results:
                suggestion = {
                    'title': result['title'],
                    'year': result.get('year'),
                    'format': result.get('format'),
                    'display': f"{result['title']} ({result.get('year', 'Unknown')})"
                }
                suggestions.append(suggestion)
        
        return jsonify({
            'query': query,
            'suggestions': suggestions
        }), 200
        
    except Exception as e:
        logger.error(f"Autocomplete error: {e}")
        return jsonify({'suggestions': []}), 200

# ================================
# WATCHLIST ENDPOINTS
# ================================

@search_bp.route('/watchlist', methods=['GET'])
@login_required
def get_watchlist():
    """Get user's watchlist"""
    try:
        from flask import session
        
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        user_id = session['user_id']
        watchlist = db.get_user_watchlist(user_id)
        
        return jsonify({
            'watchlist': watchlist,
            'count': len(watchlist),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Get watchlist error: {e}")
        return jsonify({'error': 'Failed to get watchlist'}), 500

@search_bp.route('/watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    """Add film to user's watchlist"""
    try:
        from flask import session
        
        data = request.get_json()
        film_id = data.get('film_id')
        target_price = data.get('target_price')
        
        if not film_id:
            return jsonify({'error': 'Film ID is required'}), 400
        
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        user_id = session['user_id']
        
        # Check if film exists
        film = db.get_film_by_id(film_id)
        if not film:
            return jsonify({'error': 'Film not found'}), 404
        
        # Add to watchlist
        success, result = db.add_to_watchlist(user_id, film_id, target_price)
        
        if success:
            return jsonify({
                'message': 'Added to watchlist successfully',
                'film_id': film_id,
                'target_price': target_price
            }), 201
        else:
            return jsonify({'error': 'Failed to add to watchlist'}), 500
            
    except Exception as e:
        logger.error(f"Add to watchlist error: {e}")
        return jsonify({'error': 'Failed to add to watchlist'}), 500

@search_bp.route('/watchlist/<int:film_id>', methods=['DELETE'])
@login_required
def remove_from_watchlist(film_id):
    """Remove film from user's watchlist"""
    try:
        from flask import session
        
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        user_id = session['user_id']
        success, result = db.remove_from_watchlist(user_id, film_id)
        
        if success:
            return jsonify({'message': 'Removed from watchlist successfully'}), 200
        else:
            return jsonify({'error': 'Failed to remove from watchlist'}), 500
            
    except Exception as e:
        logger.error(f"Remove from watchlist error: {e}")
        return jsonify({'error': 'Failed to remove from watchlist'}), 500

# ================================
# EXTERNAL API SEARCH FUNCTIONS
# ================================

def search_ebay(query, format_filter=None, limit=20):
    """Search eBay for films"""
    try:
        # Check if eBay API is configured
        if not current_app.config.get('EBAY_APP_ID'):
            return []
        
        # Import eBay service (if available)
        try:
            from services.ebay_service import EbayService
            ebay = EbayService()
            return ebay.search_completed_listings(query, format_filter, limit)
        except ImportError:
            logger.warning("eBay service not available")
            return []
        
    except Exception as e:
        logger.error(f"eBay search error: {e}")
        return []

def search_omdb(query, limit=10):
    """Search OMDb for film metadata"""
    try:
        # Check if OMDb API is configured
        if not current_app.config.get('OMDB_API_KEY'):
            return []
        
        import requests
        
        api_key = current_app.config['OMDB_API_KEY']
        url = f"http://www.omdbapi.com/?apikey={api_key}&s={query}&type=movie"
        
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('Response') == 'True' and data.get('Search'):
            results = []
            for item in data['Search'][:limit]:
                result = {
                    'source': 'omdb',
                    'title': item.get('Title'),
                    'year': item.get('Year'),
                    'imdb_id': item.get('imdbID'),
                    'poster_url': item.get('Poster'),
                    'type': item.get('Type')
                }
                results.append(result)
            return results
        
        return []
        
    except Exception as e:
        logger.error(f"OMDb search error: {e}")
        return []

def search_tmdb(query, limit=10):
    """Search TMDb for film metadata"""
    try:
        # Check if TMDb API is configured
        if not current_app.config.get('TMDB_API_KEY'):
            return []
        
        import requests
        
        api_key = current_app.config['TMDB_API_KEY']
        url = f"https://api.themoviedb.org/3/search/movie"
        
        params = {
            'api_key': api_key,
            'query': query,
            'page': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('results'):
            results = []
            for item in data['results'][:limit]:
                result = {
                    'source': 'tmdb',
                    'title': item.get('title'),
                    'year': item.get('release_date', '')[:4] if item.get('release_date') else None,
                    'tmdb_id': item.get('id'),
                    'poster_url': f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                    'overview': item.get('overview'),
                    'rating': item.get('vote_average')
                }
                results.append(result)
            return results
        
        return []
        
    except Exception as e:
        logger.error(f"TMDb search error: {e}")
        return []

# ================================
# UTILITY FUNCTIONS
# ================================

def calculate_price_trend(prices):
    """Calculate price trend from price history"""
    if len(prices) < 2:
        return 'stable'
    
    # Simple trend calculation
    recent_avg = sum(prices[:5]) / min(5, len(prices))
    older_avg = sum(prices[-5:]) / min(5, len(prices))
    
    if recent_avg > older_avg * 1.1:
        return 'increasing'
    elif recent_avg < older_avg * 0.9:
        return 'decreasing'
    else:
        return 'stable'

# ================================
# ADVANCED SEARCH ENDPOINTS
# ================================

@search_bp.route('/advanced', methods=['POST'])
def advanced_search():
    """Advanced search with multiple filters"""
    try:
        data = request.get_json()
        
        # Extract search parameters
        title = data.get('title', '').strip()
        director = data.get('director', '').strip()
        year_min = data.get('year_min')
        year_max = data.get('year_max')
        format_filter = data.get('format')
        genre = data.get('genre')
        price_min = data.get('price_min')
        price_max = data.get('price_max')
        condition = data.get('condition')
        limit = min(int(data.get('limit', 50)), 200)
        
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        # Build dynamic query
        where_clauses = []
        params = []
        
        if title:
            where_clauses.append("f.title LIKE %s")
            params.append(f"%{title}%")
        
        if director:
            where_clauses.append("f.director LIKE %s")
            params.append(f"%{director}%")
        
        if year_min:
            where_clauses.append("f.year >= %s")
            params.append(year_min)
        
        if year_max:
            where_clauses.append("f.year <= %s")
            params.append(year_max)
        
        if format_filter:
            where_clauses.append("f.format = %s")
            params.append(format_filter)
        
        # Build the query
        query = """
        SELECT f.*, 
               COUNT(ph.id) as price_count,
               MIN(ph.price) as min_price,
               MAX(ph.price) as max_price,
               AVG(ph.price) as avg_price
        FROM films f
        LEFT JOIN price_history ph ON f.id = ph.film_id
        """
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " GROUP BY f.id ORDER BY f.title LIMIT %s"
        params.append(limit)
        
        success, results = db.execute_query(query, params, fetch=True)
        
        return jsonify({
            'results': results if success else [],
            'count': len(results) if success else 0,
            'filters': data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        return jsonify({'error': 'Advanced search failed'}), 500

@search_bp.route('/trending', methods=['GET'])
def get_trending():
    """Get trending films based on recent activity"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        # Get films with recent price activity
        query = """
        SELECT f.*, 
               COUNT(ph.id) as recent_sales,
               AVG(ph.price) as avg_recent_price
        FROM films f
        JOIN price_history ph ON f.id = ph.film_id
        WHERE ph.sale_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY f.id
        HAVING recent_sales >= 3
        ORDER BY recent_sales DESC, avg_recent_price DESC
        LIMIT 20
        """
        
        success, results = db.execute_query(query, fetch=True)
        
        return jsonify({
            'trending': results if success else [],
            'period': '30 days',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Get trending error: {e}")
        return jsonify({'error': 'Failed to get trending films'}), 500

# ================================
# ERROR HANDLERS
# ================================

@search_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@search_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@search_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500