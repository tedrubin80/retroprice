# backend/services/omdb_service.py
"""
OMDb API Service Class
Handles The Open Movie Database API interactions for film metadata
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from config.config import Config

logger = logging.getLogger(__name__)

class OmdbService:
    """Service class for OMDb API operations"""
    
    def __init__(self):
        self.api_key = Config.OMDB_API_KEY
        self.plan_type = Config.OMDB_PLAN_TYPE
        self.base_url = Config.OMDB_BASE_URL
        self.poster_url = Config.OMDB_POSTER_URL
        self.response_format = Config.OMDB_RESPONSE_FORMAT
        
        # Rate limiting based on plan
        self.daily_limit = 1000 if self.plan_type == 'free' else 100000
        self.requests_made_today = 0
        self.last_reset_date = datetime.utcnow().date()
        
        # Request timing
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
        # Validate configuration
        self._validate_config()
        
        # Reset daily counter if needed
        self._check_daily_reset()
    
    def _validate_config(self):
        """Validate OMDb API configuration"""
        if not self.api_key:
            raise ValueError("OMDb API key not configured")
        
        logger.info(f"OMDb API Service initialized - Plan: {self.plan_type}")
    
    def _check_daily_reset(self):
        """Reset daily request counter if date has changed"""
        current_date = datetime.utcnow().date()
        if current_date > self.last_reset_date:
            self.requests_made_today = 0
            self.last_reset_date = current_date
            logger.info("OMDb daily request counter reset")
    
    def _rate_limit(self):
        """Apply rate limiting between API requests"""
        # Check daily limit
        self._check_daily_reset()
        if self.requests_made_today >= self.daily_limit:
            raise Exception(f"OMDb daily limit of {self.daily_limit} requests exceeded")
        
        # Apply timing limit
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.requests_made_today += 1
    
    def _make_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make authenticated request to OMDb API
        """
        try:
            # Apply rate limiting
            if Config.ENABLE_RATE_LIMITING:
                self._rate_limit()
            
            # Add API key to parameters
            api_params = params.copy()
            api_params['apikey'] = self.api_key
            api_params['r'] = self.response_format
            
            # Make request
            response = requests.get(self.base_url, params=api_params, timeout=10)
            
            # Log request for debugging
            logger.info(f"OMDb API request: {response.url}")
            logger.info(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            
            # Check for OMDb API errors
            if data.get('Response') == 'False':
                error_msg = data.get('Error', 'Unknown OMDb error')
                logger.warning(f"OMDb API error: {error_msg}")
                return {'success': False, 'error': error_msg}
            
            return {'success': True, 'data': data}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OMDb API request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in OMDb API request: {str(e)}")
            raise
    
    def search_movies(self, title: str, year: Optional[int] = None, 
                     movie_type: str = 'movie') -> Dict[str, Any]:
        """
        Search for movies by title
        
        Args:
            title: Movie title to search for
            year: Optional release year
            movie_type: Type of result (movie, series, episode)
        
        Returns:
            Dictionary containing search results
        """
        try:
            logger.info(f"Searching OMDb for: {title}")
            
            params = {
                's': title,
                'type': movie_type
            }
            
            if year:
                params['y'] = str(year)
            
            result = self._make_api_request(params)
            
            if not result['success']:
                return result
            
            data = result['data']
            
            # Process search results
            processed_results = {
                'success': True,
                'total_results': int(data.get('totalResults', 0)),
                'search_query': title,
                'search_year': year,
                'movies': []
            }
            
            # Process each movie in results
            for movie in data.get('Search', []):
                processed_movie = self._process_movie_data(movie)
                processed_results['movies'].append(processed_movie)
            
            logger.info(f"OMDb search completed: {len(processed_results['movies'])} results")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in OMDb search: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_movie_by_id(self, imdb_id: str, plot: str = 'short') -> Dict[str, Any]:
        """
        Get detailed movie information by IMDb ID
        
        Args:
            imdb_id: IMDb ID (e.g., tt0107290)
            plot: Plot length ('short' or 'full')
        
        Returns:
            Dictionary containing detailed movie data
        """
        try:
            logger.info(f"Getting OMDb details for IMDb ID: {imdb_id}")
            
            params = {
                'i': imdb_id,
                'plot': plot
            }
            
            result = self._make_api_request(params)
            
            if not result['success']:
                return result
            
            # Process detailed movie data
            movie_data = self._process_detailed_movie(result['data'])
            
            logger.info(f"OMDb movie details retrieved for: {movie_data.get('title', 'Unknown')}")
            return {'success': True, 'movie': movie_data}
            
        except Exception as e:
            logger.error(f"Error getting OMDb movie details: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_movie_by_title(self, title: str, year: Optional[int] = None, 
                          plot: str = 'short') -> Dict[str, Any]:
        """
        Get detailed movie information by title
        
        Args:
            title: Movie title
            year: Optional release year for precision
            plot: Plot length ('short' or 'full')
        
        Returns:
            Dictionary containing detailed movie data
        """
        try:
            logger.info(f"Getting OMDb details for title: {title}")
            
            params = {
                't': title,
                'plot': plot
            }
            
            if year:
                params['y'] = str(year)
            
            result = self._make_api_request(params)
            
            if not result['success']:
                return result
            
            # Process detailed movie data
            movie_data = self._process_detailed_movie(result['data'])
            
            logger.info(f"OMDb movie details retrieved for: {movie_data.get('title', 'Unknown')}")
            return {'success': True, 'movie': movie_data}
            
        except Exception as e:
            logger.error(f"Error getting OMDb movie by title: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _process_movie_data(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        """Process basic movie data from search results"""
        return {
            'title': movie.get('Title'),
            'year': self._safe_int(movie.get('Year')),
            'imdb_id': movie.get('imdbID'),
            'type': movie.get('Type'),
            'poster_url': movie.get('Poster') if movie.get('Poster') != 'N/A' else None
        }
    
    def _process_detailed_movie(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        """Process detailed movie data"""
        processed = {
            'title': movie.get('Title'),
            'year': self._safe_int(movie.get('Year')),
            'rated': movie.get('Rated'),
            'released': movie.get('Released'),
            'runtime': self._parse_runtime(movie.get('Runtime')),
            'genre': movie.get('Genre'),
            'director': movie.get('Director'),
            'writer': movie.get('Writer'),
            'actors': movie.get('Actors'),
            'plot': movie.get('Plot'),
            'language': movie.get('Language'),
            'country': movie.get('Country'),
            'awards': movie.get('Awards'),
            'poster_url': movie.get('Poster') if movie.get('Poster') != 'N/A' else None,
            'metascore': self._safe_int(movie.get('Metascore')),
            'imdb_rating': self._safe_float(movie.get('imdbRating')),
            'imdb_votes': self._parse_imdb_votes(movie.get('imdbVotes')),
            'imdb_id': movie.get('imdbID'),
            'type': movie.get('Type'),
            'dvd_release': movie.get('DVD'),
            'box_office': movie.get('BoxOffice'),
            'production': movie.get('Production'),
            'website': movie.get('Website'),
            'ratings': self._process_ratings(movie.get('Ratings', []))
        }
        
        # Add enhanced metadata
        processed['omdb_metadata'] = {
            'fetched_at': datetime.utcnow().isoformat(),
            'plot_type': 'full' if len(processed.get('plot', '')) > 200 else 'short',
            'has_poster': bool(processed['poster_url']),
            'data_completeness': self._calculate_completeness(processed)
        }
        
        return processed
    
    def _process_ratings(self, ratings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process movie ratings from different sources"""
        processed_ratings = {}
        
        for rating in ratings:
            source = rating.get('Source', '').lower()
            value = rating.get('Value', '')
            
            if 'imdb' in source:
                processed_ratings['imdb'] = value
            elif 'rotten tomatoes' in source:
                processed_ratings['rotten_tomatoes'] = value
            elif 'metacritic' in source:
                processed_ratings['metacritic'] = value
        
        return processed_ratings
    
    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert string to integer"""
        if not value or value == 'N/A':
            return None
        try:
            # Handle year ranges like "2019–2020"
            if '–' in str(value):
                value = str(value).split('–')[0]
            return int(str(value).strip())
        except (ValueError, TypeError):
            return None
    
    def _safe_float(self, value: str) -> Optional[float]:
        """Safely convert string to float"""
        if not value or value == 'N/A':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _parse_runtime(self, runtime: str) -> Optional[int]:
        """Parse runtime string to minutes"""
        if not runtime or runtime == 'N/A':
            return None
        try:
            # Extract number from "XX min" format
            import re
            match = re.search(r'(\d+)', runtime)
            return int(match.group(1)) if match else None
        except:
            return None
    
    def _parse_imdb_votes(self, votes: str) -> Optional[int]:
        """Parse IMDb votes string to integer"""
        if not votes or votes == 'N/A':
            return None
        try:
            # Remove commas and convert to int
            return int(votes.replace(',', ''))
        except (ValueError, TypeError):
            return None
    
    def _calculate_completeness(self, movie_data: Dict[str, Any]) -> float:
        """Calculate data completeness percentage"""
        total_fields = 20  # Important fields count
        filled_fields = 0
        
        important_fields = [
            'title', 'year', 'director', 'genre', 'plot', 
            'runtime', 'rated', 'imdb_rating', 'actors',
            'poster_url', 'language', 'country', 'released'
        ]
        
        for field in important_fields:
            if movie_data.get(field):
                filled_fields += 1
        
        return round((filled_fields / len(important_fields)) * 100, 1)
    
    def download_poster(self, poster_url: str, save_path: str) -> bool:
        """
        Download movie poster from OMDb
        
        Args:
            poster_url: URL of the poster image
            save_path: Local path to save the image
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not poster_url or poster_url == 'N/A':
                return False
            
            response = requests.get(poster_url, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Poster downloaded successfully: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading poster: {str(e)}")
            return False
    
    def enrich_film_data(self, film_title: str, film_year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get comprehensive film data for database enrichment
        
        Args:
            film_title: Title of the film
            film_year: Optional year for better matching
        
        Returns:
            Processed film data ready for database storage
        """
        try:
            # First try exact title match
            result = self.get_movie_by_title(film_title, year=film_year, plot='full')
            
            if result['success']:
                return result
            
            # If no exact match, try search and pick best result
            search_result = self.search_movies(film_title, year=film_year)
            
            if search_result['success'] and search_result['movies']:
                # Get detailed data for first result
                best_match = search_result['movies'][0]
                if best_match.get('imdb_id'):
                    return self.get_movie_by_id(best_match['imdb_id'], plot='full')
            
            return {'success': False, 'error': 'No matching movie found'}
            
        except Exception as e:
            logger.error(f"Error enriching film data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def health_check(self) -> bool:
        """
        Check if OMDb API is accessible and API key is valid
        """
        try:
            # Make a simple test request
            test_result = self.get_movie_by_id('tt0111161')  # The Shawshank Redemption
            return test_result['success']
            
        except Exception as e:
            logger.error(f"OMDb API health check failed: {str(e)}")
            return False
    
    def get_api_usage(self) -> Dict[str, Any]:
        """Get current API usage statistics"""
        return {
            'plan_type': self.plan_type,
            'daily_limit': self.daily_limit,
            'requests_made_today': self.requests_made_today,
            'requests_remaining': self.daily_limit - self.requests_made_today,
            'last_reset_date': self.last_reset_date.isoformat(),
            'rate_limit_interval': f"{self.min_request_interval * 1000}ms"
        }
    
    def batch_enrich_films(self, films: List[Dict[str, Any]], 
                          delay_between_requests: float = 0.5) -> List[Dict[str, Any]]:
        """
        Batch enrich multiple films with OMDb data
        
        Args:
            films: List of film dictionaries with 'title' and optionally 'year'
            delay_between_requests: Delay between requests to respect rate limits
        
        Returns:
            List of enriched film data
        """
        enriched_films = []
        
        for i, film in enumerate(films):
            try:
                logger.info(f"Enriching film {i+1}/{len(films)}: {film.get('title')}")
                
                result = self.enrich_film_data(
                    film.get('title'),
                    film.get('year')
                )
                
                enriched_films.append({
                    'original_film': film,
                    'enriched_data': result,
                    'success': result['success']
                })
                
                # Add delay between requests
                if i < len(films) - 1:  # Don't delay after last request
                    time.sleep(delay_between_requests)
                
            except Exception as e:
                logger.error(f"Error enriching film {film.get('title')}: {str(e)}")
                enriched_films.append({
                    'original_film': film,
                    'enriched_data': {'success': False, 'error': str(e)},
                    'success': False
                })
        
        logger.info(f"Batch enrichment completed: {len(enriched_films)} films processed")
        return enriched_films