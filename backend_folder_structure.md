# Film Price Guide - Backend Folder Structure

## Recommended Project Root Structure

```
film-price-guide/
├── frontend/                    # React/HTML frontend files
│   ├── public/
│   ├── src/
│   └── package.json
├── backend/                     # Python Flask backend
│   ├── app.py                  # Main Flask application
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.py           # Configuration settings
│   ├── endpoints/              # API endpoint blueprints
│   │   ├── __init__.py
│   │   ├── ebay_api.py         # eBay endpoint (the artifact above)
│   │   ├── omdb_api.py         # OMDb API endpoints
│   │   ├── tmdb_api.py         # TMDb API endpoints
│   │   └── admin_api.py        # Admin panel endpoints
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── ebay_service.py     # eBay API service class
│   │   ├── omdb_service.py     # OMDb API service class
│   │   ├── tmdb_service.py     # TMDb API service class
│   │   └── database_service.py # Database operations
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── film.py             # Film model
│   │   ├── price_history.py    # Price history model
│   │   ├── user.py             # User model
│   │   ├── watchlist.py        # Watchlist model
│   │   └── film_category.py    # Category model
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication helpers
│   │   ├── rate_limiter.py     # Rate limiting utilities
│   │   ├── validators.py       # Input validation
│   │   └── helpers.py          # General helpers
│   ├── migrations/             # Database migrations
│   │   └── versions/
│   ├── tests/                  # Unit and integration tests
│   │   ├── __init__.py
│   │   ├── test_ebay_api.py
│   │   ├── test_models.py
│   │   └── test_services.py
│   ├── static/                 # Static files (if serving from Flask)
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │       └── hml.png         # Hostinger logo
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables
│   ├── .env.example            # Environment template
│   ├── wsgi.py                 # WSGI entry point
│   └── Dockerfile              # Docker configuration
├── database/                   # Database files and scripts
│   ├── schema.sql              # MySQL schema (from artifact)
│   ├── seed_data.sql           # Sample data
│   └── backups/
├── docs/                       # Documentation
│   ├── api_documentation.md
│   ├── deployment_guide.md
│   └── user_guide.md
├── scripts/                    # Utility scripts
│   ├── deploy.sh
│   ├── backup_db.sh
│   └── update_prices.py
├── docker-compose.yml          # Docker Compose for development
├── .gitignore
├── README.md
└── LICENSE
```

## Key Files You Need to Create

### 1. Main Flask App (`backend/app.py`)
```python
from flask import Flask
from flask_cors import CORS
from endpoints.ebay_api import ebay_bp
from endpoints.omdb_api import omdb_bp
from endpoints.tmdb_api import tmdb_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(ebay_bp)
app.register_blueprint(omdb_bp)
app.register_blueprint(tmdb_bp)

if __name__ == '__main__':
    app.run(debug=True)
```

### 2. Configuration (`backend/config/config.py`)
```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # eBay API
    EBAY_APP_ID = os.getenv('EBAY_APP_ID')
    EBAY_CERT_ID = os.getenv('EBAY_CERT_ID')
    EBAY_DEV_ID = os.getenv('EBAY_DEV_ID')
    EBAY_ENVIRONMENT = os.getenv('EBAY_ENVIRONMENT', 'sandbox')
    
    # OMDb API
    OMDB_API_KEY = os.getenv('OMDB_API_KEY')
    
    # TMDb API
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
```

### 3. Requirements (`backend/requirements.txt`)
```txt
Flask==2.3.3
Flask-CORS==4.0.0
requests==2.31.0
python-dotenv==1.0.0
SQLAlchemy==2.0.23
Flask-SQLAlchemy==3.1.1
PyMySQL==1.1.0
Flask-Migrate==4.0.5
redis==5.0.1
celery==5.3.4
gunicorn==21.2.0
pytest==7.4.3
```

### 4. Environment Template (`backend/.env.example`)
```bash
# eBay API Configuration
EBAY_APP_ID=your_app_id_here
EBAY_CERT_ID=your_cert_id_here
EBAY_DEV_ID=your_dev_id_here
EBAY_ENVIRONMENT=sandbox

# OMDb API Configuration
OMDB_API_KEY=your_omdb_api_key_here

# TMDb API Configuration
TMDB_API_KEY=your_tmdb_api_key_here

# Database Configuration
DATABASE_URL=mysql://username:password@localhost:3306/film_price_guide

# Application Settings
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

## File Placement Instructions

1. **Place the eBay endpoint file** at: `backend/endpoints/ebay_api.py`

2. **Create the main Flask app** at: `backend/app.py`

3. **Set up your database schema** using: `database/schema.sql` (from the MySQL artifact)

4. **Configure environment variables** in: `backend/.env`

5. **Install dependencies** from: `backend/requirements.txt`

## API URL Structure

With this structure, your eBay API endpoints will be available at:

- `GET /api/ebay/search` - Search sold movie items
- `GET /api/ebay/categories` - Get movie categories
- `GET /api/ebay/price-history/<film_id>` - Get price history
- `GET /api/ebay/trending` - Get trending movies
- `GET /api/ebay/health` - Health check

## Development Workflow

1. **Clone/create** your project directory
2. **Set up the backend** folder structure as shown above
3. **Place the eBay endpoint file** in `backend/endpoints/ebay_api.py`
4. **Create supporting files** (app.py, config.py, models, services)
5. **Install dependencies**: `pip install -r requirements.txt`
6. **Set up database** using the MySQL schema
7. **Configure environment variables** in `.env`
8. **Run the Flask app**: `python app.py`

## Production Deployment

- Use `wsgi.py` for production WSGI servers (Gunicorn, uWSGI)
- Set up Docker containers using the Dockerfile
- Use docker-compose.yml for multi-service deployment
- Place static files in appropriate directories for your web server

This structure provides a solid foundation for your Film Price Guide backend with clear separation of concerns and scalability for future features!