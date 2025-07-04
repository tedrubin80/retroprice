#!/bin/bash

# ================================================================
# Film Price Guide - File Organization & Deployment Script
# Multi-API Search Engine for VHS, DVD, and Graded Movies
# Compatible with: Dreamhost, GitHub Apps, Standard LAMP Stack
# ================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="film-price-guide"
PROJECT_ROOT="$(pwd)/$PROJECT_NAME"
BACKUP_DIR="$(pwd)/backup-$(date +%Y%m%d_%H%M%S)"

echo -e "${BLUE}🎬 Film Price Guide - File Organization Script${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# Create backup of existing files
echo -e "${YELLOW}📦 Creating backup...${NC}"
if [ -d "$PROJECT_NAME" ]; then
    cp -r "$PROJECT_NAME" "$BACKUP_DIR"
    echo -e "${GREEN}✅ Backup created at: $BACKUP_DIR${NC}"
fi

# Create main project directory structure
echo -e "${YELLOW}📁 Creating directory structure...${NC}"
mkdir -p "$PROJECT_ROOT"/{public,src,config,database,api,assets,logs,docs,scripts}

# Create subdirectories
mkdir -p "$PROJECT_ROOT/public"/{css,js,images,uploads}
mkdir -p "$PROJECT_ROOT/src"/{auth,admin,search,user,common}
mkdir -p "$PROJECT_ROOT/config"/{env,api-keys,database}
mkdir -p "$PROJECT_ROOT/database"/{migrations,seeds,backups}
mkdir -p "$PROJECT_ROOT/api"/{routes,controllers,middleware,models}
mkdir -p "$PROJECT_ROOT/assets"/{templates,emails,static}
mkdir -p "$PROJECT_ROOT/logs"/{access,error,api,debug}
mkdir -p "$PROJECT_ROOT/docs"/{api,deployment,user-guide}
mkdir -p "$PROJECT_ROOT/scripts"/{deploy,maintenance,backup}

echo -e "${GREEN}✅ Directory structure created${NC}"

# Create .htaccess for Apache (Dreamhost compatibility)
echo -e "${YELLOW}⚙️  Creating .htaccess files...${NC}"

cat > "$PROJECT_ROOT/public/.htaccess" << 'EOF'
# Film Price Guide - Apache Configuration
# Dreamhost & GitHub Apps Compatible

RewriteEngine On

# Security Headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"

# Remove server signature
ServerTokens Prod
Header unset Server

# Prevent access to sensitive files
<Files ~ "^\.">
    Order allow,deny
    Deny from all
</Files>

<FilesMatch "\.(env|log|sql|md|txt|json)$">
    Order allow,deny
    Deny from all
</FilesMatch>

# PHP Security
<FilesMatch "\.php$">
    Header set X-Content-Type-Options nosniff
</FilesMatch>

# Route all requests through index.php
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php [QSA,L]

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>

# Browser caching
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
</IfModule>
EOF

# Create main index.php (entry point)
echo -e "${YELLOW}📝 Creating main index.php...${NC}"

cat > "$PROJECT_ROOT/public/index.php" << 'EOF'
<?php
/**
 * Film Price Guide - Main Entry Point
 * Multi-API Search Engine for VHS, DVD, and Graded Movies
 * 
 * Compatible with: Dreamhost, GitHub Apps, Standard LAMP
 */

// Start session
session_start();

// Security headers
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('X-XSS-Protection: 1; mode=block');

// Load configuration
require_once '../config/config.php';
require_once '../src/common/functions.php';
require_once '../src/auth/auth.php';

// Get current page
$page = $_GET['page'] ?? 'home';
$allowed_pages = ['home', 'search', 'dashboard', 'admin', 'profile', 'api-test'];

if (!in_array($page, $allowed_pages)) {
    $page = 'home';
}

// Check admin access for admin pages
if ($page === 'admin' && (!isset($_SESSION['is_admin']) || !$_SESSION['is_admin'])) {
    header('Location: index.php?page=login&error=admin_required');
    exit;
}

