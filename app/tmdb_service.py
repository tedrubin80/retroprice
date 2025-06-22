# backend/services/tmdb_service.py
"""
TMDb API Service Class
Handles The Movie Database API interactions for comprehensive film data
"""

import requests
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

from config.config import Config

logger = logging.getLogger(__name__)

class TmdbService:
    """Service class for TMDb API operations"""
    
    def __init__(self):
        self.api_key = Config.TMDB_API_KEY
        self.api_version = Config.TMDB_API_VERSION
        self.base_url = Config.TMDB_BASE_URL
        self.image_base_url = Config.TMDB_IMAGE_URL
        self.language = Config.TMDB_LANGUAGE
        self.image_quality = Config.TMDB_IMAGE_QUALITY
        
        # Rate limiting (40 requests per 10 seconds for free accounts)
        self.max_requests_per_window = 40
        self.window_duration = 10  # seconds
        self.request_timestamps = []
        
        # Image configuration cache
        self._image_config = None
        self._image_config_expires = None
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate TMDb API configuration"""
        if not self.api_key:
            raise ValueError("TMDb API key not configured")
        
        logger.info(f"TMDb API Service initialized - Version: {self.api_version}, Language: {self.language}")
    
    def _rate_limit(self):
        """Apply rate limiting for TMDb API (40 requests per 10 seconds)"""
        current_time = time.time()
        
        # Remove timestamps older than window duration
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if current_time - ts < self.window_duration
        ]
        
        # Check if we're at the limit
        if len(self.request_timestamps) >= self.max_requests_per_window:
            sleep_time = self.window_duration - (current_time - self.request_timestamps[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        # Add current request timestamp
        self.request_timestamps.append(current_time)
    
    def _make_api_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make authenticated request to TMDb API
        """
        try:
            # Apply rate limiting
            if Config.ENABLE_RATE_LIMITING:
                self._rate_limit()
            
            # Prepare headers
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Prepare parameters
            api_params = params or {}
            api_params['language'] = api_params.get('language', self.language)
            
            # Build URL
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
            
            # Make request
            response = requests.get(url, headers=headers, params=api_params, timeout=10)
            
            # Log request for debugging
            logger.info(f"TMDb API request: {response.url}")
            logger.info(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"TMDb API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDb API request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in TMDb API request: {str(e)}")
            raise
    
    def get_image_configuration(self) -> Dict[str, Any]:
        """
        Get TMDb image configuration (cached for performance)
        Required to build proper image URLs
        """
        try:
            # Check cache first
            if (self._image_config and self._image_config_expires and 
                datetime.utcnow() < self._image_config_expires):
                return self._image_config
            
            logger.info("Fetching TMDb image configuration")
            
            config_data = self._make_api_request('configuration')
            self._image_config = config_data.get('images', {})
            
            # Cache for 24 hours
            self._image_config_expires = datetime.utcnow() + timedelta(hours=24)
            
            logger.info("TMDb image configuration cached successfully")
            return self._image_config
            
        except Exception as e:
            logger.error(f"Error fetching TMDb image configuration: {str(e)}")
            # Return default configuration if fetch fails
            return {
                'base_url': 'https://image.tmdb.org/t/p/',
                'poster_sizes': ['w154', 'w185', 'w342', 'w500', 'w780', 'original'],
                'backdrop_sizes': ['w300', 'w780', 'w1280', 'original']
            }
    
    def build_image_url(self, image_path: str, image_type: str = 'poster', 
                       size: Optional[str] = None) -> Optional[str]:
        """
        Build complete image URL from TMDb image path
        
        Args:
            image_path: Image path from TMDb API
            image_type: Type of image ('poster', 'backdrop', 'profile')
            size: Image size (uses config default if not specified)
        
        Returns:
            Complete image URL or None if invalid
        """
        if not image_path:
            return None
        
        try:
            config = self.get_image_configuration()
            base_url = config.get('base_url', self.image_base_url)
            
            # Select appropriate size
            if not size:
                if image_type == 'poster':
                    size = self.image_quality
                elif image_type == 'backdrop':
                    size = 'w1280'
                else:
                    size = 'w500'
            
            return f"{base_url}{size}{image_path}"
            
        except Exception as e:
            logger.error(f"Error building image URL: {str(e)}")
            return f"{self.image_base_url}{self.image_quality}{image_path}"
    
    def search_movies(self, query: str, year: Optional[int] = None, 
                     page: int = 1) -> Dict[str, Any]:
        """
        Search for movies by title
        
        Args:
            query: Movie title to search for
            year: Optional release year
            page: Page number for pagination
        
        Returns:
            Dictionary containing search results
        """
        try:
            logger.info(f"Searching TMDb for: {query}")
            
            params = {
                'query': query,
                'page': page,
                'include_adult': False
            }
            
            if year:
                params['year'] = year
            
            data = self._make_api_request('search/movie', params)
            
            # Process search results
            processed_results = {
                'success': True,
                'page': data.get('page', 1),
                'total_pages': data.get('total_pages', 1),
                'total_results': data.get('total_results', 0),
                'search_query': query,
                'search_year': year,
                'movies': []
            }
            
            # Process each movie in results
            for movie in data.get('results', []):
                processed_movie = self._process_search_result(movie)
                processed_results['movies'].append(processed_movie)
            
            logger.info(f"TMDb search completed: {len(processed_results['movies'])} results on page {page}")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in TMDb search: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_movie_details(self, movie_id: int, append_to_response: str = '') -> Dict[str, Any]:
        """
        Get detailed movie information by TMDb ID
        
        Args:
            movie_id: TMDb movie ID
            append_to_response: Additional data to include (credits, videos, images)
        
        Returns:
            Dictionary containing detailed movie data
        """
        try:
            logger.info(f"Getting TMDb details for movie ID: {movie_id}")
            
            params = {}
            if append_to_response:
                params['append_to_response'] = append_to_response
            
            data = self._make_api_request(f'movie/{movie_id}', params)
            
            # Process detailed movie data
            movie_data = self._process_movie_details(data)
            
            logger.info(f"TMDb movie details retrieved for: {movie_data.get('title', 'Unknown')}")
            return {'success': True, 'movie': movie_data}
            
        except Exception as e:
            logger.error(f"Error getting TMDb movie details: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_movie_credits(self, movie_id: int) -> Dict[str, Any]:
        """Get movie cast and crew information"""
        try:
            data = self._make_api_request(f'movie/{movie_id}/credits')
            
            processed_credits = {
                'cast': [self._process_cast_member(person) for person in data.get('cast', [])[:10]],  # Top 10 cast
                'crew': [self._process_crew_member(person) for person in data.get('crew', []) 
                        if person.get('job') in ['Director', 'Producer', 'Writer', 'Screenplay']]
            }
            
            return {'success': True, 'credits': processed_credits}
            
        except Exception as e:
            logger.error(f"Error getting TMDb movie credits: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_movie_images(self, movie_id: int) -> Dict[str, Any]:
        """Get movie posters and backdrops"""
        try:
            data = self._make_api_request(f'movie/{movie_id}/images')
            
            processed_images = {
                'posters': [self._process_image(img, 'poster') for img in data.get('posters', [])[:5]],
                'backdrops': [self._process_image(img, 'backdrop') for img in data.get('backdrops', [])[:5]]
            }
            
            return {'success': True, 'images': processed_images}
            
        except Exception as e:
            logger.error(f"Error getting TMDb movie images: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_movie_videos(self, movie_id: int) -> Dict[str, Any]:
        """Get movie trailers and videos"""
        try:
            data = self._make_api_request(f'movie/{movie_id}/videos')
            
            videos = []
            for video in data.get('results', []):
                if video.get('site') == 'YouTube':  # Focus on YouTube videos
                    videos.append(self._process_video(video))
            
            return {'success': True, 'videos': videos[:10]}  # Limit to 10 videos
            
        except Exception as e:
            logger.error(f"Error getting TMDb movie videos: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _process_search_result(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        """Process movie data from search results"""
        return {
            'tmdb_id': movie.get('id'),
            'title': movie.get('title'),
            'original_title': movie.get('original_title'),
            'release_date': movie.get('release_date'),
            'year': self._extract_year(movie.get('release_date')),
            'overview': movie.get('overview'),
            'popularity': movie.get('popularity'),
            'vote_average': movie.get('vote_average'),
            'vote_count': movie.get('vote_count'),
            'adult': movie.get('adult'),
            'poster_url': self.build_image_url(movie.get('poster_path'), 'poster'),
            'backdrop_url': self.build_image_url(movie.get('backdrop_path'), 'backdrop'),
            'genre_ids': movie.get('genre_ids', [])
        }
    
    def _process_movie_details(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        """Process detailed movie data"""
        processed = {
            'tmdb_id': movie.get('id'),
            'title': movie.get('title'),
            'original_title': movie.get('original_title'),
            'tagline': movie.get('tagline'),
            'overview': movie.get('overview'),
            'release_date': movie.get('release_date'),
            'year': self._extract_year(movie.get('release_date')),
            'runtime': movie.get('runtime'),
            'budget': movie.get('budget'),
            'revenue': movie.get('revenue'),
            'status': movie.get('status'),
            'popularity': movie.get('popularity'),
            'vote_average': movie.get('vote_average'),
            'vote_count': movie.get('vote_count'),
            'adult': movie.get('adult'),
            'homepage': movie.get('homepage'),
            'imdb_id': movie.get('imdb_id'),
            'original_language': movie.get('original_language'),
            'poster_url': self.build_image_url(movie.get('poster_path'), 'poster'),
            'backdrop_url': self.build_image_url(movie.get('backdrop_path'), 'backdrop'),
            'genres': [genre.get('name') for genre in movie.get('genres', [])],
            'production_companies': [company.get('name') for company in movie.get('production_companies', [])],
            'production_countries': [country.get('name') for country in movie.get('production_countries', [])],
            'spoken_languages': [lang.get('english_name', lang.get('name')) for lang in movie.get('spoken_languages', [])]
        }
        
        # Process appended data if available
        if 'credits' in movie:
            processed['credits'] = self._process_credits_data(movie['credits'])
        
        if 'videos' in movie:
            processed['videos'] = [self._process_video(video) for video in movie['videos'].get('results', [])[:5]]
        
        if 'images' in movie:
            processed['additional_images'] = {
                'posters': [self._process_image(img, 'poster') for img in movie['images'].get('posters', [])[:3]],
                'backdrops': [self._process_image(img, 'backdrop') for img in movie['images'].get('backdrops', [])[:3]]
            }
        
        # Add metadata
        processed['tmdb_metadata'] = {
            'fetched_at': datetime.utcnow().isoformat(),
            'language': self.language,
            'data_completeness': self._calculate_completeness(processed)
        }
        
        return processed
    
    def _process_credits_data(self, credits: Dict[str, Any]) -> Dict[str, Any]:
        """Process credits data from movie details"""
        return {
            'cast': [self._process_cast_member(person) for person in credits.get('cast', [])[:10]],
            'crew': [self._process_crew_member(person) for person in credits.get('crew', []) 
                    if person.get('job') in ['Director', 'Producer', 'Writer', 'Screenplay']]
        }
    
    def _process_cast_member(self, person: Dict[str, Any]) -> Dict[str, Any]:
        """Process cast member data"""
        return {
            'name': person.get('name'),
            'character': person.get('character'),
            'order': person.get('order'),
            'profile_url': self.build_image_url(person.get('profile_path'), 'profile')
        }
    
    def _process_crew_member(self, person: Dict[str, Any]) -> Dict[str, Any]:
        """Process crew member data"""
        return {
            'name': person.get('name'),
            'job': person.get('job'),
            'department': person.get('department'),
            'profile_url': self.build_image_url(person.get('profile_path'), 'profile')
        }
    
    def _process_image(self, image: Dict[str, Any], image_type: str) -> Dict[str, Any]:
        """Process image data"""
        return {
            'file_path': image.get('file_path'),
            'aspect_ratio': image.get('aspect_ratio'),
            'height': image.get('height'),
            'width': image.get('width'),
            'vote_average': image.get('vote_average'),
            'vote_count': image.get('vote_count'),
            'url': self.build_image_url(image.get('file_path'), image_type),
            'high_res_url': self.build_image_url(image.get('file_path'), image_type, 'original')
        }
    
    def _process_video(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """Process video data"""
        video_data = {
            'key': video.get('key'),
            'name': video.get('name'),
            'site': video.get('site'),
            'type': video.get('type'),
            'official': video.get('official'),
            'published_at': video.get('published_at')
        }
        
        # Build YouTube URL
        if video.get('site') == 'YouTube' and video.get('key'):
            video_data['url'] = f"https://www.youtube.com/watch?v={video['key']}"
            video_data['embed_url'] = f"https://www.youtube.com/embed/{video['key']}"
        
        return video_data
    
    def _extract_year(self, release_date: str) -> Optional[int]:
        """Extract year from release date string"""
        if not release_date:
            return None
        try:
            return int(release_date.split('-')[0])
        except (ValueError, IndexError):
            return None
    
    def _calculate_completeness(self, movie_data: Dict[str, Any]) -> float:
        """Calculate data completeness percentage"""
        important_fields = [
            'title', 'overview', 'release_date', 'runtime', 
            'genres', 'poster_url', 'vote_average', 'production_companies'
        ]
        
        filled_fields = sum(1 for field in important_fields if movie_data.get(field))
        return round((filled_fields / len(important_fields)) * 100, 1)
    
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
            # Search for the movie
            search_result = self.search_movies(film_title, year=film_year)
            
            if not search_result['success'] or not search_result['movies']:
                return {'success': False, 'error': 'No matching movie found in TMDb'}
            
            # Get the best match (first result)
            best_match = search_result['movies'][0]
            movie_id = best_match.get('tmdb_id')
            
            if not movie_id:
                return {'success': False, 'error': 'No valid movie ID found'}
            
            # Get detailed information with credits and videos
            detailed_result = self.get_movie_details(
                movie_id, 
                append_to_response='credits,videos,images'
            )
            
            return detailed_result
            
        except Exception as e:
            logger.error(f"Error enriching film data with TMDb: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def download_image(self, image_url: str, save_path: str) -> bool:
        """
        Download image from TMDb
        
        Args:
            image_url: URL of the image
            save_path: Local path to save the image
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not image_url:
                return False
            
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Image downloaded successfully: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            return False
    
    def health_check(self) -> bool:
        """
        Check if TMDb API is accessible and API key is valid
        """
        try:
            # Make a simple test request
            self.get_image_configuration()
            return True
            
        except Exception as e:
            logger.error(f"TMDb API health check failed: {str(e)}")
            return False
    
    def get_api_usage(self) -> Dict[str, Any]:
        """Get current API usage statistics"""
        current_time = time.time()
        recent_requests = [
            ts for ts in self.request_timestamps 
            if current_time - ts < self.window_duration
        ]
        
        return {
            'max_requests_per_window': self.max_requests_per_window,
            'window_duration_seconds': self.window_duration,
            'requests_in_current_window': len(recent_requests),
            'requests_remaining': self.max_requests_per_window - len(recent_requests),
            'api_version': self.api_version,
            'language': self.language
        }
    
    def batch_enrich_films(self, films: List[Dict[str, Any]], 
                          delay_between_requests: float = 0.3) -> List[Dict[str, Any]]:
        """
        Batch enrich multiple films with TMDb data
        
        Args:
            films: List of film dictionaries with 'title' and optionally 'year'
            delay_between_requests: Delay between requests
        
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
                
                # Add delay between requests for rate limiting
                if i < len(films) - 1:
                    time.sleep(delay_between_requests)
                
            except Exception as e:
                logger.error(f"Error enriching film {film.get('title')}: {str(e)}")
                enriched_films.append({
                    'original_film': film,
                    'enriched_data': {'success': False, 'error': str(e)},
                    'success': False
                })
        
        logger.info(f"TMDb batch enrichment completed: {len(enriched_films)} films processed")
        return enriched_films
    
    def get_popular_movies(self, page: int = 1) -> Dict[str, Any]:
        """Get popular movies from TMDb"""
        try:
            data = self._make_api_request('movie/popular', {'page': page})
            
            return {
                'success': True,
                'page': data.get('page', 1),
                'total_pages': data.get('total_pages', 1),
                'total_results': data.get('total_results', 0),
                'movies': [self._process_search_result(movie) for movie in data.get('results', [])]
            }
            
        except Exception as e:
            logger.error(f"Error getting popular movies: {str(e)}")
            return {'success': False, 'error': str(e)}