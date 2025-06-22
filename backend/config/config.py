# backend/config/config.py
"""
Film Price Guide - Configuration Management
Handles environment variables and application settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Application Settings
    APP_NAME = os.getenv('APP_NAME', 'Film Price Guide')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@yoursite.com')
    
    # Database Configuration
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'mysql')
    DATABASE_URL = os.getenv('DATABASE_URL', 'mysql://root:password@localhost:3306/film_price_guide')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 10
    }
    
    # eBay API Configuration
    EBAY_APP_ID = os.getenv('EBAY_APP_ID')
    EBAY_CERT_ID = os.getenv('EBAY_CERT_ID')
    EBAY_DEV_ID = os.getenv('EBAY_DEV_ID')
    EBAY_USER_TOKEN = os.getenv('EBAY_USER_TOKEN')
    EBAY_ENVIRONMENT = os.getenv('EBAY_ENVIRONMENT', 'sandbox')
    EBAY_BASE_URL = 'https://api.ebay.com' if EBAY_ENVIRONMENT == 'production' else 'https://api.sandbox.ebay.com'
    
    # eBay Feature Flags
    ENABLE_PRICE_UPDATES = os.getenv('ENABLE_PRICE_UPDATES', 'True').lower() == 'true'
    ENABLE_RATE_LIMITING = os.getenv('ENABLE_RATE_LIMITING', 'True').lower() == 'true'
    UPDATE_FREQUENCY = os.getenv('UPDATE_FREQUENCY', 'daily')
    MAX_ITEMS_PER_SEARCH = int(os.getenv('MAX_ITEMS_PER_SEARCH', '100'))
    
    # eBay Deletion Notifications
    EBAY_VERIFICATION_TOKEN = os.getenv('EBAY_VERIFICATION_TOKEN')
    EBAY_DELETION_ENDPOINT_URL = os.getenv('EBAY_DELETION_ENDPOINT_URL')
    
    # OMDb API Configuration
    OMDB_API_KEY = os.getenv('OMDB_API_KEY')
    OMDB_PLAN_TYPE = os.getenv('OMDB_PLAN_TYPE', 'free')
    OMDB_BASE_URL = os.getenv('OMDB_BASE_URL', 'http://www.omdbapi.com/')
    OMDB_POSTER_URL = os.getenv('OMDB_POSTER_URL', 'http://img.omdbapi.com/')
    OMDB_RESPONSE_FORMAT = os.getenv('OMDB_RESPONSE_FORMAT', 'json')
    
    # OMDb Feature Flags
    ENABLE_MOVIE_ENRICHMENT = os.getenv('ENABLE_MOVIE_ENRICHMENT', 'True').lower() == 'true'
    ENABLE_POSTER_DOWNLOAD = os.getenv('ENABLE_POSTER_DOWNLOAD', 'True').lower() == 'true'
    ENABLE_IMDB_INTEGRATION = os.getenv('ENABLE_IMDB_INTEGRATION', 'False').lower() == 'true'
    
    # TMDb API Configuration
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    TMDB_API_VERSION = os.getenv('TMDB_API_VERSION', '3')
    TMDB_BASE_URL = os.getenv('TMDB_BASE_URL', 'https://api.themoviedb.org/3/')
    TMDB_IMAGE_URL = os.getenv('TMDB_IMAGE_URL', 'https://image.tmdb.org/t/p/')
    TMDB_LANGUAGE = os.getenv('TMDB_LANGUAGE', 'en-US')
    TMDB_IMAGE_QUALITY = os.getenv('TMDB_IMAGE_QUALITY', 'w500')
    
    # TMDb Feature Flags
    ENABLE_TMDB_ENRICHMENT = os.getenv('ENABLE_TMDB_ENRICHMENT', 'True').lower() == 'true'
    ENABLE_TMDB_IMAGES = os.getenv('ENABLE_TMDB_IMAGES', 'True').lower() == 'true'
    ENABLE_TMDB_VIDEOS = os.getenv('ENABLE_TMDB_VIDEOS', 'False').lower() == 'true'
    ENABLE_TMDB_CREDITS = os.getenv('ENABLE_TMDB_CREDITS', 'True').lower() == 'true'
    
    # General Feature Flags
    ENABLE_EMAIL_ALERTS = os.getenv('ENABLE_EMAIL_ALERTS', 'True').lower() == 'true'
    
    # Security Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    API_RATE_LIMIT_PER_HOUR = int(os.getenv('API_RATE_LIMIT_PER_HOUR', '1000'))
    
    # File Upload Settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Cache Settings (Redis)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'redis' if REDIS_URL else 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Email Configuration (for alerts)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', ADMIN_EMAIL)
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/film_price_guide.log')
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings"""
        missing_vars = []
        
        # Check critical eBay settings
        if not cls.EBAY_APP_ID:
            missing_vars.append('EBAY_APP_ID')
        if not cls.EBAY_CERT_ID:
            missing_vars.append('EBAY_CERT_ID')
        if not cls.EBAY_DEV_ID:
            missing_vars.append('EBAY_DEV_ID')
        
        # Check database URL
        if not cls.DATABASE_URL or cls.DATABASE_URL == 'mysql://root:password@localhost:3306/film_price_guide':
            missing_vars.append('DATABASE_URL (using default)')
        
        # Check deletion notification settings if eBay API is configured
        if cls.EBAY_APP_ID and not cls.EBAY_VERIFICATION_TOKEN:
            missing_vars.append('EBAY_VERIFICATION_TOKEN (required for eBay compliance)')
        
        return missing_vars
    
    @classmethod
    def get_api_status(cls):
        """Get status of configured APIs"""
        return {
            'ebay': {
                'configured': bool(cls.EBAY_APP_ID and cls.EBAY_CERT_ID and cls.EBAY_DEV_ID),
                'environment': cls.EBAY_ENVIRONMENT,
                'features': {
                    'price_updates': cls.ENABLE_PRICE_UPDATES,
                    'rate_limiting': cls.ENABLE_RATE_LIMITING
                }
            },
            'omdb': {
                'configured': bool(cls.OMDB_API_KEY),
                'plan': cls.OMDB_PLAN_TYPE,
                'features': {
                    'movie_enrichment': cls.ENABLE_MOVIE_ENRICHMENT,
                    'poster_download': cls.ENABLE_POSTER_DOWNLOAD,
                    'imdb_integration': cls.ENABLE_IMDB_INTEGRATION
                }
            },
            'tmdb': {
                'configured': bool(cls.TMDB_API_KEY),
                'version': cls.TMDB_API_VERSION,
                'features': {
                    'enrichment': cls.ENABLE_TMDB_ENRICHMENT,
                    'images': cls.ENABLE_TMDB_IMAGES,
                    'videos': cls.ENABLE_TMDB_VIDEOS,
                    'credits': cls.ENABLE_TMDB_CREDITS
                }
            }
        }

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # Log SQL queries in development

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting is more strict in production
    API_RATE_LIMIT_PER_HOUR = int(os.getenv('API_RATE_LIMIT_PER_HOUR', '500'))

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable external API calls during testing
    ENABLE_PRICE_UPDATES = False
    ENABLE_EMAIL_ALERTS = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}