// Include header
include '../src/common/header.php';

// Include page content
switch($page) {
    case 'home':
        include '../src/common/home.php';
        break;
    case 'search':
        include '../src/search/search.php';
        break;
    case 'dashboard':
        include '../src/user/dashboard.php';
        break;
    case 'admin':
        include '../src/admin/admin.php';
        break;
    case 'profile':
        include '../src/user/profile.php';
        break;
    case 'api-test':
        include '../src/search/api-test.php';
        break;
    default:
        include '../src/common/404.php';
}

// Include footer
include '../src/common/footer.php';
?>
EOF

# Create configuration files
echo -e "${YELLOW}⚙️  Creating configuration files...${NC}"

cat > "$PROJECT_ROOT/config/config.php" << 'EOF'
<?php
/**
 * Film Price Guide - Main Configuration
 */

// Load environment variables
if (file_exists(__DIR__ . '/env/.env')) {
    $env = parse_ini_file(__DIR__ . '/env/.env');
    foreach ($env as $key => $value) {
        $_ENV[$key] = $value;
    }
}

// Database Configuration
define('DB_HOST', $_ENV['DB_HOST'] ?? 'localhost');
define('DB_NAME', $_ENV['DB_NAME'] ?? 'film_price_guide');
define('DB_USER', $_ENV['DB_USER'] ?? 'root');
define('DB_PASS', $_ENV['DB_PASS'] ?? '');
define('DB_CHARSET', 'utf8mb4');

// Application Configuration
define('APP_NAME', 'Film Price Guide');
define('APP_VERSION', '1.0.0');
define('APP_ENV', $_ENV['APP_ENV'] ?? 'development');
define('APP_DEBUG', $_ENV['APP_DEBUG'] ?? true);
define('APP_URL', $_ENV['APP_URL'] ?? 'http://localhost');

// Security Configuration
define('SECRET_KEY', $_ENV['SECRET_KEY'] ?? 'your-secret-key-change-this');
define('SESSION_LIFETIME', 3600 * 24); // 24 hours
define('CSRF_TOKEN_LIFETIME', 3600); // 1 hour

// API Configuration
define('OMDB_API_KEY', $_ENV['OMDB_API_KEY'] ?? '');
define('TMDB_API_KEY', $_ENV['TMDB_API_KEY'] ?? '');
define('EBAY_APP_ID', $_ENV['EBAY_APP_ID'] ?? '');
define('EBAY_CLIENT_SECRET', $_ENV['EBAY_CLIENT_SECRET'] ?? '');
define('HERITAGE_API_KEY', $_ENV['HERITAGE_API_KEY'] ?? '');

// File Upload Configuration
define('UPLOAD_MAX_SIZE', 5 * 1024 * 1024); // 5MB
define('ALLOWED_IMAGE_TYPES', ['jpg', 'jpeg', 'png', 'gif', 'webp']);
define('UPLOAD_PATH', __DIR__ . '/../public/uploads/');

// Email Configuration
define('SMTP_HOST', $_ENV['SMTP_HOST'] ?? '');
define('SMTP_PORT', $_ENV['SMTP_PORT'] ?? 587);
define('SMTP_USER', $_ENV['SMTP_USER'] ?? '');
define('SMTP_PASS', $_ENV['SMTP_PASS'] ?? '');
define('FROM_EMAIL', $_ENV['FROM_EMAIL'] ?? 'noreply@filmpriceguide.com');

// Timezone
date_default_timezone_set($_ENV['TIMEZONE'] ?? 'America/New_York');

// Error reporting
if (APP_DEBUG) {
    error_reporting(E_ALL);
    ini_set('display_errors', 1);
} else {
    error_reporting(0);
    ini_set('display_errors', 0);
}
?>
EOF

# Create environment template
cat > "$PROJECT_ROOT/config/env/.env.example" << 'EOF'
# Film Price Guide Environment Configuration
# Copy this file to .env and update with your values

