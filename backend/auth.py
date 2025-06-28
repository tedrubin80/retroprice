#!/usr/bin/env python3
"""
Film Price Guide - Authentication System
Handles user authentication, session management, and security
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, session, current_app
import mysql.connector
from mysql.connector import Error
import bcrypt
import re

class AuthManager:
    """Handles user authentication and session management"""
    
    def __init__(self, db_config):
        self.db_config = db_config
    
    def get_db_connection(self):
        """Get database connection"""
        try:
            # Parse DATABASE_URL if it's in URL format
            if self.db_config.startswith('mysql://'):
                # Extract components from mysql://user:password@host:port/database
                parts = self.db_config.replace('mysql://', '').split('/')
                db_name = parts[1] if len(parts) > 1 else 'film_price_guide'
                
                user_host = parts[0].split('@')
                host_port = user_host[1].split(':')
                user_pass = user_host[0].split(':')
                
                connection = mysql.connector.connect(
                    host=host_port[0],
                    port=int(host_port[1]) if len(host_port) > 1 else 3306,
                    user=user_pass[0],
                    password=user_pass[1] if len(user_pass) > 1 else '',
                    database=db_name,
                    autocommit=True
                )
            else:
                # Direct connection parameters
                connection = mysql.connector.connect(**self.db_config)
            
            return connection
        except Error as e:
            current_app.logger.error(f"Database connection error: {e}")
            return None
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def validate_password(self, password):
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one number")
        
        # Optional special character requirement
        # if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        #     errors.append("Password must contain at least one special character")
        
        return errors
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def create_user(self, username, email, password, first_name=None, last_name=None):
        """Create a new user account"""
        
        # Validate inputs
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if not self.validate_email(email):
            return False, "Invalid email format"
        
        password_errors = self.validate_password(password)
        if password_errors:
            return False, "; ".join(password_errors)
        
        connection = self.get_db_connection()
        if not connection:
            return False, "Database connection failed"
        
        try:
            cursor = connection.cursor()
            
            # Check if username or email already exists
            cursor.execute(
                "SELECT id FROM users WHERE username = %s OR email = %s",
                (username, email)
            )
            
            if cursor.fetchone():
                return False, "Username or email already exists"
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            
            # Insert new user
            cursor.execute("""
                INSERT INTO users (
                    username, email, password_hash, first_name, last_name,
                    verification_token, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                username, email, hashed_password, first_name, last_name,
                verification_token, datetime.utcnow()
            ))
            
            user_id = cursor.lastrowid
            
            return True, {
                'user_id': user_id,
                'username': username,
                'email': email,
                'verification_token': verification_token,
                'message': 'User created successfully'
            }
            
        except Error as e:
            current_app.logger.error(f"Error creating user: {e}")
            return False, "Failed to create user account"
        
        finally:
            if connection:
                connection.close()
    
    def authenticate_user(self, login, password):
        """Authenticate user with username/email and password"""
        
        connection = self.get_db_connection()
        if not connection:
            return False, "Database connection failed"
        
        try: