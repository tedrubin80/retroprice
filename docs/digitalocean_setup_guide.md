# 🌊 DigitalOcean App Platform Setup Guide

## 📁 Required Project Structure for DigitalOcean

```
film-price-guide/                    ← Your GitHub repository
├── .github/
│   └── workflows/
│       └── deploy.yml              ← GitHub Actions workflow
├── .do/
│   └── app.yaml                    ← DigitalOcean App spec
├── .gitignore
├── README.md
│
├── frontend/                       ← Static files (optional)
│   ├── index.html
│   ├── search-results.html
│   ├── item-detail.html
│   ├── dashboard.html
│   ├── admin-config.html
│   └── ebay-price-search.html
│
├── backend/                        ← Flask application
│   ├── app.py                     ← Main Flask app
│   ├── wsgi.py                    ← Production entry point
│   ├── gunicorn.conf.py           ← Gunicorn configuration
│   ├── requirements.txt           ← Python dependencies
│   ├── .env.example              ← Environment template
│   ├── endpoints/
│   │   ├── ebay_api.py           ← Your eBay endpoint
│   │   ├── ebay_deletion.py      ← Compliance endpoint
│   │   └── admin_api.py          ← Admin API
│   ├── services/
│   ├── models/
│   ├── utils/
│   └── tests/
│
├── database/
│   ├── schema.sql                 ← MySQL schema
│   └── migrations/
│
└── docs/
```

## 🔧 Required Configuration Files

### 1. **Gunicorn Configuration** (`backend/gunicorn.conf.py`)
```python
# Gunicorn configuration for DigitalOcean App Platform
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', 8080)}"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50

# Restart workers after this many requests, with up to 50 additional
# requests to avoid all workers restarting at the same time
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "film-price-guide"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = "/tmp"

# SSL (handled by DigitalOcean)
keyfile = None
certfile = None
```

### 2. **Production WSGI** (`backend/wsgi.py`)
```python
#!/usr/bin/env python3
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
```

### 3. **Requirements** (`backend/requirements.txt`)
```txt
# Core Flask application
Flask==2.3.3
gunicorn==21.2.0
flask-cors==4.0.0

# Database
mysql-connector-python==8.2.0
SQLAlchemy==2.0.23

# eBay API integration
requests==2.31.0
python-dotenv==1.0.0

# Background jobs
schedule==1.2.0
celery==5.3.4

# eBay compliance
cryptography==41.0.7

# Utilities
python-dateutil==2.8.2
pytz==2023.3

# Development/Testing (optional)
pytest==7.4.3
pytest-cov==4.1.0
flake8==6.1.0
```

### 4. **Main Flask App** (`backend/app.py`)
```python
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

# Import your blueprints
from endpoints.ebay_api import ebay_bp
from endpoints.ebay_deletion import deletion_bp
# from endpoints.admin_api import admin_bp  # Create this

def create_app():
    app = Flask(__name__, static_folder='../frontend')
    
    # Configure CORS for production
    CORS(app, origins=[
        "https://film-price-guide.ondigitalocean.app",
        "https://your-custom-domain.com"  # Add your custom domain
    ])
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
    app.config['EBAY_APP_ID'] = os.getenv('EBAY_APP_ID')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
    
    # Register blueprints
    app.register_blueprint(ebay_bp)
    app.register_blueprint(deletion_bp)
    # app.register_blueprint(admin_bp)
    
    # Serve frontend files
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path.startswith('api/'):
            # Let API routes handle themselves
            return "API endpoint not found", 404
        
        # Serve static files or return index.html for SPA routing
        try:
            return send_from_directory(app.static_folder, path)
        except:
            return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/health')
    def health():
        return {
            'status': 'healthy',
            'service': 'Film Price Guide',
            'version': '1.0.0'
        }
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
```

## 🔐 GitHub Secrets Setup

Add these secrets in your GitHub repository:
**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

