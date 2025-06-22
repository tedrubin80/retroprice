# backend/services/gocollect_service.py
"""
GoCollect API Service for Film Price Guide
Integrates collectible movie item pricing from GoCollect
"""

import requests
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class GoCollectService:
    def __init__(self):
        self.base_url = "https://gocollect.com"
        self.api_token = os.getenv('GOCOLLECT_API_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Rate limiting - VERY STRICT (from OpenAPI spec)
        self.rate_limit_daily = 50  # Non-subscribers (conservative default)
        self.rate_limit_pro_daily = 100  # Pro subscribers
        self.rate_limit_sold_examples = 500  # Per hour for sold examples API
        self.rate_limit_staged_sales = 500  # Per hour for staged sales API
        
        # Valid markets from OpenAPI spec
        self.valid_markets = [
            'comics', 'video-games', 'concert-posters', 
            'trading-cards', 'sports-cards', 'magazines'
        ]
        
        # Certification companies by market
        self.certification_companies = {
            'comics': ['cbcs', 'cgc'],
            'concert-posters': ['cgc', 'not-certified'],
            'magazines': ['cbcs', 'cgc'],
            'sports-cards': ['bgs', 'cgc', 'psa', 'sgc'],
            'trading-cards': ['bgs', 'cgc', 'psa'],
            'video-games': ['cgc', 'vga', 'wata']
        }
        
    def search_collectibles(self, query: str, cam: str = "comics", limit: int = 20) -> Optional[List[Dict]]:
        """
        Search for collectible items related to movies
        
        Args:
            query: Search term (e.g., "Star Wars", "Jurassic Park")
            cam: Collectible market - must be one of: comics, video-games, concert-posters, 
                 trading-cards, sports-cards, magazines (defaults to "comics")
            limit: Max results (default 20, max 100 per OpenAPI spec)
        
        Returns:
            List of collectible items with GoCollect IDs
        """
        try:
            # Validate market parameter
            if cam not in self.valid_markets:
                logger.error(f"Invalid market '{cam}'. Valid markets: {self.valid_markets}")
                return None
                
            endpoint = f"{self.base_url}/api/collectibles/v1/item/search"
            
            params = {
                'query': query,
                'cam': cam,
                'limit': min(limit, 100)  # OpenAPI spec max is 100
            }
            
            logger.info(f"Searching GoCollect for: {query} in {cam} market")
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code == 200:
                results = response.json()
                # OpenAPI shows results are a direct array, not wrapped in a data object
                logger.info(f"Found {len(results)} collectibles on GoCollect")
                return results
                
            elif response.status_code == 204:
                logger.info("No results found on GoCollect")
                return []
                
            elif response.status_code == 400:
                error_data = response.json()
                logger.error(f"GoCollect search error: {error_data.get('message', 'Bad request')}")
                return None
                
            elif response.status_code == 404:
                error_data = response.json()
                logger.error(f"Invalid cam parameter: {error_data.get('message', 'Invalid market')}")
                return None
                
            elif response.status_code == 429:
                logger.warning("GoCollect rate limit exceeded")
                return None
                
            else:
                logger.error(f"GoCollect search failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching GoCollect: {str(e)}")
            return None
    
    def get_item_insights(self, item_id: int, grade: str = "9.8", 
                         company: str = "CGC", label: str = "Universal") -> Optional[Dict]:
        """
        Get pricing insights for a specific GoCollect item
        
        Args:
            item_id: GoCollect item ID
            grade: Item grade (required)
            company: Certification company (default: CGC)
            label: Certification label (default: Universal)
        
        Returns:
            Pricing insights with 30/90/365 day metrics
        """
        try:
            endpoint = f"{self.base_url}/api/insights/v1/item/{item_id}"
            
            params = {
                'grade': grade,
                'company': company,
                'label': label
            }
            
            logger.info(f"Getting insights for GoCollect item {item_id}")
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            
            if response.status_code == 200:
                insights = response.json()
                logger.info(f"Retrieved insights for {insights.get('title', 'Unknown')} #{insights.get('issue_number', '')}")
                return insights
                
            elif response.status_code == 404:
                logger.warning(f"GoCollect item {item_id} not found or invalid grade/company/label")
                return None
                
            elif response.status_code == 429:
                logger.warning("GoCollect rate limit exceeded")
                return None
                
            else:
                logger.error(f"GoCollect insights failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting GoCollect insights: {str(e)}")
            return None
    
    def search_movie_collectibles(self, movie_title: str) -> Dict[str, List[Dict]]:
        """
        Search across all GoCollect markets for movie-related collectibles
        
        Args:
            movie_title: Movie title to search for
            
        Returns:
            Dictionary with results from each market
        """
        # Use correct market names from OpenAPI spec
        movie_relevant_markets = ["comics", "video-games", "concert-posters"]
        results = {}
        
        for market in movie_relevant_markets:
            try:
                # Add delay to respect very strict rate limits (50-100/day)
                time.sleep(1)  # Be very conservative with rate limits
                
                market_results = self.search_collectibles(movie_title, market, limit=20)  # Reduced from 50
                if market_results:
                    results[market] = market_results
                else:
                    results[market] = []
                    
            except Exception as e:
                logger.error(f"Error searching {market} for {movie_title}: {str(e)}")
                results[market] = []
        
        return results
    
    def get_comparable_pricing(self, movie_title: str, format_type: str = "comics") -> Optional[Dict]:
        """
        Get pricing data for movie collectibles to compare with VHS/DVD prices
        
        Args:
            movie_title: Movie title
            format_type: GoCollect market to search (comics, video-games, concert-posters)
            
        Returns:
            Aggregated pricing data across items
        """
        try:
            # Validate market
            if format_type not in self.valid_markets:
                logger.error(f"Invalid market '{format_type}'. Valid: {self.valid_markets}")
                return None
                
            # Search for related collectibles
            collectibles = self.search_collectibles(movie_title, format_type)
            
            if not collectibles:
                return None
            
            pricing_data = []
            
            # Get insights for each collectible (limit to top 3 to respect STRICT rate limits)
            for item in collectibles[:3]:  # Reduced from 5 to 3
                time.sleep(2)  # More conservative rate limiting (daily limits are very low)
                
                insights = self.get_item_insights(item['item_id'])
                if insights and insights.get('metrics'):
                    pricing_data.append(insights)
            
            if not pricing_data:
                return None
            
            # Aggregate pricing across all items
            return self._aggregate_pricing_data(pricing_data, movie_title, format_type)
            
        except Exception as e:
            logger.error(f"Error getting comparable pricing: {str(e)}")
            return None
    
    def _aggregate_pricing_data(self, pricing_data: List[Dict], movie_title: str, format_type: str) -> Dict:
        """Aggregate pricing data from multiple GoCollect items"""
        
        aggregated = {
            'movie_title': movie_title,
            'collectible_type': format_type,
            'total_items_found': len(pricing_data),
            'aggregated_metrics': {
                '30': {'sold_count': 0, 'avg_price': 0, 'price_range': [0, 0]},
                '90': {'sold_count': 0, 'avg_price': 0, 'price_range': [0, 0]},
                '365': {'sold_count': 0, 'avg_price': 0, 'price_range': [0, 0]}
            },
            'individual_items': []
        }
        
        for period in ['30', '90', '365']:
            total_sales = 0
            total_revenue = 0
            min_price = float('inf')
            max_price = 0
            
            for item in pricing_data:
                metrics = item.get('metrics', {}).get(period, {})
                if metrics:
                    sold_count = metrics.get('sold_count', 0)
                    avg_price = metrics.get('average_price', 0)
                    
                    total_sales += sold_count
                    total_revenue += (sold_count * avg_price)
                    
                    low_price = metrics.get('low_price', 0)
                    high_price = metrics.get('high_price', 0)
                    
                    if low_price > 0:
                        min_price = min(min_price, low_price)
                    max_price = max(max_price, high_price)
            
            if total_sales > 0:
                aggregated['aggregated_metrics'][period] = {
                    'sold_count': total_sales,
                    'avg_price': round(total_revenue / total_sales, 2),
                    'price_range': [min_price if min_price != float('inf') else 0, max_price]
                }
        
        # Store individual item details
        for item in pricing_data:
            aggregated['individual_items'].append({
                'item_id': item.get('item_id'),
                'title': item.get('title'),
                'issue_number': item.get('issue_number'),
                'fmv': item.get('fmv'),
                'grade': item.get('grade'),
                'company': item.get('company')
            })
        
        return aggregated
    
    def health_check(self) -> bool:
        """Check if GoCollect API is accessible"""
        try:
            # Simple search to test connectivity
            response = requests.get(
                f"{self.base_url}/api/collectibles/v1/item/search",
                headers=self.headers,
                params={'query': 'test', 'limit': 1},
                timeout=10
            )
            return response.status_code in [200, 204]  # 204 = no results, but API working
            
        except Exception:
            return False

class GoCollectMovieIntegration:
    """
    Integration service that combines GoCollect data with existing film price data
    """
    
    def __init__(self, gocollect_service: GoCollectService):
        self.gocollect = gocollect_service
    
    def get_enhanced_movie_pricing(self, movie_title: str, release_year: Optional[int] = None) -> Dict:
        """
        Get comprehensive pricing data combining traditional movie formats with collectibles
        
        Args:
            movie_title: Title of the movie
            release_year: Release year for better matching
            
        Returns:
            Enhanced pricing data with collectible context
        """
        
        # Search all GoCollect markets for this movie
        search_query = f"{movie_title}"
        if release_year:
            search_query += f" {release_year}"
        
        collectible_data = self.gocollect.search_movie_collectibles(search_query)
        
        enhanced_data = {
            'movie_title': movie_title,
            'release_year': release_year,
            'collectible_markets': {},
            'collectible_summary': {
                'total_items_found': 0,
                'markets_with_data': [],
                'highest_value_item': None,
                'collectible_demand_indicator': 'Unknown'
            }
        }
        
        total_items = 0
        highest_value = 0
        highest_value_item = None
        
        # Process each market's data
        for market, items in collectible_data.items():
            if items:
                total_items += len(items)
                enhanced_data['collectible_summary']['markets_with_data'].append(market)
                
                # Get pricing for top item in this market
                if items:
                    top_item = items[0]  # Take first result
                    pricing = self.gocollect.get_item_insights(top_item['item_id'])
                    
                    if pricing and pricing.get('fmv'):
                        fmv = pricing['fmv']
                        if fmv > highest_value:
                            highest_value = fmv
                            highest_value_item = {
                                'market': market,
                                'title': pricing.get('title'),
                                'issue_number': pricing.get('issue_number'),
                                'fmv': fmv,
                                'item_id': top_item['item_id']
                            }
                
                enhanced_data['collectible_markets'][market] = {
                    'items_found': len(items),
                    'sample_items': items[:3]  # Top 3 results
                }
        
        enhanced_data['collectible_summary']['total_items_found'] = total_items
        enhanced_data['collectible_summary']['highest_value_item'] = highest_value_item
        
        # Determine collectible demand
        if total_items == 0:
            demand = "No Collectible Data"
        elif total_items < 5:
            demand = "Low Collectible Interest"
        elif total_items < 15:
            demand = "Moderate Collectible Interest"
        else:
            demand = "High Collectible Interest"
        
        enhanced_data['collectible_summary']['collectible_demand_indicator'] = demand
        
        return enhanced_data
    
    def compare_format_values(self, movie_title: str, vhs_price: float, dvd_price: float) -> Dict:
        """
        Compare traditional movie format prices with collectible market values
        """
        collectible_data = self.get_enhanced_movie_pricing(movie_title)
        
        comparison = {
            'movie_title': movie_title,
            'traditional_formats': {
                'vhs_price': vhs_price,
                'dvd_price': dvd_price,
                'highest_traditional': max(vhs_price, dvd_price)
            },
            'collectible_context': collectible_data['collectible_summary'],
            'value_comparison': {
                'collectibles_found': collectible_data['collectible_summary']['total_items_found'] > 0,
                'collectible_premium': None,
                'investment_potential': 'Unknown'
            }
        }
        
        highest_collectible = collectible_data['collectible_summary']['highest_value_item']
        if highest_collectible and highest_collectible['fmv']:
            highest_traditional = max(vhs_price, dvd_price)
            collectible_value = highest_collectible['fmv'] / 100  # Convert cents to dollars
            
            premium = ((collectible_value - highest_traditional) / highest_traditional * 100) if highest_traditional > 0 else 0
            
            comparison['value_comparison']['collectible_premium'] = round(premium, 1)
            
            if premium > 500:
                investment_potential = "Very High - Significant collectible premium"
            elif premium > 200:
                investment_potential = "High - Strong collectible market"
            elif premium > 50:
                investment_potential = "Moderate - Some collectible interest"
            else:
                investment_potential = "Low - Traditional formats preferred"
            
            comparison['value_comparison']['investment_potential'] = investment_potential
        
        return comparison