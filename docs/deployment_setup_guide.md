# Film Price Guide - GitHub Deployment Setup

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Easiest)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial Film Price Guide commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/film-price-guide.git
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub account
   - Deploy from repo
   - Railway auto-detects Flask app
   - Add environment variables in Railway dashboard

3. **Environment Variables:**
   ```bash
   # Required in Railway dashboard:
   EBAY_APP_ID=your_actual_app_id
   EBAY_CERT_ID=your_actual_cert_id
   EBAY_DEV_ID=your_actual_dev_id
   DATABASE_URL=mysql://user:pass@host:port/db_name
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   ```

### Option 2: Render (Great Free Tier)

1. **Create `render.yaml`:**
   ```yaml
   services:
     - type: web
       name: film-price-guide
       env: python
       buildCommand: "cd backend && pip install -r requirements.txt"
       startCommand: "cd backend && gunicorn app:app"
       envVars:
         - key: FLASK_ENV
           value: production
         - key: DATABASE_URL
           fromDatabase:
             name: film-price-db
             property: connectionString
   
   databases:
     - name: film-price-db
       databaseName: film_price_guide
       user: film_user
   ```

2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Connect GitHub repository
   - Render auto-deploys on push

### Option 3: Heroku (Classic)

1. **Add Heroku files:**
   ```bash
   # Procfile
   web: cd backend && gunicorn app:app
   worker: cd backend && python services/scheduler.py
   
   # runtime.txt
   python-3.11.8
   ```

2. **Deploy:**
   ```bash
   heroku create film-price-guide
   heroku addons:create cleardb:ignite  # MySQL addon
   heroku config:set EBAY_APP_ID=your_app_id
   git push heroku main
   ```

## 📁 Required Project Structure

```
film-price-guide/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions
├── backend/
│   ├── app.py                  # Main Flask app
│   ├── requirements.txt        # Python dependencies
│   ├── wsgi.py                 # Production WSGI
│   ├── endpoints/
│   ├── services/
│   ├── models/
│   └── utils/
├── frontend/                   # Static files
├── database/
│   └── schema.sql             # MySQL schema
├── .env.example               # Environment template
├── .gitignore
├── README.md
├── Procfile                   # For Heroku
├── render.yaml               # For Render
└── railway.json              # For Railway
```

## 🔧 Production Configuration

### 1. Environment Variables (Critical)
```bash
# eBay API (Required)
EBAY_APP_ID=YourApp-YourAppI-PRD-abc123def456
EBAY_CERT_ID=PRD-abc123def456ghi789...
EBAY_DEV_ID=12345abc-6789-def0-1234-56789abcdef0
EBAY_ENVIRONMENT=production  # or sandbox for testing

# Database
DATABASE_URL=mysql://user:password@host:port/film_price_guide

# Security
SECRET_KEY=your-super-secret-key-32-chars-min
FLASK_ENV=production

# Optional API integrations
OMDB_API_KEY=your_omdb_key
TMDB_API_KEY=your_tmdb_key
```

### 2. Production wsgi.py
```python
# backend/wsgi.py
import os
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

### 3. Updated requirements.txt
```txt
Flask==2.3.3
gunicorn==21.2.0
mysql-connector-python==8.2.0
requests==2.31.0
python-dotenv==1.0.0
flask-cors==4.0.0
schedule==1.2.0
celery==5.3.4
redis==5.0.1
```

## 🔒 Security Checklist

- [ ] eBay API credentials in environment variables (never in code)
- [ ] Strong SECRET_KEY for Flask sessions
- [ ] Database credentials secured
- [ ] `.env` file in `.gitignore`
- [ ] Input validation for all API endpoints
- [ ] Rate limiting enabled for public endpoints
- [ ] HTTPS enforced in production

## 📊 Monitoring & Maintenance

### GitHub Actions Integration
- Automated testing on pull requests
- Security scanning with Trufflehog
- Automatic deployments on main branch push
- Database migration checks

### Production Monitoring
```python
# Add to your Flask app for health checks
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }
```

## 🎯 Recommended Workflow

1. **Development:**
   ```bash
   git checkout -b feature/price-alerts
   # Make changes
   git commit -m "Add price alert functionality"
   git push origin feature/price-alerts
   # Create pull request
   ```

2. **Testing:**
   - GitHub Actions runs tests automatically
   - Manual testing on staging environment
   - Review code in pull request

3. **Deployment:**
   ```bash
   git checkout main
   git merge feature/price-alerts
   git push origin main
   # Auto-deploys to production via GitHub Actions
   ```

## 💡 Pro Tips

1. **Use GitHub Secrets** for sensitive data
2. **Branch protection** on main branch
3. **Staging environment** for testing
4. **Database backups** scheduled daily
5. **Monitor eBay API rate limits**
6. **Cache frequently accessed data**

## 🆘 Troubleshooting

**Common deployment issues:**
- eBay API credentials not working → Check environment variables
- Database connection fails → Verify DATABASE_URL format
- Static files not loading → Check Flask static file configuration
- Background jobs not running → Ensure worker process is configured

**Useful debug commands:**
```bash
# Check deployment logs
railway logs
# or
heroku logs --tail
# or
render logs

# Test database connection
python -c "from backend.models import db; print(db.engine.execute('SELECT 1').scalar())"
```