### Required Secrets:
```
Name: DIGITALOCEAN_ACCESS_TOKEN
Value: [Get from DigitalOcean → API → Personal Access Tokens]

Name: EBAY_APP_ID
Value: YourApp-YourAppI-PRD-abc123def456

Name: EBAY_CERT_ID
Value: PRD-abc123def456ghi789jkl012mno345pqr678

Name: EBAY_DEV_ID
Value: 12345abc-6789-def0-1234-56789abcdef0

Name: EBAY_VERIFICATION_TOKEN
Value: your_32_to_80_char_verification_token

Name: SECRET_KEY
Value: your-super-secret-flask-key-32-chars-minimum
```

### Optional Test Secrets:
```
Name: EBAY_APP_ID_TEST
Value: [Sandbox credentials]

Name: EBAY_CERT_ID_TEST
Value: [Sandbox credentials]

Name: EBAY_DEV_ID_TEST
Value: [Sandbox credentials]
```

## 🚀 Deployment Steps

### Step 1: Set up DigitalOcean Account
1. **Create account** at [digitalocean.com](https://digitalocean.com)
2. **Go to Apps** in the control panel
3. **Generate API token**: API → Personal Access Tokens → Generate New Token

### Step 2: Prepare Your Repository
```bash
# Create required directories
mkdir -p .github/workflows
mkdir -p .do
mkdir -p backend
mkdir -p frontend

# Create configuration files (use the code above)
# Save them in the correct locations
```

### Step 3: Push to GitHub
```bash
git init
git add .
git commit -m "🎬 Initial Film Price Guide setup for DigitalOcean"
git remote add origin https://github.com/yourusername/film-price-guide.git
git push -u origin main
```

### Step 4: GitHub Actions Deploy Automatically
- ✅ Tests run on push to main
- ✅ Security scans execute
- ✅ Deploys to DigitalOcean App Platform
- ✅ Health checks verify deployment

### Step 5: Configure Environment Variables in DigitalOcean
1. **Go to your App** in DigitalOcean control panel
2. **Settings** → **App-Level Environment Variables**
3. **Add encrypted variables**:
   - `EBAY_APP_ID` = your eBay App ID
   - `EBAY_CERT_ID` = your eBay Cert ID
   - `EBAY_DEV_ID` = your eBay Dev ID
   - `SECRET_KEY` = your Flask secret key

## 💰 DigitalOcean Pricing

### App Platform Pricing:
- **Basic App**: $5/month (512 MB RAM, 1 vCPU)
- **Professional App**: $12/month (1 GB RAM, 1 vCPU)
- **Managed Database**: $15/month (MySQL 8.0, 1 GB RAM)

### **Total Cost**: ~$20/month for full production setup

### Free Tier Options:
- **3 static sites** (for frontend only)
- **$200 credit** for new accounts (2 months free)

## 🔧 Advanced Configuration

### Custom Domain Setup:
1. **Buy domain** (Namecheap, Google Domains, etc.)
2. **Add to App Platform**: Settings → Domains
3. **Update DNS**: Point CNAME to your app URL
4. **SSL**: Automatically handled by DigitalOcean

### Database Backups:
- **Automatic daily backups** included
- **Manual backups** available
- **Point-in-time recovery** for Professional tier

### Monitoring:
- **Built-in metrics** in App Platform dashboard
- **Alerts** for downtime, high CPU, memory usage
- **Logs** accessible via dashboard or CLI

## 🐛 Troubleshooting

### Common Issues:

**Build fails?**
- Check `requirements.txt` formatting
- Verify Python version compatibility
- Review build logs in DigitalOcean dashboard

**Database connection fails?**
- Ensure `DATABASE_URL` is set correctly
- Check database is in same region as app
- Verify MySQL version compatibility

**eBay API errors?**
- Confirm environment variables are set
- Check eBay Developer Account status
- Verify API credentials format

### Debug Commands:
```bash
# Check app status
doctl apps list

# View logs
doctl apps logs <app-id> --follow

# Get app details
doctl apps get <app-id>

# Update app
doctl apps update <app-id> --spec .do/app.yaml
```

## 🎯 Next Steps

1. **Create the configuration files** above
2. **Set up GitHub secrets**
3. **Push to GitHub** (auto-deploys to DigitalOcean)
4. **Configure environment variables** in DigitalOcean
5. **Test your deployed app**
6. **Set up custom domain** (optional)

Your Film Price Guide will be live at: `https://film-price-guide.ondigitalocean.app` 🚀