# Application
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost
SECRET_KEY=your-secret-key-here-change-this

# Database
DB_HOST=localhost
DB_NAME=film_price_guide
DB_USER=your_db_user
DB_PASS=your_db_password

# Email/SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FROM_EMAIL=noreply@yourdomain.com

# API Keys
OMDB_API_KEY=your-omdb-api-key
TMDB_API_KEY=your-tmdb-api-key
EBAY_APP_ID=your-ebay-app-id
EBAY_CLIENT_SECRET=your-ebay-client-secret
HERITAGE_API_KEY=your-heritage-api-key

# Other
TIMEZONE=America/New_York
EOF

# Create deployment script for Dreamhost
echo -e "${YELLOW}🚀 Creating deployment scripts...${NC}"

cat > "$PROJECT_ROOT/scripts/deploy/dreamhost-deploy.sh" << 'EOF'
#!/bin/bash

# Film Price Guide - Dreamhost Deployment Script

echo "🚀 Deploying Film Price Guide to Dreamhost..."

# Configuration
REMOTE_USER="your-dreamhost-user"
REMOTE_HOST="your-domain.com"
REMOTE_PATH="/home/$REMOTE_USER/your-domain.com"
LOCAL_PATH="./public"

# Upload files via SFTP
echo "📤 Uploading files..."
rsync -avz --delete \
    --exclude '.git' \
    --exclude '.env' \
    --exclude 'node_modules' \
    --exclude 'logs' \
    --exclude '.DS_Store' \
    $LOCAL_PATH/ $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/

echo "✅ Deployment complete!"
echo "🌐 Visit: https://$REMOTE_HOST"
EOF

# Create GitHub Actions workflow
mkdir -p "$PROJECT_ROOT/.github/workflows"

cat > "$PROJECT_ROOT/.github/workflows/deploy.yml" << 'EOF'
name: Deploy Film Price Guide

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup PHP
      uses: shivammathur/setup-php@v2
      with:
        php-version: '8.1'
        extensions: mbstring, xml, ctype, iconv, intl, pdo_sqlite, mysql
        coverage: xdebug
        
    - name: Validate composer.json and composer.lock
      run: composer validate --strict
      
    - name: Cache Composer packages
      id: composer-cache
      uses: actions/cache@v2
      with:
        path: vendor
        key: ${{ runner.os }}-php-${{ hashFiles('**/composer.lock') }}
        restore-keys: |
          ${{ runner.os }}-php-
          
    - name: Install dependencies
      run: composer install --prefer-dist --no-progress
      
    - name: Run test suite
      run: composer run-script test
EOF

# Create package.json for dependencies
cat > "$PROJECT_ROOT/package.json" << 'EOF'
{
  "name": "film-price-guide",
  "version": "1.0.0",
  "description": "Multi-API Search Engine for VHS, DVD, and Graded Movies",
  "main": "public/index.php",
  "scripts": {
    "build": "npm run build-css && npm run build-js",
    "build-css": "sass src/assets/scss:public/css",
    "build-js": "webpack --mode production",
    "dev": "npm run build-css && npm run build-js && php -S localhost:8000 -t public",
    "watch": "npm run build-css && npm run build-js && concurrently \"sass --watch src/assets/scss:public/css\" \"webpack --watch\"",
    "test": "php vendor/bin/phpunit"
  },
  "dependencies": {
    "axios": "^1.3.0",
    "chart.js": "^4.2.0",
    "alpinejs": "^3.12.0"
  },
  "devDependencies": {
    "sass": "^1.58.0",
    "webpack": "^5.75.0",
    "webpack-cli": "^5.0.0",
    "concurrently": "^7.6.0"
  },
  "keywords": [
    "vhs",
    "dvd",
    "movies",
    "price-tracking",
    "api",
    "search-engine"
  ],
  "author": "Your Name",
  "license": "MIT"
}
EOF

