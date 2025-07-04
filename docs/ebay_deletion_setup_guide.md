# eBay Marketplace Account Deletion - Setup Guide

## Overview

This guide helps you implement eBay's required Marketplace Account Deletion/Closure notifications for your Film Price Guide application. **All eBay developers are required to implement this or face account termination.**

## 🚨 Requirements

- **Mandatory for all eBay API users**
- **HTTPS endpoint required** (no localhost or internal IPs)
- **Must respond within 24 hours** or face compliance issues
- **Irreversible data deletion** required when notified

## 📁 File Placement

Place the deletion endpoint at: `backend/endpoints/ebay_deletion.py`

## 🔧 Environment Variables

Add these to your `.env` file:

```bash
# eBay Marketplace Account Deletion
EBAY_VERIFICATION_TOKEN=your_32_to_80_char_token_here
EBAY_DELETION_ENDPOINT_URL=https://yourdomain.com/api/ebay/deletion/notifications

# Must be 32-80 characters, alphanumeric + underscore + hyphen only
# Example: my_film_price_guide_verification_token_2025_secure
```

## 🔗 Integration Steps

### 1. Update Main Flask App

Add to your `backend/app.py`:

```python
from endpoints.ebay_deletion import deletion_bp

# Register the deletion blueprint
app.register_blueprint(deletion_bp)
```

### 2. Update Requirements

Add to `backend/requirements.txt`:

```txt
cryptography==41.0.7
```

Install: `pip install cryptography`

### 3. Database Models Updates

Ensure your User model has methods to handle eBay user data:

```python
# In backend/models/user.py
class User:
    @classmethod
    def find_by_ebay_data(cls, username=None, ebay_user_id=None):
        """Find user by eBay username or stored eBay user ID"""
        # Implementation to find user linked to eBay account
        pass
    
    @classmethod
    def permanent_delete(cls, user_id):
        """Permanently and irreversibly delete user account"""
        # Implementation for complete data deletion
        pass
```

## 🌐 eBay Developer Portal Setup

### Step 1: Login to eBay Developer Portal
1. Go to [developer.ebay.com](https://developer.ebay.com)
2. Sign in with your developer account
3. Navigate to **Application Keys** page

### Step 2: Configure Notifications
1. Click **Notifications** link next to your App ID
2. Select **Marketplace Account Deletion** radio button
3. Enter your alert email address and click **Save**

### Step 3: Set Endpoint URL
1. **Notification Endpoint URL**: `https://yourdomain.com/api/ebay/deletion/notifications`
2. **Verification Token**: Your 32-80 character token from `.env`
3. Click **Save** - eBay will immediately send a challenge code

### Step 4: Verify Setup
1. Your endpoint should automatically respond to the challenge
2. Click **Send Test Notification** to verify everything works
3. Check your logs for successful processing

## 🧪 Testing Your Implementation

### Test Challenge Response
```bash
# eBay will send this automatically, but you can simulate:
curl "https://yourdomain.com/api/ebay/deletion/notifications?challenge_code=test123"

# Should return:
{
  "challengeResponse": "your_calculated_hash_here"
}
```

### Test Deletion Notification
```bash
# Use the built-in test endpoint:
curl -X POST https://yourdomain.com/api/ebay/deletion/notifications/test

# Should return successful processing result
```

### Check Status
```bash
curl https://yourdomain.com/api/ebay/deletion/notifications/status

# Returns current configuration status
```

## 📊 What Gets Deleted

When a user requests account deletion, the endpoint will remove:

1. **User Account** - Complete profile deletion
2. **Watchlist Items** - All tracked movies
3. **Price Alerts** - All price notifications
4. **Search History** - User's search records
5. **Preferences** - Settings and configuration
6. **Cached Data** - Any temporary user data

## 🔒 Security & Compliance

### Signature Verification
The endpoint includes signature verification to ensure notifications actually come from eBay:

```python
# Uses eBay's public key to verify authenticity
signature_header = request.headers.get('x-ebay-signature')
if verify_notification_signature(signature_header, notification_data):
    # Process legitimate notification
```

### Audit Logging
All deletion events are logged for compliance:

```python
log_entry = {
    'event_type': 'EBAY_MARKETPLACE_ACCOUNT_DELETION',
    'notification_id': notification_id,
    'ebay_username': username,
    'processed_at': datetime.utcnow().isoformat(),
    'deletion_result': deletion_result
}
```

## 🚨 Production Considerations

### 1. Immediate Acknowledgment
- **MUST** return 200 OK immediately
- Process deletion asynchronously if needed
- eBay retries failed notifications every few hours

### 2. Irreversible Deletion
- Deletion must be permanent and complete
- Even system administrators cannot recover deleted data
- Consider secure data wiping for sensitive information

### 3. Response Time Requirements
- Respond within **24 hours** or face compliance issues
- After 30 days of non-compliance, API access is terminated
- Monitor endpoint health continuously

### 4. Error Handling
- Log all errors but still acknowledge receipt
- Email alerts for critical failures
- Retry mechanisms for database operations

## 📈 Monitoring & Alerts

### Essential Monitoring
1. **Endpoint uptime** - Must be 99.9%+ available
2. **Response times** - Should acknowledge within seconds
3. **Failed deletions** - Alert on any deletion errors
4. **eBay notifications** - Track notification volume

### Example Monitoring Code
```python
# Add to your monitoring system
@deletion_bp.after_request
def log_deletion_metrics(response):
    if request.endpoint == 'ebay_deletion.handle_deletion_notification':
        # Log metrics for monitoring
        metrics.increment('ebay_deletion.notifications_received')
        if response.status_code == 200:
            metrics.increment('ebay_deletion.notifications_acknowledged')
        else:
            metrics.increment('ebay_deletion.notifications_failed')
    return response
```

## 🔧 Troubleshooting

### Common Issues

**Challenge Response Fails:**
- Verify verification token is correct
- Check endpoint URL exactly matches configuration
- Ensure HTTPS is working properly

**Notifications Not Received:**
- Check eBay Developer Portal subscription status
- Verify endpoint is publicly accessible
- Review firewall and security settings

**Deletion Errors:**
- Check database connectivity
- Verify user lookup logic
- Review cascade deletion constraints

### Debug Endpoints

```bash
# Check configuration
GET /api/ebay/deletion/status

# Test with sample data
POST /api/ebay/deletion/test

# View recent logs (add authentication in production)
GET /api/ebay/deletion/logs
```

## 📋 Compliance Checklist

- [ ] Endpoint deployed to production HTTPS URL
- [ ] Environment variables configured
- [ ] Subscribed in eBay Developer Portal
- [ ] Challenge response working
- [ ] Test notification successful
- [ ] Data deletion logic implemented
- [ ] Audit logging enabled
- [ ] Monitoring and alerts configured
- [ ] Error handling tested
- [ ] Documentation updated

## 🆘 Support

If you encounter issues:

1. **eBay Developer Support**: [developer.ebay.com/support](https://developer.ebay.com/support)
2. **Documentation**: [developer.ebay.com/api-docs/developer/notification](https://developer.ebay.com/api-docs/developer/notification)
3. **Community Forum**: eBay Developer Community

**Remember**: Failure to implement this correctly will result in termination of your eBay API access, which would break your Film Price Guide's core functionality.