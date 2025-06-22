# backend/services/ebay_service.py
"""
eBay API Service Class
Handles all eBay API interactions for Film Price Guide
"""

import requests
import base64
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from config.config import Config

logger = logging.getLogger(__name__)

class EbayService:
    """Service class for eBay API operations"""
    
    def __init__(self):
        self.app_id = Config.EBAY_APP_ID
        self.cert_id = Config.EBAY_CERT_ID
        self.dev_id = Config.EBAY_DEV_ID
        self.user_token = Config.EBAY_USER_TOKEN
        self.environment = Config.EBAY_ENVIRONMENT
        self.base_url = Config.EBAY_BASE_URL
        
        # API endpoints
        self.marketplace_insights_url = f"{self.base_url}/buy/marketplace_insights/v1_beta"
        self.oauth_url = f"{self.base_url}/identity/v1/oauth2/token"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        
        # Token management
        self._access_token = None
        self._token_expires_at = None
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate eBay API configuration"""
        if not all([self.app_id, self.cert_id, self.dev_id]):
            raise ValueError("eBay API credentials not properly configured")
        
        logger.info(f"eBay API Service initialized for {self.environment} environment")
    
    def _get_access_token(self) -> str:
        """
        Get OAuth 2.0 access token for eBay API
        Caches token and refreshes when expired
        """
        try:
            # Check if we have a valid cached token
            if (self._access_token and self._token_expires_at and 
                datetime.utcnow() < self._token_expires_at):
                return self._access_token
            
            # Generate new access token
            logger.info("Generating new eBay access token")
            
            # Prepare OAuth request
            credentials = f"{self.app_id}:{self.cert_id}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {encoded_credentials}'
            }
            
            data = {
                'grant_type': 'client_credentials',
                'scope': 'https://api.ebay.com/oauth/api_scope'
            }
            
            response = requests.post(self.oauth_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data['access_token']
            
            # Set expiration time (subtract 5 minutes for safety)
            expires_in = token_data.get('expires_in', 7200)  # Default 2 hours
            self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 300)
            
            logger.info("eBay access token generated successfully")
            return self._access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get eBay access token: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting eBay access token: {str(e)}")
            raise
    
    def _rate_limit(self):
        """Apply rate limiting between API requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make authenticated request to eBay API
        """
        try:
            # Apply rate limiting
            if Config.ENABLE_RATE_LIMITING:
                self._rate_limit()
            
            # Get access token
            access_token = self._get_access_token()
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',  # US marketplace
                'Accept': 'application/json'
            }
            
            # Make request
            url = f"{self.marketplace_insights_url}/{endpoint}"
            response = requests.get(url, headers=headers, params=params)
            
            # Log request for debugging
            logger.info(f"eBay API request: {response.url}")
            logger.info(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"eBay API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"eBay API request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in eBay API request: {str(e)}")
            raise
    
    def search_sold_items(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for sold items using eBay Marketplace Insights API
        
        Args:
            search_params: Dictionary containing search parameters
                - q: Search query (movie title)
                - category_ids: Comma-separated category IDs
                - filter: Additional filters (condition, price, etc.)
                - limit: Number of results (max 200)
                - offset: Pagination offset
                - sort: Sort order
        
        Returns:
            Dictionary containing search results and metadata
        """
        try:
            logger.info(f"Searching eBay sold items with params: {search_params}")
            
            # Build API parameters
            api_params = self._build_search_params(search_params)
            
            # Make API request
            response_data = self._make_api_request('item_sales/search', api_params)
            
            # Process and enhance response
            processed_data = self._process_search_response(response_data, search_params)
            
            logger.info(f"eBay search completed: {len(processed_data.get('itemSales', []))} items found")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error in eBay search: {str(e)}")
            raise
    
    def _build_search_params(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Build API parameters from search request"""
        api_params = {}
        
        # Query string
        if search_params.get('q'):
            api_params['q'] = search_params['q']
        
        # Category IDs
        if search_params.get('category_ids'):
            api_params['category_ids'] = search_params['category_ids']
        
        # Filters
        if search_params.get('filter'):
            api_params['filter'] = search_params['filter']
        
        # Pagination
        api_params['limit'] = min(search_params.get('limit', 50), 200)
        api_params['offset'] = search_params.get('offset', 0)
        
        # Sorting
        if search_params.get('sort'):
            api_params['sort'] = search_params['sort']
        
        # Add default parameters
        api_params['fieldgroups'] = 'MATCHING_ITEMS,EXTENDED'
        
        return api_params
    
    def _process_search_response(self, response_data: Dict[str, Any], 
                               original_params: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance eBay API response"""
        try:
            processed = {
                'total': response_data.get('total', 0),
                'limit': response_data.get('limit', 50),
                'offset': response_data.get('offset', 0),
                'itemSales': response_data.get('itemSales', []),
                'refinement': response_data.get('refinement', {}),
                'warnings': response_data.get('warnings', [])
            }
            
            # Add pagination links
            if 'next' in response_data:
                processed['next'] = response_data['next']
            if 'prev' in response_data:
                processed['prev'] = response_data['prev']
            
            # Enhance item data
            enhanced_items = []
            for item in processed['itemSales']:
                enhanced_item = self._enhance_item_data(item)
                enhanced_items.append(enhanced_item)
            
            processed['itemSales'] = enhanced_items
            
            # Add search metadata
            processed['searchMetadata'] = {
                'query': original_params.get('q', ''),
                'categories_searched': original_params.get('category_ids', ''),
                'search_timestamp': datetime.utcnow().isoformat(),
                'api_environment': self.environment
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing eBay response: {str(e)}")
            # Return original data if processing fails
            return response_data
    
    def _enhance_item_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance individual item data with additional metadata"""
        try:
            enhanced = item.copy()
            
            # Add format detection
            title = item.get('title', '')
            enhanced['detectedFormat'] = self._detect_format(title)
            
            # Add condition mapping
            condition_id = item.get('conditionId')
            enhanced['conditionName'] = self._map_condition_id(condition_id)
            
            # Add price analysis
            if 'lastSoldPrice' in item:
                enhanced['priceAnalysis'] = self._analyze_price(item['lastSoldPrice'])
            
            # Add date formatting
            if 'lastSoldDate' in item:
                enhanced['lastSoldDateFormatted'] = self._format_date(item['lastSoldDate'])
            
            # Add seller analysis
            if 'seller' in item:
                enhanced['sellerAnalysis'] = self._analyze_seller(item['seller'])
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error enhancing item data: {str(e)}")
            return item
    
    def _detect_format(self, title: str) -> str:
        """Detect movie format from title"""
        title_upper = title.upper()
        
        if 'VHS' in title_upper:
            return 'VHS'
        elif 'DVD' in title_upper:
            return 'DVD'
        elif 'BLU-RAY' in title_upper or 'BLURAY' in title_upper:
            return 'Blu-ray'
        elif '4K' in title_upper or 'UHD' in title_upper:
            return '4K UHD'
        elif 'LASERDISC' in title_upper:
            return 'LaserDisc'
        else:
            return 'Unknown'
    
    def _map_condition_id(self, condition_id: str) -> str:
        """Map eBay condition ID to readable name"""
        condition_map = {
            '1000': 'New',
            '1500': 'New Other',
            '2000': 'Manufacturer Refurbished',
            '2500': 'Seller Refurbished',
            '2750': 'Like New',
            '3000': 'Used',
            '4000': 'Very Good',
            '5000': 'Good',
            '6000': 'Acceptable',
            '7000': 'For Parts or Not Working'
        }
        
        return condition_map.get(str(condition_id), 'Unknown')
    
    def _analyze_price(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze price data and add insights"""
        try:
            price_value = float(price_data.get('value', 0))
            currency = price_data.get('currency', 'USD')
            
            analysis = {
                'value': price_value,
                'currency': currency,
                'formatted': f"${price_value:.2f}" if currency == 'USD' else f"{price_value:.2f} {currency}",
                'category': self._categorize_price(price_value)
            }
            
            return analysis
            
        except (ValueError, TypeError):
            return {'value': 0, 'currency': 'USD', 'formatted': '$0.00', 'category': 'Unknown'}
    
    def _categorize_price(self, price: float) -> str:
        """Categorize price into ranges"""
        if price < 5:
            return 'Budget'
        elif price < 15:
            return 'Low'
        elif price < 50:
            return 'Medium'
        elif price < 100:
            return 'High'
        else:
            return 'Premium'
    
    def _format_date(self, date_string: str) -> str:
        """Format ISO date string to readable format"""
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M UTC')
        except:
            return date_string
    
    def _analyze_seller(self, seller_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze seller data and add insights"""
        try:
            feedback_score = seller_data.get('feedbackScore', 0)
            feedback_percentage = seller_data.get('feedbackPercentage', 0)
            
            analysis = {
                'feedback_score': feedback_score,
                'feedback_percentage': feedback_percentage,
                'reputation': self._calculate_seller_reputation(feedback_score, feedback_percentage)
            }
            
            return analysis
            
        except:
            return {'reputation': 'Unknown'}
    
    def _calculate_seller_reputation(self, score: int, percentage: float) -> str:
        """Calculate seller reputation based on feedback"""
        if score >= 1000 and percentage >= 99:
            return 'Excellent'
        elif score >= 500 and percentage >= 98:
            return 'Very Good'
        elif score >= 100 and percentage >= 95:
            return 'Good'
        elif score >= 10 and percentage >= 90:
            return 'Fair'
        else:
            return 'New/Limited'
    
    def get_categories(self) -> Dict[str, Any]:
        """Get eBay categories relevant to movies"""
        return {
            'vhs': {'id': '309', 'name': 'VHS Movies'},
            'dvd': {'id': '617', 'name': 'DVD Movies'},
            'bluray': {'id': '2649', 'name': 'Blu-ray Movies'},
            'memorabilia': {'id': '11232', 'name': 'Movie Memorabilia'}
        }
    
    def health_check(self) -> bool:
        """
        Check if eBay API is accessible and credentials are valid
        """
        try:
            # Try to get an access token
            token = self._get_access_token()
            
            # Make a simple API call
            test_params = {
                'q': 'test',
                'category_ids': '617',  # DVD category
                'limit': 1
            }
            
            self._make_api_request('item_sales/search', test_params)
            return True
            
        except Exception as e:
            logger.error(f"eBay API health check failed: {str(e)}")
            return False
    
    def get_api_limits(self) -> Dict[str, Any]:
        """Get current API usage and limits"""
        # This would require tracking API calls
        # For now, return configuration limits
        return {
            'calls_per_day': 5000,  # Typical eBay limit
            'calls_made_today': 0,  # Would need to track this
            'rate_limit_per_second': 1,
            'environment': self.environment
        }