# Film Price Guide - Environment Variables Template
# Copy this file to .env and fill in your actual values

# ================================
# FLASK APPLICATION SETTINGS
# ================================
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
PORT=5000
HOST=127.0.0.1

# ================================
# DATABASE CONFIGURATION
# ================================
# MySQL database connection URL
DATABASE_URL=mysql://username:password@localhost:3306/film_price_guide

# Alternative format (for some deployment platforms)
# DB_HOST=localhost
# DB_PORT=3306
# DB_NAME=film_price_guide
# DB_USER=username
# DB_PASSWORD=password

# ================================
# EBAY API CREDENTIALS
# ================================
# Get these from https://developer.ebay.com/my/keys
EBAY_APP_ID=YourApp-YourAppI-PRD-abc123def456
EBAY_CERT_ID=PRD-abc123def456ghi789jkl012mno345pqr678stu901vwx234
EBAY_DEV_ID=12345abc-6789-def0-1234-56789abcdef0
EBAY_USER_TOKEN=your_user_token_here
EBAY_VERIFICATION_TOKEN=your_verification_token_for_notifications

# eBay Sandbox credentials (for testing)
EBAY_APP_ID_SANDBOX=YourApp-YourAppI-SBX-abc123def456
EBAY_CERT_ID_SANDBOX=SBX-abc123def456ghi789jkl012mno345pqr678
EBAY_DEV_ID_SANDBOX=12345abc-6789-def0-1234-56789abcdef0

# ================================
# MOVIE DATABASE API KEYS
# ================================
# OMDb API (http://www.omdbapi.com/apikey.aspx)
OMDB_API_KEY=your_omdb_api_key_here

# TMDb API (https://www.themoviedb.org/settings/api)
TMDB_API_KEY=your_tmdb_api_key_here

# ================================
# OPTIONAL API INTEGRATIONS
# ================================
# Heritage Auctions (if needed)
HERITAGE_API_KEY=your_heritage_api_key

# Email configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com

# ================================
# REDIS CONFIGURATION (optional)
# ================================
# For caching and rate limiting
REDIS_URL=redis://localhost:6379/0

# ================================
# SECURITY SETTINGS
# ================================
# JWT tokens (if using JWT authentication)
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Rate limiting
RATELIMIT_ENABLED=true
RATELIMIT_DEFAULT=1000 per hour

# ================================
# LOGGING CONFIGURATION
# ================================
LOG_LEVEL=INFO
LOG_FILE=logs/film_price_guide.log

# ================================
# BUSINESS LOGIC SETTINGS
# ================================
# Price update frequency (in hours)
PRICE_UPDATE_INTERVAL_HOURS=24

# Maximum items in user watchlist
MAX_WATCHLIST_ITEMS=100

# Price alert check interval (in minutes)
PRICE_ALERT_INTERVAL=60

# ================================
# DEPLOYMENT SETTINGS
# ================================
# Production domain (for CORS)
PRODUCTION_DOMAIN=yourdomain.com

# File upload settings
MAX_FILE_SIZE_MB=16
UPLOAD_FOLDER=uploads

# Feature flags
ENABLE_USER_REGISTRATION=true
ENABLE_EMAIL_VERIFICATION=false
ENABLE_PRICE_ALERTS=true
ENABLE_API_DOCS=false

# ================================
# EXTERNAL SERVICE URLS
# ================================
# Custom API endpoints (if any)
CUSTOM_API_ENDPOINT=https://api.yourservice.com
WEBHOOK_URL=https://yourdomain.com/webhooks

# ================================
# DEVELOPMENT SETTINGS
# ================================
# Only use in development
MOCK_EXTERNAL_APIS=false
BYPASS_AUTH=false
ENABLE_DEBUG_TOOLBAR=false