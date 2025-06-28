#!/usr/bin/env python3
"""
Film Price Guide - Authentication API
User login, logout, registration endpoints
"""

from flask import Blueprint, request, jsonify, session
import bcrypt
import re
from datetime import datetime
from functools import wraps
import logging

# Import database service
try:
    from services.database_service import get_db
except ImportError:
    # Fallback for when service isn't available yet
    def get_db():
        return None

logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# ================================
# UTILITY FUNCTIONS
# ================================

def hash_password(password):
    """Hash password with bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password_strength(password):
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
    
    return errors

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        db = get_db()
        if db:
            user = db.get_user_by_id(session['user_id'])
            if not user or not user.get('is_admin'):
                return jsonify({'error': 'Admin privileges required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# ================================
# AUTHENTICATION ENDPOINTS
# ================================

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        # Validate inputs
        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters long'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        password_errors = validate_password_strength(password)
        if password_errors:
            return jsonify({'error': '; '.join(password_errors)}), 400
        
        # Check database connection
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        # Check if user already exists
        existing_user = db.get_user_by_email(email) or db.get_user_by_username(username)
        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Create user data
        user_data = {
            'username': username,
            'email': email,
            'password_hash': hashed_password,
            'first_name': first_name or None,
            'last_name': last_name or None,
            'created_at': datetime.utcnow()
        }
        
        # Create user
        success, result = db.create_user(user_data)
        
        if success:
            return jsonify({
                'message': 'User registered successfully',
                'username': username,
                'email': email
            }), 201
        else:
            return jsonify({'error': 'Failed to create user account'}), 500
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        login_field = data.get('login', '').strip()  # Can be username or email
        password = data.get('password', '')
        
        if not login_field or not password:
            return jsonify({'error': 'Login and password are required'}), 400
        
        # Check database connection
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        # Find user by email or username
        user = None
        if validate_email(login_field):
            user = db.get_user_by_email(login_field.lower())
        else:
            user = db.get_user_by_username(login_field)
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        db.update_user_login(user['id'])
        
        # Create session
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['email'] = user['email']
        session['is_admin'] = user.get('is_admin', False)
        session.permanent = True
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'is_admin': user.get('is_admin', False)
            }
        }), 200
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        session.clear()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user information"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        user = db.get_user_by_id(session['user_id'])
        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user.get('first_name'),
                'last_name': user.get('last_name'),
                'display_name': user.get('display_name'),
                'is_admin': user.get('is_admin', False),
                'created_at': user.get('created_at').isoformat() if user.get('created_at') else None,
                'last_login': user.get('last_login').isoformat() if user.get('last_login') else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({'error': 'Failed to get user information'}), 500

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session.get('username'),
                'email': session.get('email'),
                'is_admin': session.get('is_admin', False)
            }
        }), 200
    else:
        return jsonify({'authenticated': False}), 200

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        # Validate new password strength
        password_errors = validate_password_strength(new_password)
        if password_errors:
            return jsonify({'error': '; '.join(password_errors)}), 400
        
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        # Get current user
        user = db.get_user_by_id(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Verify current password
        if not verify_password(current_password, user['password_hash']):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Hash new password
        new_hashed_password = hash_password(new_password)
        
        # Update password in database
        query = "UPDATE users SET password_hash = %s, updated_at = NOW() WHERE id = %s"
        success, result = db.execute_query(query, (new_hashed_password, session['user_id']))
        
        if success:
            return jsonify({'message': 'Password changed successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update password'}), 500
            
    except Exception as e:
        logger.error(f"Change password error: {e}")
        return jsonify({'error': 'Failed to change password'}), 500

@auth_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        
        # Allowed fields to update
        allowed_fields = ['first_name', 'last_name', 'display_name', 'bio', 'location']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        # Build dynamic update query
        set_clauses = [f"{field} = %s" for field in update_data.keys()]
        set_clauses.append("updated_at = NOW()")
        
        query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = %s"
        params = list(update_data.values()) + [session['user_id']]
        
        success, result = db.execute_query(query, params)
        
        if success:
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update profile'}), 500
            
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        return jsonify({'error': 'Failed to update profile'}), 500

# ================================
# ADMIN ENDPOINTS
# ================================

@auth_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """List all users (admin only)"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        offset = (page - 1) * per_page
        
        query = """
        SELECT id, username, email, first_name, last_name, 
               is_active, is_verified, created_at, last_login
        FROM users 
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
        """
        
        success, users = db.execute_query(query, (per_page, offset), fetch=True)
        
        if success:
            # Convert datetime objects to strings
            for user in users:
                if user.get('created_at'):
                    user['created_at'] = user['created_at'].isoformat()
                if user.get('last_login'):
                    user['last_login'] = user['last_login'].isoformat()
            
            return jsonify({
                'users': users,
                'page': page,
                'per_page': per_page
            }), 200
        else:
            return jsonify({'error': 'Failed to fetch users'}), 500
            
    except Exception as e:
        logger.error(f"List users error: {e}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@auth_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status (admin only)"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        # Don't allow deactivating self
        if user_id == session['user_id']:
            return jsonify({'error': 'Cannot deactivate your own account'}), 400
        
        query = "UPDATE users SET is_active = NOT is_active WHERE id = %s"
        success, result = db.execute_query(query, (user_id,))
        
        if success:
            return jsonify({'message': 'User status updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update user status'}), 500
            
    except Exception as e:
        logger.error(f"Toggle user active error: {e}")
        return jsonify({'error': 'Failed to update user status'}), 500

# ================================
# ERROR HANDLERS
# ================================

@auth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@auth_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

@auth_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@auth_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
            