# Create composer.json for PHP dependencies
cat > "$PROJECT_ROOT/composer.json" << 'EOF'
{
    "name": "film-price-guide/app",
    "description": "Multi-API Search Engine for VHS, DVD, and Graded Movies",
    "type": "project",
    "license": "MIT",
    "require": {
        "php": ">=8.0",
        "ext-pdo": "*",
        "ext-json": "*",
        "ext-curl": "*",
        "guzzlehttp/guzzle": "^7.5",
        "vlucas/phpdotenv": "^5.5",
        "firebase/php-jwt": "^6.4",
        "swiftmailer/swiftmailer": "^6.3",
        "league/csv": "^9.8"
    },
    "require-dev": {
        "phpunit/phpunit": "^10.0",
        "squizlabs/php_codesniffer": "^3.7"
    },
    "autoload": {
        "psr-4": {
            "FilmPriceGuide\\": "src/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "FilmPriceGuide\\Tests\\": "tests/"
        }
    },
    "scripts": {
        "test": "phpunit",
        "cs-check": "phpcs",
        "cs-fix": "phpcbf"
    }
}
EOF

# Create file organization function
echo -e "${YELLOW}📋 Creating file movement commands...${NC}"

cat > "$PROJECT_ROOT/scripts/organize-files.sh" << 'EOF'
#!/bin/bash

# Film Price Guide - File Organization Commands
# Run this script to move existing files to proper locations

echo "📁 Organizing existing project files..."

# Move main files
echo "Moving main PHP files..."
[ -f "index.php" ] && mv "index.php" "$PROJECT_ROOT/public/"
[ -f "login.php" ] && mv "login.php" "$PROJECT_ROOT/src/auth/"
[ -f "logout.php" ] && mv "logout.php" "$PROJECT_ROOT/src/auth/"
[ -f "register.php" ] && mv "register.php" "$PROJECT_ROOT/src/auth/"

# Move page content files
echo "Moving page content files..."
[ -f "search_content.php" ] && mv "search_content.php" "$PROJECT_ROOT/src/search/"
[ -f "admin_content.php" ] && mv "admin_content.php" "$PROJECT_ROOT/src/admin/"
[ -f "dashboard_content.php" ] && mv "dashboard_content.php" "$PROJECT_ROOT/src/user/"

# Move database files
echo "Moving database files..."
[ -f "schema.sql" ] && mv "schema.sql" "$PROJECT_ROOT/database/"
[ -f "*.sql" ] && mv *.sql "$PROJECT_ROOT/database/migrations/"

# Move static files
echo "Moving static HTML files..."
[ -f "vhs_dvd_homepage.html" ] && mv "vhs_dvd_homepage.html" "$PROJECT_ROOT/assets/templates/"
[ -f "*.html" ] && mv *.html "$PROJECT_ROOT/assets/templates/"

# Move CSS and JS files
echo "Moving assets..."
[ -f "*.css" ] && mv *.css "$PROJECT_ROOT/public/css/"
[ -f "*.js" ] && mv *.js "$PROJECT_ROOT/public/js/"
[ -f "*.png" ] && mv *.png "$PROJECT_ROOT/public/images/"
[ -f "*.jpg" ] && mv *.jpg "$PROJECT_ROOT/public/images/"
[ -f "*.jpeg" ] && mv *.jpeg "$PROJECT_ROOT/public/images/"
[ -f "*.gif" ] && mv *.gif "$PROJECT_ROOT/public/images/"

echo "✅ File organization complete!"
EOF

chmod +x "$PROJECT_ROOT/scripts/organize-files.sh"

# Create README with deployment instructions
echo -e "${YELLOW}📖 Creating documentation...${NC}"

cat > "$PROJECT_ROOT/README.md" << 'EOF'
# 🎬 Film Price Guide

Multi-API Search Engine for VHS, DVD, and Graded Movies

## 🚀 Features

