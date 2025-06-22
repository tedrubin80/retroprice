# 🎬 Film Price Guide - Current File Structure

## 📂 Your Current Files (From Documents)

Based on the files you've created, here's how to organize them:

### ✅ **Frontend Files (HTML/CSS/JS)**
```
frontend/
├── index.html                     ← vhs_dvd_homepage.html
├── search-results.html            ← search_results_page.html  
├── item-detail.html               ← item_detail_page.html
├── dashboard.html                 ← dashboard_page.html
├── admin-config.html              ← backend_admin_config.html
├── ebay-price-search.html         ← ebay_price_search.html
├── css/
│   └── (extract CSS from HTML files)
├── js/
│   └── (extract JavaScript from HTML files)
└── assets/
    └── images/
```

### ✅ **Backend Files (Python/Flask)**
```
backend/
├── app.py                         ← Create main Flask app
├── wsgi.py                        ← Create for production
├── requirements.txt               ← Create from ebay_backend_setup.py
├── .env.example                   ← Create template
│
├── endpoints/
│   ├── __init__.py
│   ├── ebay_api.py               ← ebay_endpoint.py
│   ├── ebay_deletion.py          ← ebay_deletion_endpoint.py  
│   └── admin_api.py              ← Create for admin panel
│
├── services/
│   ├── __init__.py
│   ├── ebay_service.py           ← Extract from ebay_backend_setup.py
│   └── database_service.py       ← Extract from ebay_backend_setup.py
│
├── models/
│   ├── __init__.py
│   ├── film.py                   ← Extract from schema
│   ├── price_history.py          ← Extract from schema
│   ├── user.py                   ← Extract from schema
│   └── watchlist.py              ← Extract from schema
│
├── utils/
│   ├── __init__.py
│   ├── rate_limiter.py           ← Extract from ebay_endpoint.py
│   └── helpers.py
│
└── tests/
    ├── __init__.py
    ├── test_ebay_api.py
    └── test_services.py
```

### ✅ **Database Files**
```
database/
├── schema.sql                     ← mysql_schema.sql
└── migrations/
    └── 001_initial_schema.sql
```

### ✅ **Documentation**
```
docs/
├── backend_folder_structure.md    ← backend_folder_structure.md
├── ebay_deletion_setup_guide.md   ← ebay_deletion_setup_guide.md
├── film_price_guide_structure.txt ← film_price_guide_structure.txt
└── api_documentation.md           ← Create API docs
```

---

## 🔧 **Files You Need to Create**

### 1. **Main Flask App** (`backend/app.py`)
```python
from flask import Flask
from flask_cors import CORS
from endpoints.ebay_api import ebay_bp
from endpoints.ebay_deletion import deletion_bp
from endpoints.admin_api import admin_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(ebay_bp)
app.register_blueprint(deletion_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'Film Price Guide'}

if __name__ == '__main__':
    app.run(debug=True)
```

### 2. **Requirements** (`backend/requirements.txt`)
```txt
# Extract from ebay_backend_setup.py
flask==2.3.3
flask-cors==4.0.0
requests==2.31.0
python-dotenv==1.0.0
mysql-connector-python==8.2.0
schedule==1.2.0
gunicorn==21.2.0
cryptography==41.0.7
```

### 3. **Production WSGI** (`backend/wsgi.py`)
```python
import os
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
```

### 4. **Environment Template** (`backend/.env.example`)
```bash
# eBay API Configuration
EBAY_APP_ID=your_app_id_here
EBAY_CERT_ID=your_cert_id_here
EBAY_DEV_ID=your_dev_id_here
EBAY_VERIFICATION_TOKEN=your_verification_token_here

# Database
DATABASE_URL=mysql://user:password@localhost:3306/film_price_guide

# Application
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

### 5. **GitHub Actions** (`.github/workflows/deploy.yml`)
```yaml
# Use the workflow from previous artifact
```

### 6. **Root Configuration Files**
```bash
# .gitignore
__pycache__/
*.pyc
.env
*.db
node_modules/
.DS_Store
backend/.env

