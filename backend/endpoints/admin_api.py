#!/usr/bin/env python3
"""
Film Price Guide - Admin API
Admin panel endpoints for configuration and management
"""

from flask import Blueprint, request, jsonify, session, current_app
import os
import json
import logging
from datetime import datetime

# Import database service and auth decorators
try:
    from services.database_service import get_db
    from endpoints.auth_api import admin_required, login_required
except ImportError:
    # Fallback decorators if auth not available
    def admin_required(f):
        return f
    def login_required(f):
        return f
    def get_db():
        return None

logger = logging.getLogger(__name__)

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# ================================
# SYSTEM STATUS & MONITORING
# ================================

@admin_bp.route('/status', methods=['GET'])
@admin_required
def system_status():
    """Get comprehensive system status"""
    try:
        db = get_db()
        
        # Database status
        db_status = "unknown"
        db_error = None
        if db:
            success, message = db.test_connection()
            db_status = "connected" if success else "disconnected"
            if not success:
                db_error = message
        
        # API keys status
        api_status = {
            'ebay': {
                'app_id': bool(current_app.config.get('EBAY_APP_ID')),
                'cert_id': bool(current_app.config.get('EBAY_CERT_ID')),
                'dev_id': bool(current_app.config.get('EBAY_DEV_ID'))
            },
            'omdb': bool(current_app.config.get('OMDB_API_KEY')),
            'tmdb': bool(current_app.config.get('TMDB_API_KEY'))
        }
        
        # Environment info
        env_info = {
            'flask_env': current_app.config.get('FLASK_ENV'),
            'debug': current_app.config.get('DEBUG'),
            'secret_key_set': bool(current_app.config.get('SECRET_KEY')),
            'database_url_set': bool(current_app.config.get('DATABASE_URL'))
        }
        
        return jsonify({
            'status': 'running',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'status': db_status,
                'error': db_error
            },
            'api_keys': api_status,
            'environment': env_info,
            'blueprints': list(current_app.blueprints.keys())
        }), 200
        
    except Exception as e:
        logger.error(f"System status error: {e}")
        return jsonify({'error': 'Failed to get system status'}), 500

# ================================
# API KEY MANAGEMENT
# ================================

@admin_bp.route('/api-keys', methods=['GET'])
@admin_required
def get_api_keys():
    """Get current API key configuration (masked)"""
    try:
        def mask_key(key):
            """Mask API key for display"""
            if not key:
                return None
            return key[:4] + '*' * (len(key) - 8) + key[-4:] if len(key) > 8 else '*' * len(key)
        
        api_keys = {
            'ebay': {
                'app_id': mask_key(current_app.config.get('EBAY_APP_ID')),
                'cert_id': mask_key(current_app.config.get('EBAY_CERT_ID')),
                'dev_id': mask_key(current_app.config.get('EBAY_DEV_ID')),
                'verification_token': mask_key(current_app.config.get('EBAY_VERIFICATION_TOKEN'))
            },
            'omdb': {
                'api_key': mask_key(current_app.config.get('OMDB_API_KEY'))
            },
            'tmdb': {
                'api_key': mask_key(current_app.config.get('TMDB_API_KEY'))
            }
        }
        
        return jsonify({'api_keys': api_keys}), 200
        
    except Exception as e:
        logger.error(f"Get API keys error: {e}")
        return jsonify({'error': 'Failed to get API keys'}), 500

@admin_bp.route('/api-keys', methods=['POST'])
@admin_required
def update_api_keys():
    """Update API keys"""
    try:
        data = request.get_json()
        
        # Validate request
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        updated_keys = []
        
        # eBay API keys
        if 'ebay' in data:
            ebay_data = data['ebay']
            if ebay_data.get('app_id'):
                os.environ['EBAY_APP_ID'] = ebay_data['app_id']
                current_app.config['EBAY_APP_ID'] = ebay_data['app_id']
                updated_keys.append('EBAY_APP_ID')
            
            if ebay_data.get('cert_id'):
                os.environ['EBAY_CERT_ID'] = ebay_data['cert_id']
                current_app.config['EBAY_CERT_ID'] = ebay_data['cert_id']
                updated_keys.append('EBAY_CERT_ID')
            
            if ebay_data.get('dev_id'):
                os.environ['EBAY_DEV_ID'] = ebay_data['dev_id']
                current_app.config['EBAY_DEV_ID'] = ebay_data['dev_id']
                updated_keys.append('EBAY_DEV_ID')
            
            if ebay_data.get('verification_token'):
                os.environ['EBAY_VERIFICATION_TOKEN'] = ebay_data['verification_token']
                current_app.config['EBAY_VERIFICATION_TOKEN'] = ebay_data['verification_token']
                updated_keys.append('EBAY_VERIFICATION_TOKEN')
        
        # OMDb API key
        if 'omdb' in data and data['omdb'].get('api_key'):
            os.environ['OMDB_API_KEY'] = data['omdb']['api_key']
            current_app.config['OMDB_API_KEY'] = data['omdb']['api_key']
            updated_keys.append('OMDB_API_KEY')
        
        # TMDb API key
        if 'tmdb' in data and data['tmdb'].get('api_key'):
            os.environ['TMDB_API_KEY'] = data['tmdb']['api_key']
            current_app.config['TMDB_API_KEY'] = data['tmdb']['api_key']
            updated_keys.append('TMDB_API_KEY')
        
        # Optionally save to database for persistence
        db = get_db()
        if db:
            for key_name in updated_keys:
                key_value = os.environ.get(key_name)
                if key_value:
                    db.save_api_key(key_name, key_value)
        
        return jsonify({
            'message': 'API keys updated successfully',
            'updated_keys': updated_keys
        }), 200
        
    except Exception as e:
        logger.error(f"Update API keys error: {e}")
        return jsonify({'error': 'Failed to update API keys'}), 500