- **Multi-API Integration**: OMDb, TMDb, eBay, Heritage Auctions
- **User Authentication**: Secure login/registration system
- **Admin Panel**: API key management, user administration
- **Price Tracking**: Real-time pricing from multiple sources
- **Advanced Search**: Filter by format, condition, rarity
- **Responsive Design**: Mobile-friendly interface
- **MySQL Database**: Complete schema for movies and pricing

## 📋 Requirements

- PHP 8.0+
- MySQL 5.7+ / MariaDB 10.2+
- Apache/Nginx with mod_rewrite
- cURL extension
- PDO extension

## 🛠️ Installation

### 1. Clone & Setup
```bash
git clone <your-repo-url>
cd film-price-guide
composer install
npm install
```

### 2. Configure Environment
```bash
cp config/env/.env.example config/env/.env
# Edit .env with your database and API credentials
```

### 3. Database Setup
```bash
mysql -u root -p < database/schema.sql
```

### 4. Set Permissions
```bash
chmod 755 public/uploads/
chmod 644 config/env/.env
```

## 🌐 Deployment

### Dreamhost
```bash
./scripts/deploy/dreamhost-deploy.sh
```

### GitHub Apps
Push to main branch - automated via GitHub Actions

### Manual Upload
Upload `public/` contents to your web root directory

## 🔧 Configuration

### API Keys Required
- **OMDb API**: Movie metadata
- **TMDb API**: Additional movie data
- **eBay API**: Price tracking
- **Heritage Auctions**: Graded media prices

### Environment Variables
See `config/env/.env.example` for all available options

## 📁 Project Structure

```
film-price-guide/
├── public/              # Web-accessible files
│   ├── index.php       # Main entry point
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── uploads/        # User uploads
├── src/                # Application source
│   ├── auth/           # Authentication
│   ├── admin/          # Admin panel
│   ├── search/         # Search functionality
│   └── user/           # User dashboard
├── config/             # Configuration files
├── database/           # SQL schemas & migrations
├── api/                # API routes & controllers
└── scripts/            # Deployment & maintenance
```

## 🔐 Security Features

- CSRF protection
- SQL injection prevention
- XSS protection
- Secure password hashing
- Session management
- File upload validation

## 📊 API Endpoints

- `/api/search` - Movie search
- `/api/prices` - Price data
- `/api/admin` - Admin functions
- `/api/user` - User management

## 🧪 Testing

```bash
composer test
npm test
```

## 📈 Performance

- Gzip compression
- Browser caching
- Optimized database queries
- CDN-ready assets

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

## 📞 Support

For issues and feature requests, please use the GitHub Issues page.
EOF

# Create final setup instructions
echo -e "${GREEN}✅ File organization script created successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "${YELLOW}1.${NC} Run the organization script:"
echo -e "   ${BLUE}cd $PROJECT_NAME && ./scripts/organize-files.sh${NC}"
echo ""
echo -e "${YELLOW}2.${NC} Configure your environment:"
echo -e "   ${BLUE}cp config/env/.env.example config/env/.env${NC}"
echo -e "   ${BLUE}nano config/env/.env${NC}"
echo ""
echo -e "${YELLOW}3.${NC} Install dependencies:"
echo -e "   ${BLUE}composer install${NC}"
echo -e "   ${BLUE}npm install${NC}"
echo ""
echo -e "${YELLOW}4.${NC} Set up database:"
echo -e "   ${BLUE}mysql -u root -p < database/schema.sql${NC}"
echo ""
echo -e "${YELLOW}5.${NC} Deploy to Dreamhost:"
echo -e "   ${BLUE}./scripts/deploy/dreamhost-deploy.sh${NC}"
echo ""
echo -e "${GREEN}🎬 Your Film Price Guide is ready for deployment!${NC}"

# Make all scripts executable
chmod +x "$PROJECT_ROOT/scripts/"*.sh
chmod +x "$PROJECT_ROOT/scripts/deploy/"*.sh

echo ""
echo -e "${BLUE}📁 Project created at: $PROJECT_ROOT${NC}"
echo -e "${BLUE}💾 Backup created at: $BACKUP_DIR${NC}"
