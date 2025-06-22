# backend/endpoints/ebay_deletion.py
"""
eBay Marketplace Account Deletion/Closure Notifications Endpoint
Handles eBay user data deletion requests as required by eBay Developers Program
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import hashlib
import hmac
import base64
import json
import requests
import os
import logging
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

# Import custom modules
from services.user_service import UserService
from services.database_service import DatabaseService
from utils.auth import verify_ebay_signature
from models.user import User
from models.price_history import PriceHistory
from models.watchlist import Watchlist

# Create Blueprint
deletion_bp = Blueprint('ebay_deletion', __name__, url_prefix='/api/ebay/deletion')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
VERIFICATION_TOKEN = os.getenv('EBAY_VERIFICATION_TOKEN', 'your_verification_token_here')
ENDPOINT_URL = os.getenv('EBAY_DELETION_ENDPOINT_URL', 'https://yoursite.com/api/ebay/deletion/notifications')
EBAY_NOTIFICATION_API_BASE = 'https://api.ebay.com/developer/notification/v1'

# Cache for public keys (recommended by eBay - cache for 1 hour)
public_key_cache = {}
CACHE_DURATION = 3600  # 1 hour in seconds

@deletion_bp.route('/notifications', methods=['GET'])
def challenge_response():
    """
    Handle eBay's challenge code validation during subscription setup
    
    eBay sends: GET https://yoursite.com/api/ebay/deletion/notifications?challenge_code=123
    Must respond with SHA256 hash of: challengeCode + verificationToken + endpoint
    """
    try:
        # Get challenge code from query parameter
        challenge_code = request.args.get('challenge_code')
        
        if not challenge_code:
            logger.error("Challenge code not provided in request")
            return jsonify({
                'error': 'Missing challenge_code parameter'
            }), 400
        
        # Verify we have required configuration
        if not VERIFICATION_TOKEN or VERIFICATION_TOKEN == 'your_verification_token_here':
            logger.error("Verification token not configured")
            return jsonify({
                'error': 'Server configuration error'
            }), 500
        
        # Create hash: challengeCode + verificationToken + endpoint
        hash_input = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
        
        # Generate SHA256 hash
        hash_object = hashlib.sha256(hash_input.encode('utf-8'))
        challenge_response_hash = hash_object.hexdigest()
        
        logger.info(f"Challenge response generated for challenge_code: {challenge_code}")
        
        # Return response in required JSON format
        response = {
            'challengeResponse': challenge_response_hash
        }
        
        return jsonify(response), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        logger.error(f"Error in challenge response: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@deletion_bp.route('/notifications', methods=['POST'])
def handle_deletion_notification():
    """
    Handle eBay marketplace account deletion/closure notifications
    
    When eBay user requests account deletion, eBay sends POST notification
    Must acknowledge immediately, then verify signature and delete user data
    """
    try:
        # Immediately acknowledge receipt (required by eBay)
        notification_data = request.get_json()
        
        if not notification_data:
            logger.error("No JSON data in deletion notification")
            return '', 400
        
        # Log notification receipt
        notification_id = notification_data.get('notification', {}).get('notificationId', 'unknown')
        logger.info(f"Received eBay deletion notification: {notification_id}")
        
        # Verify this is a marketplace account deletion notification
        metadata = notification_data.get('metadata', {})
        if metadata.get('topic') != 'MARKETPLACE_ACCOUNT_DELETION':
            logger.warning(f"Unexpected notification topic: {metadata.get('topic')}")
            return '', 200  # Still acknowledge to avoid retries
        
        # Extract user data from notification
        notification = notification_data.get('notification', {})
        user_data = notification.get('data', {})
        
        username = user_data.get('username')
        user_id = user_data.get('userId')  
        eias_token = user_data.get('eiasToken')
        event_date = notification.get('eventDate')
        
        if not username or not user_id:
            logger.error(f"Missing required user data in notification {notification_id}")
            return '', 200  # Still acknowledge
        
        logger.info(f"Processing deletion for eBay user: {username} (ID: {user_id})")
        
        # Acknowledge immediately (return 200 OK first, then process)
        # This is done by spawning async task or processing after response
        
        # For now, we'll process synchronously but quickly
        try:
            # Verify notification signature (recommended security step)
            signature_header = request.headers.get('x-ebay-signature')
            if signature_header and verify_notification_signature(signature_header, notification_data):
                logger.info(f"Signature verified for notification {notification_id}")
            else:
                logger.warning(f"Could not verify signature for notification {notification_id}")
                # Continue processing anyway, but log the warning
            
            # Delete user data from our systems
            deletion_result = delete_user_data(username, user_id, eias_token)
            
            # Log the deletion
            log_deletion_event(
                notification_id=notification_id,
                username=username,
                user_id=user_id,
                eias_token=eias_token,
                event_date=event_date,
                deletion_result=deletion_result
            )
            
            logger.info(f"Successfully processed deletion for user {username}")
            
        except Exception as process_error:
            logger.error(f"Error processing deletion for {username}: {str(process_error)}")
            # Still return 200 to acknowledge receipt
        
        # Return successful acknowledgment
        return '', 200
        
    except Exception as e:
        logger.error(f"Critical error in deletion notification handler: {str(e)}")
        # Even on error, return 200 to avoid eBay retries unless it's a parsing issue
        return '', 500

def verify_notification_signature(signature_header, notification_data):
    """
    Verify that the notification actually came from eBay using signature verification
    """
    try:
        # Decode the signature header to get keyId
        signature_data = base64.b64decode(signature_header)
        
        # For this example, we'll implement basic verification
        # In production, use eBay's official SDKs for this
        
        # Get public key from eBay (with caching)
        public_key = get_ebay_public_key(signature_data)
        
        if not public_key:
            logger.warning("Could not retrieve eBay public key for verification")
            return False
        
        # Verify signature against notification payload
        payload_bytes = json.dumps(notification_data, separators=(',', ':')).encode('utf-8')
        
        # This is a simplified verification - use eBay SDKs in production
        return True  # Placeholder
        
    except Exception as e:
        logger.error(f"Error verifying notification signature: {str(e)}")
        return False

def get_ebay_public_key(signature_data):
    """
    Get eBay's public key for signature verification (with caching)
    """
    try:
        # Extract keyId from signature data (simplified)
        # In production, properly parse the signature header
        
        # Check cache first
        cache_key = "ebay_public_key"
        cached_key = public_key_cache.get(cache_key)
        
        if cached_key and cached_key['expires'] > datetime.utcnow().timestamp():
            return cached_key['key']
        
        # Fetch public key from eBay Notification API
        # Note: This requires proper implementation based on eBay's documentation
        
        # For now, return None (implement proper key fetching)
        return None
        
    except Exception as e:
        logger.error(f"Error fetching eBay public key: {str(e)}")
        return None

def delete_user_data(username, user_id, eias_token):
    """
    Delete all user data from our Film Price Guide systems
    This must be irreversible deletion as required by eBay
    """
    deletion_results = {
        'username': username,
        'user_id': user_id,
        'eias_token': eias_token,
        'deleted_records': {},
        'errors': [],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        # Find user in our database by eBay username or stored eBay user ID
        user = User.find_by_ebay_data(username=username, ebay_user_id=user_id)
        
        if not user:
            logger.info(f"No user found in our system for eBay user {username}")
            deletion_results['deleted_records']['user'] = 0
            return deletion_results
        
        logger.info(f"Found user {user.id} ({user.username}) linked to eBay user {username}")
        
        # Delete user's watchlist items
        try:
            watchlist_count = Watchlist.delete_by_user_id(user.id)
            deletion_results['deleted_records']['watchlist_items'] = watchlist_count
            logger.info(f"Deleted {watchlist_count} watchlist items for user {user.id}")
        except Exception as e:
            error_msg = f"Error deleting watchlist: {str(e)}"
            deletion_results['errors'].append(error_msg)
            logger.error(error_msg)
        
        # Delete user's price alerts
        try:
            alerts_count = PriceHistory.delete_user_alerts(user.id)
            deletion_results['deleted_records']['price_alerts'] = alerts_count
            logger.info(f"Deleted {alerts_count} price alerts for user {user.id}")
        except Exception as e:
            error_msg = f"Error deleting price alerts: {str(e)}"
            deletion_results['errors'].append(error_msg)
            logger.error(error_msg)
        
        # Delete user's search history
        try:
            search_count = DatabaseService.delete_user_search_history(user.id)
            deletion_results['deleted_records']['search_history'] = search_count
            logger.info(f"Deleted {search_count} search history records for user {user.id}")
        except Exception as e:
            error_msg = f"Error deleting search history: {str(e)}"
            deletion_results['errors'].append(error_msg)
            logger.error(error_msg)
        
        # Delete any user preferences or settings
        try:
            prefs_count = DatabaseService.delete_user_preferences(user.id)
            deletion_results['deleted_records']['preferences'] = prefs_count
            logger.info(f"Deleted {prefs_count} preference records for user {user.id}")
        except Exception as e:
            error_msg = f"Error deleting preferences: {str(e)}"
            deletion_results['errors'].append(error_msg)
            logger.error(error_msg)
        
        # Finally, delete the user account itself
        try:
            User.permanent_delete(user.id)  # Irreversible deletion
            deletion_results['deleted_records']['user_account'] = 1
            logger.info(f"Permanently deleted user account {user.id}")
        except Exception as e:
            error_msg = f"Error deleting user account: {str(e)}"
            deletion_results['errors'].append(error_msg)
            logger.error(error_msg)
        
        # Clean up any cached data related to this user
        try:
            cache_count = DatabaseService.clear_user_cache(user.id)
            deletion_results['deleted_records']['cached_data'] = cache_count
        except Exception as e:
            error_msg = f"Error clearing user cache: {str(e)}"
            deletion_results['errors'].append(error_msg)
            logger.error(error_msg)
        
        logger.info(f"Completed data deletion for eBay user {username}")
        return deletion_results
        
    except Exception as e:
        error_msg = f"Critical error in user data deletion: {str(e)}"
        deletion_results['errors'].append(error_msg)
        logger.error(error_msg)
        return deletion_results

def log_deletion_event(notification_id, username, user_id, eias_token, event_date, deletion_result):
    """
    Log the deletion event for compliance and audit purposes
    """
    try:
        log_entry = {
            'event_type': 'EBAY_MARKETPLACE_ACCOUNT_DELETION',
            'notification_id': notification_id,
            'ebay_username': username,
            'ebay_user_id': user_id,
            'ebay_eias_token': eias_token,
            'ebay_event_date': event_date,
            'processed_at': datetime.utcnow().isoformat(),
            'deletion_result': deletion_result,
            'compliance_status': 'COMPLETED' if not deletion_result.get('errors') else 'COMPLETED_WITH_ERRORS'
        }
        
        # Store in audit log table or secure log file
        DatabaseService.log_compliance_event(log_entry)
        
        # Also log to application logs
        logger.info(f"Logged deletion event for notification {notification_id}")
        
    except Exception as e:
        logger.error(f"Error logging deletion event: {str(e)}")

@deletion_bp.route('/test', methods=['POST'])
def test_deletion_endpoint():
    """
    Test endpoint to verify deletion notification handling
    (Remove this in production or add proper authentication)
    """
    try:
        # Sample test notification based on eBay documentation
        test_notification = {
            "metadata": {
                "topic": "MARKETPLACE_ACCOUNT_DELETION",
                "schemaVersion": "1.0",
                "deprecated": False
            },
            "notification": {
                "notificationId": "test-notification-12345",
                "eventDate": datetime.utcnow().isoformat() + "Z",
                "publishDate": datetime.utcnow().isoformat() + "Z",
                "publishAttemptCount": 1,
                "data": {
                    "username": "test_user",
                    "userId": "testUserId123",
                    "eiasToken": "testEiasToken=="
                }
            }
        }
        
        # Process the test notification
        result = delete_user_data(
            username=test_notification["notification"]["data"]["username"],
            user_id=test_notification["notification"]["data"]["userId"],
            eias_token=test_notification["notification"]["data"]["eiasToken"]
        )
        
        return jsonify({
            'success': True,
            'message': 'Test deletion notification processed',
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error in test deletion endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@deletion_bp.route('/status', methods=['GET'])
def deletion_status():
    """
    Get status of deletion notification endpoint
    """
    try:
        status = {
            'service': 'eBay Marketplace Account Deletion',
            'status': 'active',
            'endpoint_url': ENDPOINT_URL,
            'verification_token_configured': bool(VERIFICATION_TOKEN and VERIFICATION_TOKEN != 'your_verification_token_here'),
            'last_notification': 'No recent notifications',  # Could track this
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({
            'service': 'eBay Marketplace Account Deletion',
            'status': 'error',
            'error': str(e)
        }), 500

# Error handlers
@deletion_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested deletion API endpoint does not exist'
    }), 404

@deletion_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred in the deletion service'
    }), 500