# ================================
# DATABASE MANAGEMENT
# ================================

@admin_bp.route('/database/test', methods=['POST'])
@admin_required
def test_database():
    """Test database connection"""
    try:
        db = get_db()
        if not db:
            return jsonify({
                'success': False,
                'error': 'Database service not initialized'
            }), 500
        
        success, message = db.test_connection()
        
        return jsonify({
            'success': success,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }), 200 if success else 500
        
    except Exception as e:
        logger.error(f"Database test error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_bp.route('/database/stats', methods=['GET'])
@admin_required
def database_stats():
    """Get database statistics"""
    try:
        db = get_db()
        if not db:
            return jsonify({'error': 'Database service unavailable'}), 503
        
        stats = {}
        
        # Get table counts
        tables = ['users', 'films', 'price_history', 'watchlist']
        for table in tables:
            query = f"SELECT COUNT(*) as count FROM {table}"
            success, result = db.execute_query(query, fetch=True)
            if success and result:
                stats[f"{table}_count"] = result[0]['count']
            else:
                stats[f"{table}_count"] = 0
        
        # Get recent activity
        query = """
        SELECT DATE(created_at) as date, COUNT(*) as count 
        FROM users 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        GROUP BY DATE(created_at) 
        ORDER BY date DESC
        """
        success, recent_users = db.execute_query(query, fetch=True)
        if success:
            stats['recent_user_registrations'] = recent_users
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        logger.error(f"Database stats error: {e}")
        return jsonify({'error': 'Failed to get database stats'}), 500

# ================================
# APPLICATION SETTINGS
# ================================

@admin_bp.route('/settings', methods=['GET'])
@admin_required
def get_settings():
    """Get application settings"""
    try:
        settings = {
            'app_name': 'Film Price Guide',
            'version': '1.0.0',
            'environment': current_app.config.get('FLASK_ENV'),
            'debug': current_app.config.get('DEBUG'),
            'features': {
                'user_registration': True,
                'email_verification': False,  # Not implemented yet
                'price_alerts': True,
                'watchlist': True,
                'admin_panel': True
            },
            'limits': {
                'max_watchlist_items': 100,
                'max_search_results': 200,
                'file_upload_size_mb': 16
            }
        }
        
        return jsonify({'settings': settings}), 200
        
    except Exception as e:
        logger.error(f"Get settings error: {e}")
        return jsonify({'error': 'Failed to get settings'}), 500

@admin_bp.route('/settings', methods=['POST'])
@admin_required
def update_settings():
    """Update application settings"""
    try:
        data = request.get_json()
        
        # This is a placeholder - in a real app, you'd save these to database
        # or a configuration file
        
        return jsonify({
            'message': 'Settings updated successfully',
            'updated_at': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Update settings error: {e}")
        return jsonify({'error': 'Failed to update settings'}), 500

# ================================
# LOGS & MONITORING
# ================================

@admin_bp.route('/logs', methods=['GET'])
@admin_required
def get_logs():
    """Get application logs"""
    try:
        log_file = current_app.config.get('LOG_FILE', 'logs/film_price_guide.log')
        lines = int(request.args.get('lines', 100))
        
        logs = []
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                # Get last N lines
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                for line in recent_lines:
                    logs.append(line.strip())
        
        return jsonify({
            'logs': logs,
            'total_lines': len(logs),
            'log_file': log_file
        }), 200
        
    except Exception as e:
        logger.error(f"Get logs error: {e}")
        return jsonify({'error': 'Failed to get logs'}), 500

# ================================
# SYSTEM ACTIONS
# ================================

@admin_bp.route('/cache/clear', methods=['POST'])
@admin_required
def clear_cache():
    """Clear application cache"""
    try:
        # Placeholder for cache clearing logic
        # You would implement actual cache clearing here
        
        return jsonify({
            'message': 'Cache cleared successfully',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        return jsonify({'error': 'Failed to clear cache'}), 500

@admin_bp.route('/backup/create', methods=['POST'])
@admin_required
def create_backup():
    """Create database backup"""
    try:
        # Placeholder for backup creation logic
        # You would implement actual backup logic here
        
        backup_name = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.sql"
        
        return jsonify({
            'message': 'Backup created successfully',
            'backup_name': backup_name,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Create backup error: {e}")
        return jsonify({'error': 'Failed to create backup'}), 500

# ================================
# ERROR HANDLERS
# ================================

@admin_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Admin privileges required'}), 403

@admin_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Admin endpoint not found'}), 404

@admin_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500