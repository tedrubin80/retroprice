# backend/endpoints/ebay_api.py
"""
eBay API Endpoint for Film Price Guide
Handles eBay Marketplace Insights API calls for movie price data
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import requests
import os
import time
from functools import wraps
import logging

# Import custom modules
from services.ebay_service import EbayService
from utils.rate_limiter import RateLimiter
from utils.auth import require_api_key
from models.price_history import PriceHistory
from models.film import Film

# Create Blueprint
ebay_bp = Blueprint('ebay_api', __name__, url_prefix='/api/ebay')

# Initialize services
ebay_service = EbayService()
rate_limiter = RateLimiter(max_requests=100, window_seconds=3600)  # 100 requests per hour

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rate_limit_check(f):
    """Decorator to check rate limits"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if not rate_limiter.is_allowed(client_ip):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': rate_limiter.get_retry_after(client_ip)
            }), 429
        return f(*args, **kwargs)
    return decorated_function

@ebay_bp.route('/search', methods=['GET'])
@rate_limit_check
def search_sold_items():
    """
    Search for sold movie items on eBay
    
    Query Parameters:
    - q: Search query (movie title)
    - category_ids: eBay category IDs (comma-separated)
    - condition: Item condition filter
    - min_price: Minimum price filter
    - max_price: Maximum price filter
    - currency: Currency code (default: USD)
    - limit: Number of results (default: 50, max: 200)
    - offset: Pagination offset (default: 0)
    - sort: Sort order (price, -price, or best_match)
    """
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        category_ids = request.args.get('category_ids', '')
        condition = request.args.get('condition', '')
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        currency = request.args.get('currency', 'USD')
        limit = min(int(request.args.get('limit', 50)), 200)
        offset = int(request.args.get('offset', 0))
        sort_order = request.args.get('sort', '')
        
        # Validate required parameters
        if not query and not category_ids:
            return jsonify({
                'error': 'Missing required parameter',
                'message': 'Either "q" (query) or "category_ids" must be provided'
            }), 400
        
        # Default to movie categories if no category specified
        if not category_ids and query:
            category_ids = '309,617,2649'  # VHS, DVD, Blu-ray
        
        # Build search parameters
        search_params = {
            'q': query,
            'category_ids': category_ids,
            'limit': limit,
            'offset': offset
        }
        
        # Add filters
        filters = []
        if condition:
            condition_map = {
                'graded': 'conditionIds:{2750}',  # Graded
                'sealed': 'conditionIds:{1000,1500}',  # New/New Other
                'new': 'conditionIds:{1000}',  # New
                'very-good': 'conditionIds:{2000}',  # Very Good
                'good': 'conditionIds:{2500}',  # Good
                'used': 'conditionIds:{3000,4000,5000,6000}'  # Used conditions
            }
            if condition in condition_map:
                filters.append(condition_map[condition])
        
        if min_price or max_price:
            min_val = min_price or '0'
            max_val = max_price or '999999'
            filters.append(f'price:[{min_val}..{max_val}]')
            filters.append(f'priceCurrency:{currency}')
        
        if filters:
            search_params['filter'] = ','.join(filters)
        
        if sort_order:
            search_params['sort'] = sort_order
        
        # Make eBay API call
        logger.info(f"eBay search request: {search_params}")
        response_data = ebay_service.search_sold_items(search_params)
        
        # Process and enhance results
        processed_results = process_ebay_results(response_data, query)
        
        # Store price history in database
        if 'itemSales' in response_data:
            store_price_history(response_data['itemSales'], query)
        
        return jsonify(processed_results), 200
        
    except requests.exceptions.RequestException as e:
        logger.error(f"eBay API request failed: {str(e)}")
        return jsonify({
            'error': 'eBay API request failed',
            'message': str(e)
        }), 503
        
    except ValueError as e:
        logger.error(f"Invalid parameter: {str(e)}")
        return jsonify({
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in eBay search: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@ebay_bp.route('/categories', methods=['GET'])
@rate_limit_check
def get_movie_categories():
    """
    Get eBay category information for movies
    """
    try:
        categories = {
            'vhs': {
                'id': '309',
                'name': 'VHS Movies',
                'description': 'VHS videotapes and movies'
            },
            'dvd': {
                'id': '617', 
                'name': 'DVD Movies',
                'description': 'DVD movies and collections'
            },
            'bluray': {
                'id': '2649',
                'name': 'Blu-ray Movies', 
                'description': 'Blu-ray discs and movies'
            },
            'memorabilia': {
                'id': '11232',
                'name': 'Movie Memorabilia',
                'description': 'Movie collectibles and memorabilia'
            }
        }
        
        return jsonify({
            'success': True,
            'categories': categories
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch categories',
            'message': str(e)
        }), 500

@ebay_bp.route('/price-history/<int:film_id>', methods=['GET'])
@rate_limit_check
def get_price_history(film_id):
    """
    Get price history for a specific film
    """
    try:
        days = int(request.args.get('days', 90))
        format_filter = request.args.get('format', '')
        
        # Get price history from database
        price_data = PriceHistory.get_by_film_id(
            film_id=film_id,
            days=days,
            format_filter=format_filter
        )
        
        if not price_data:
            return jsonify({
                'error': 'No price data found',
                'message': f'No price history found for film ID {film_id}'
            }), 404
        
        # Calculate statistics
        prices = [float(item['price']) for item in price_data]
        stats = {
            'count': len(prices),
            'avg_price': round(sum(prices) / len(prices), 2) if prices else 0,
            'min_price': min(prices) if prices else 0,
            'max_price': max(prices) if prices else 0,
            'median_price': round(sorted(prices)[len(prices)//2], 2) if prices else 0
        }
        
        return jsonify({
            'success': True,
            'film_id': film_id,
            'period_days': days,
            'statistics': stats,
            'price_history': price_data
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid parameter',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error fetching price history: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch price history',
            'message': str(e)
        }), 500

@ebay_bp.route('/trending', methods=['GET'])
@rate_limit_check
def get_trending_movies():
    """
    Get trending movie titles based on recent sales activity
    """
    try:
        days = int(request.args.get('days', 7))
        limit = min(int(request.args.get('limit', 20)), 100)
        format_filter = request.args.get('format', '')
        
        # Get trending data from database
        trending_data = PriceHistory.get_trending_films(
            days=days,
            limit=limit,
            format_filter=format_filter
        )
        
        return jsonify({
            'success': True,
            'period_days': days,
            'trending_movies': trending_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching trending movies: {str(e)}")
        return jsonify({
            'error': 'Failed to fetch trending movies',
            'message': str(e)
        }), 500

@ebay_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for eBay API service
    """
    try:
        # Test eBay API connectivity
        health_status = ebay_service.health_check()
        
        return jsonify({
            'service': 'eBay API',
            'status': 'healthy' if health_status else 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }), 200 if health_status else 503
        
    except Exception as e:
        return jsonify({
            'service': 'eBay API',
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

def process_ebay_results(ebay_response, search_query):
    """
    Process eBay API response and enhance with additional data
    """
    try:
        processed = {
            'success': True,
            'query': search_query,
            'total_results': ebay_response.get('total', 0),
            'results_returned': len(ebay_response.get('itemSales', [])),
            'search_timestamp': datetime.utcnow().isoformat(),
            'items': []
        }
        
        # Add pagination info
        if 'next' in ebay_response:
            processed['next_page'] = ebay_response['next']
        if 'prev' in ebay_response:
            processed['prev_page'] = ebay_response['prev']
        
        # Process each item
        for item in ebay_response.get('itemSales', []):
            processed_item = {
                'item_id': item.get('itemId'),
                'title': item.get('title'),
                'format': detect_format(item.get('title', '')),
                'condition': item.get('condition'),
                'condition_id': item.get('conditionId'),
                'price': {
                    'value': float(item.get('lastSoldPrice', {}).get('value', 0)),
                    'currency': item.get('lastSoldPrice', {}).get('currency', 'USD')
                },
                'sale_date': item.get('lastSoldDate'),
                'quantity_sold': item.get('totalSoldQuantity', 1),
                'images': {
                    'primary': item.get('image', {}).get('imageUrl'),
                    'additional': [img.get('imageUrl') for img in item.get('additionalImages', [])]
                },
                'seller': {
                    'username': item.get('seller', {}).get('username'),
                    'feedback_score': item.get('seller', {}).get('feedbackScore'),
                    'feedback_percentage': item.get('seller', {}).get('feedbackPercentage')
                },
                'listing_url': item.get('itemWebUrl'),
                'categories': [cat.get('categoryId') for cat in item.get('categories', [])]
            }
            
            processed['items'].append(processed_item)
        
        return processed
        
    except Exception as e:
        logger.error(f"Error processing eBay results: {str(e)}")
        return {
            'success': False,
            'error': 'Failed to process results',
            'message': str(e)
        }

def detect_format(title):
    """
    Detect movie format from title
    """
    title_upper = title.upper()
    if 'VHS' in title_upper:
        return 'VHS'
    elif 'DVD' in title_upper:
        return 'DVD'
    elif 'BLU-RAY' in title_upper or 'BLURAY' in title_upper:
        return 'Blu-ray'
    elif '4K' in title_upper or 'UHD' in title_upper:
        return '4K UHD'
    else:
        return 'Unknown'

def store_price_history(items, search_query):
    """
    Store price history data in database
    """
    try:
        for item in items:
            # Find or create film record
            film = Film.find_or_create_by_title_format(
                title=item.get('title'),
                format=detect_format(item.get('title', ''))
            )
            
            # Create price history record
            price_data = {
                'film_id': film.id,
                'price': float(item.get('lastSoldPrice', {}).get('value', 0)),
                'currency': item.get('lastSoldPrice', {}).get('currency', 'USD'),
                'condition_name': item.get('condition'),
                'condition_id': item.get('conditionId'),
                'sale_date': item.get('lastSoldDate'),
                'platform': 'eBay',
                'listing_type': 'Unknown',  # eBay doesn't always provide this
                'seller_rating': item.get('seller', {}).get('feedbackScore'),
                'total_sold_quantity': item.get('totalSoldQuantity', 1),
                'external_listing_id': item.get('itemId'),
                'external_listing_url': item.get('itemWebUrl'),
                'listing_title': item.get('title')
            }
            
            PriceHistory.create(price_data)
            
    except Exception as e:
        logger.error(f"Error storing price history: {str(e)}")

# Error handlers
@ebay_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested eBay API endpoint does not exist'
    }), 404

@ebay_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred in the eBay API service'
    }), 500