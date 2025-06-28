#!/usr/bin/env python3
"""
Film Price Guide - Database Service
Handles MySQL database connections and operations
"""

import mysql.connector
from mysql.connector import Error, pooling
import logging
import os
from contextlib import contextmanager
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database service for MySQL operations"""
    
    def __init__(self, database_url=None):
        self.database_url = database_url or os.environ.get('DATABASE_URL')
        self.connection_pool = None
        self._init_connection_pool()
    
    def _parse_database_url(self, database_url):
        """Parse database URL into connection parameters"""
        if not database_url:
            raise ValueError("Database URL is required")
        
        if database_url.startswith('mysql://'):
            parsed = urlparse(database_url)
            return {
                'host': parsed.hostname,
                'port': parsed.port or 3306,
                'user': parsed.username,
                'password': parsed.password,
                'database': parsed.path.lstrip('/'),
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci'
            }
        else:
            # Assume it's already a connection dict or string
            return database_url
    
    def _init_connection_pool(self):
        """Initialize connection pool"""
        try:
            db_config = self._parse_database_url(self.database_url)
            
            # Add pool-specific configuration
            pool_config = {
                **db_config,
                'pool_name': 'film_price_guide_pool',
                'pool_size': 5,
                'pool_reset_session': True,
                'autocommit': True,
                'time_zone': '+00:00'
            }
            
            self.connection_pool = pooling.MySQLConnectionPool(**pool_config)
            logger.info("✅ Database connection pool initialized")
            
        except Error as e:
            logger.error(f"❌ Failed to create connection pool: {e}")
            self.connection_pool = None
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        connection = None
        try:
            if self.connection_pool:
                connection = self.connection_pool.get_connection()
            else:
                # Fallback to direct connection
                db_config = self._parse_database_url(self.database_url)
                connection = mysql.connector.connect(**db_config)
            
            yield connection
            
        except Error as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                return True, "Database connection successful"
        except Error as e:
            return False, f"Database connection failed: {e}"
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a database query"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                
                if fetch:
                    if 'SELECT' in query.upper():
                        result = cursor.fetchall()
                    else:
                        result = cursor.fetchone()
                else:
                    result = cursor.rowcount
                
                cursor.close()
                return True, result
                
        except Error as e:
            logger.error(f"Query execution error: {e}")
            return False, str(e)
    
    def get_user_by_email(self, email):
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s AND is_active = 1"
        success, result = self.execute_query(query, (email,), fetch=True)
        return result[0] if success and result else None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = %s AND is_active = 1"
        success, result = self.execute_query(query, (username,), fetch=True)
        return result[0] if success and result else None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = %s AND is_active = 1"
        success, result = self.execute_query(query, (user_id,), fetch=True)
        return result[0] if success and result else None
    
    def create_user(self, user_data):
        """Create a new user"""
        query = """
        INSERT INTO users (username, email, password_hash, first_name, last_name, created_at)
        VALUES (%(username)s, %(email)s, %(password_hash)s, %(first_name)s, %(last_name)s, %(created_at)s)
        """
        success, result = self.execute_query(query, user_data)
        return success, result
    
    def update_user_login(self, user_id):
        """Update user's last login timestamp"""
        query = "UPDATE users SET last_login = NOW() WHERE id = %s"
        return self.execute_query(query, (user_id,))
    
    def search_films(self, search_term, format_filter=None, limit=50):
        """Search for films in database"""
        query = """
        SELECT f.*, 
               COUNT(ph.id) as price_count,
               MIN(ph.price) as min_price,
               MAX(ph.price) as max_price,
               AVG(ph.price) as avg_price
        FROM films f
        LEFT JOIN price_history ph ON f.id = ph.film_id
        WHERE (f.title LIKE %s OR f.director LIKE %s OR f.year LIKE %s)
        """
        
        params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
        
        if format_filter:
            query += " AND f.format = %s"
            params.append(format_filter)
        
        query += " GROUP BY f.id ORDER BY f.title LIMIT %s"
        params.append(limit)
        
        success, result = self.execute_query(query, params, fetch=True)
        return result if success else []
    
    def get_film_by_id(self, film_id):
        """Get film details by ID"""
        query = """
        SELECT f.*, 
               COUNT(ph.id) as price_count,
               MIN(ph.price) as min_price,
               MAX(ph.price) as max_price,
               AVG(ph.price) as avg_price
        FROM films f
        LEFT JOIN price_history ph ON f.id = ph.film_id
        WHERE f.id = %s
        GROUP BY f.id
        """
        success, result = self.execute_query(query, (film_id,), fetch=True)
        return result[0] if success and result else None
    
    def get_price_history(self, film_id, limit=100):
        """Get price history for a film"""
        query = """
        SELECT * FROM price_history 
        WHERE film_id = %s 
        ORDER BY sale_date DESC 
        LIMIT %s
        """
        success, result = self.execute_query(query, (film_id, limit), fetch=True)
        return result if success else []
    
    def add_price_entry(self, price_data):
        """Add a new price entry"""
        query = """
        INSERT INTO price_history (
            film_id, price, shipping_cost, condition_name, sale_date,
            platform, listing_url, ebay_item_id
        ) VALUES (
            %(film_id)s, %(price)s, %(shipping_cost)s, %(condition_name)s,
            %(sale_date)s, %(platform)s, %(listing_url)s, %(ebay_item_id)s
        )
        """
        return self.execute_query(query, price_data)
    
    def get_user_watchlist(self, user_id):
        """Get user's watchlist"""
        query = """
        SELECT w.*, f.title, f.year, f.format, f.poster_url
        FROM watchlist w
        JOIN films f ON w.film_id = f.id
        WHERE w.user_id = %s AND w.status = 'Active'
        ORDER BY w.created_at DESC
        """
        success, result = self.execute_query(query, (user_id,), fetch=True)
        return result if success else []
    
    def add_to_watchlist(self, user_id, film_id, target_price=None):
        """Add film to user's watchlist"""
        query = """
        INSERT INTO watchlist (user_id, film_id, target_price, created_at)
        VALUES (%s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE 
        target_price = VALUES(target_price),
        status = 'Active',
        updated_at = NOW()
        """
        return self.execute_query(query, (user_id, film_id, target_price))
    
    def remove_from_watchlist(self, user_id, film_id):
        """Remove film from user's watchlist"""
        query = "UPDATE watchlist SET status = 'Removed' WHERE user_id = %s AND film_id = %s"
        return self.execute_query(query, (user_id, film_id))
    
    def get_api_keys(self):
        """Get stored API keys (for admin use)"""
        # This would require an api_keys table in your schema
        query = "SELECT * FROM api_keys WHERE is_active = 1"
        success, result = self.execute_query(query, fetch=True)
        return result if success else []
    
    def save_api_key(self, api_name, api_key, api_secret=None):
        """Save API key"""
        query = """
        INSERT INTO api_keys (api_name, api_key, api_secret, created_at)
        VALUES (%s, %s, %s, NOW())
        ON DUPLICATE KEY UPDATE 
        api_key = VALUES(api_key),
        api_secret = VALUES(api_secret),
        updated_at = NOW()
        """
        return self.execute_query(query, (api_name, api_key, api_secret))

# Global database instance
db_service = None

def init_database(database_url=None):
    """Initialize global database service"""
    global db_service
    db_service = DatabaseService(database_url)
    return db_service

def get_db():
    """Get database service instance"""
    global db_service
    if not db_service:
        db_service = DatabaseService()
    return db_service