# Procfile (for Heroku/Railway)
web: cd backend && gunicorn wsgi:app

# runtime.txt  
python-3.11.8
```

---

## 📋 **Action Plan: Organize Your Files**

### **Step 1: Create Directory Structure**
```bash
mkdir -p .github/workflows
mkdir -p frontend/{css,js,assets/images}
mkdir -p backend/{endpoints,services,models,utils,tests}
mkdir -p database/migrations
mkdir -p docs
```

### **Step 2: Move/Rename Your Files**
```bash
# Frontend files
mv vhs_dvd_homepage.html frontend/index.html
mv search_results_page.html frontend/search-results.html
mv item_detail_page.html frontend/item-detail.html
mv dashboard_page.html frontend/dashboard.html
mv backend_admin_config.html frontend/admin-config.html
mv ebay_price_search.html frontend/ebay-price-search.html

# Backend files  
mv ebay_endpoint.py backend/endpoints/ebay_api.py
mv ebay_deletion_endpoint.py backend/endpoints/ebay_deletion.py

# Database files
mv mysql_schema.sql database/schema.sql

# Documentation
mv backend_folder_structure.md docs/
mv ebay_deletion_setup_guide.md docs/
mv film_price_guide_structure.txt docs/
```

### **Step 3: Extract Code from Combined Files**

From `ebay_backend_setup.py`, extract into separate files:

- **Services** → `backend/services/ebay_service.py`
- **Database** → `backend/services/database_service.py`  
- **Models** → `backend/models/` (separate files)
- **Main App** → `backend/app.py`
- **Requirements** → `backend/requirements.txt`

### **Step 4: Extract CSS/JS from HTML**

Your HTML files have embedded CSS/JS. Consider extracting:
- **CSS** → `frontend/css/main.css`
- **JavaScript** → `frontend/js/main.js`
- **Keep HTML clean** with external references

---

## 🎯 **Recommended Final Structure**

```
film-price-guide/                    ← Your GitHub repository
├── .github/
│   └── workflows/
│       └── deploy.yml              ← GitHub Actions workflow
├── .gitignore
├── README.md
├── Procfile                        ← For deployment
├── runtime.txt                     ← Python version
│
├── frontend/                       ← All your HTML files (organized)
│   ├── index.html                 ← Homepage
│   ├── search-results.html        ← Search results
│   ├── item-detail.html           ← Item details
│   ├── dashboard.html             ← User dashboard
│   ├── admin-config.html          ← Admin panel
│   ├── ebay-price-search.html     ← Price search
│   ├── css/
│   │   └── main.css              ← Extracted styles
│   ├── js/
│   │   └── main.js               ← Extracted scripts
│   └── assets/
│       └── images/
│
├── backend/                        ← Python Flask application
│   ├── app.py                     ← Main Flask app
│   ├── wsgi.py                    ← Production entry
│   ├── requirements.txt           ← Dependencies
│   ├── .env.example              ← Environment template
│   ├── endpoints/                 ← API endpoints
│   │   ├── ebay_api.py           ← Your eBay endpoint
│   │   ├── ebay_deletion.py      ← Compliance endpoint
│   │   └── admin_api.py          ← Admin API
│   ├── services/                  ← Business logic
│   ├── models/                    ← Database models
│   ├── utils/                     ← Helper functions
│   └── tests/                     ← Test files
│
├── database/
│   ├── schema.sql                 ← Your MySQL schema
│   └── migrations/
│
└── docs/                          ← Documentation
    ├── setup.md
    ├── api.md
    └── deployment.md
```

This structure is **deployment-ready** and follows best practices for Flask applications that integrate with GitHub Actions and cloud platforms like Railway, Render, or Heroku.

Would you like me to help you create any of the missing files or guide you through reorganizing the existing ones?