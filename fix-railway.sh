#!/bin/bash

# ================================================================
# Film Price Guide - Railway Deployment Setup Script
# Multi-API Search Engine for VHS, DVD, and Graded Movies
# Railway.app Compatible - Full composer/npm support
# ================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

PROJECT_NAME="film-price-guide"
PROJECT_ROOT="$(pwd)/$PROJECT_NAME"

echo -e "${BLUE}🚂 Film Price Guide - Railway Deployment Setup${NC}"
echo -e "${BLUE}===============================================${NC}"
echo ""
echo -e "${GREEN}✅ Railway Benefits for Your Project:${NC}"
echo -e "${YELLOW}   • Full composer & npm support${NC}"
echo -e "${YELLOW}   • Built-in MySQL database${NC}"
echo -e "${YELLOW}   • Automatic deployments from Git${NC}"
echo -e "${YELLOW}   • Environment variable management${NC}"
echo -e "${YELLOW}   • Free tier available${NC}"
echo ""

# Create Railway-optimized directory structure
echo -e "${YELLOW}📁 Creating Railway-optimized structure...${NC}"
mkdir -p "$PROJECT_ROOT"/{public,src,config,database,api,assets,scripts}

# Create subdirectories
mkdir -p "$PROJECT_ROOT/public"/{css,js,images,uploads}
mkdir -p "$PROJECT_ROOT/src"/{auth,admin,search,user,common}
mkdir -p "$PROJECT_ROOT/config"/{env,api-keys}
mkdir -p "$PROJECT_ROOT/database"/{migrations,seeds}
mkdir -p "$PROJECT_ROOT/api"/{routes,controllers,models}
mkdir -p "$PROJECT_ROOT/assets"/{templates,static}
mkdir -p "$PROJECT_ROOT/scripts"/{railway,maintenance}

echo -e "${GREEN}✅ Railway structure created${NC}"

# Create Railway-specific configuration
echo -e "${YELLOW}🚂 Creating Railway configuration...${NC}"

# railway.json - Railway deployment configuration
cat > "$PROJECT_ROOT/railway.json" << 'EOF'
{
  "deploy": {
    "startCommand": "php -S 0.0.0.0:$PORT -t public",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  },
  "build": {
    "builder": "HEROKU_BUILDPACKS",
    "buildpacks": [
      "heroku/php"
    ]
  },
  "environments": {
    "production": {
      "variables": {
        "APP_ENV": "production",
        "APP_DEBUG": "false"
      }
    },
    "staging": {
      "variables": {
        "APP_ENV": "staging", 
        "APP_DEBUG": "true"
      }
    }
  }
}
EOF

# Create composer.json for Railway PHP dependencies
cat > "$PROJECT_ROOT/composer.json" << 'EOF'
{
    "name": "film-price-guide/railway-app",
    "description": "Multi-API Search Engine for VHS, DVD, and Graded Movies - Railway Deployment",
    "type": "project",
    "license": "MIT",
    "require": {
        "php": "^8.1",
        "ext-pdo": "*",
        "ext-json": "*",
        "ext-curl": "*",
        "ext-mbstring": "*",
        "guzzlehttp/guzzle": "^7.5",
        "vlucas/phpdotenv": "^5.5",
        "firebase/php-jwt": "^6.4",
        "swiftmailer/swiftmailer": "^6.3",
        "league/csv": "^9.8",
        "monolog/monolog": "^3.3"
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
    "scripts": {
        "post-install-cmd": [
            "php scripts/railway/post-deploy.php"
        ],
        "test": "phpunit",
        "start": "php -S 0.0.0.0:8080 -t public"
    },
    "config": {
        "platform": {
            "php": "8.1"
        }
    }
}
EOF

# Create package.json for Railway frontend dependencies
cat > "$PROJECT_ROOT/package.json" << 'EOF'
{
  "name": "film-price-guide-railway",
  "version": "1.0.0",
  "description": "Multi-API Search Engine for VHS, DVD, and Graded Movies",
  "main": "public/index.php",
  "scripts": {
    "build": "npm run build-css && npm run build-js",
    "build-css": "sass assets/scss:public/css --style compressed",
    "build-js": "webpack --mode production",
    "dev": "concurrently \"npm run watch-css\" \"npm run watch-js\"",
    "watch-css": "sass --watch assets/scss:public/css",
    "watch-js": "webpack --watch --mode development",
    "postinstall": "npm run build"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "chart.js": "^4.4.0",
    "alpinejs": "^3.13.0"
  },
  "devDependencies": {
    "sass": "^1.69.0",
    "webpack": "^5.89.0",
    "webpack-cli": "^5.1.0",
    "concurrently": "^8.2.0",
    "terser-webpack-plugin": "^5.3.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
}
EOF

# Create Railway-optimized index.php
echo -e "${YELLOW}📝 Creating Railway-optimized index.php...${NC}"

cat > "$PROJECT_ROOT/public/index.php" << 'EOF'
<?php
/**
 * Film Price Guide - Railway Entry Point
 * Multi-API Search Engine for VHS, DVD, and Graded Movies
 * Optimized for Railway.app deployment
 */

// Start session with Railway-compatible settings
ini_set('session.cookie_secure', 1);
ini_set('session.cookie_httponly', 1);
session_start();

// Railway environment detection
$is_railway = isset($_ENV['RAILWAY_ENVIRONMENT']) || isset($_SERVER['RAILWAY_ENVIRONMENT']);
$port = $_ENV['PORT'] ?? $_SERVER['PORT'] ?? 8080;

// Security headers for Railway
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('X-XSS-Protection: 1; mode=block');
header('Strict-Transport-Security: max-age=31536000; includeSubDomains');

// Load Railway configuration
if ($is_railway) {
    // Railway automatically loads environment variables
    $database_url = parse_url($_ENV['DATABASE_URL'] ?? '');
    define('DB_HOST', $database_url['host'] ?? 'localhost');
    define('DB_NAME', ltrim($database_url['path'] ?? '/film_price_guide', '/'));
    define('DB_USER', $database_url['user'] ?? 'root');
    define('DB_PASS', $database_url['pass'] ?? '');
} else {
    // Local development
    require_once '../config/config.php';
}

// Load application components
require_once '../src/common/functions.php';
require_once '../src/auth/auth.php';

// Get current page
$page = $_GET['page'] ?? 'home';
$allowed_pages = ['home', 'search', 'dashboard', 'admin', 'profile', 'api-test'];

if (!in_array($page, $allowed_pages)) {
    $page = 'home';
}

// Admin access check
if ($page === 'admin' && (!isset($_SESSION['is_admin']) || !$_SESSION['is_admin'])) {
    header('Location: index.php?page=login&error=admin_required');
    exit;
}

// Railway health check endpoint
if ($page === 'health') {
    http_response_code(200);
    echo json_encode([
        'status' => 'healthy',
        'environment' => $is_railway ? 'railway' : 'local',
        'timestamp' => date('c'),
        'version' => '1.0.0'
    ]);
    exit;
}

// Include application layout
include '../src/common/header.php';

// Route to appropriate page
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

include '../src/common/footer.php';
?>
EOF

# Create Railway environment configuration
cat > "$PROJECT_ROOT/config/railway-config.php" << 'EOF'
<?php
/**
 * Railway-specific configuration for Film Price Guide
 */

// Railway environment detection
function is_railway_environment() {
    return isset($_ENV['RAILWAY_ENVIRONMENT']) || isset($_SERVER['RAILWAY_ENVIRONMENT']);
}

// Get Railway database configuration
function get_railway_database_config() {
    if (!isset($_ENV['DATABASE_URL'])) {
        return null;
    }
    
    $url = parse_url($_ENV['DATABASE_URL']);
    return [
        'host' => $url['host'],
        'port' => $url['port'] ?? 3306,
        'database' => ltrim($url['path'], '/'),
        'username' => $url['user'],
        'password' => $url['pass'],
        'charset' => 'utf8mb4'
    ];
}

// Railway-specific database connection
function get_railway_database_connection() {
    $config = get_railway_database_config();
    if (!$config) {
        throw new Exception('DATABASE_URL not configured in Railway');
    }
    
    $dsn = sprintf(
        'mysql:host=%s;port=%d;dbname=%s;charset=%s',
        $config['host'],
        $config['port'],
        $config['database'],
        $config['charset']
    );
    
    try {
        $pdo = new PDO($dsn, $config['username'], $config['password'], [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]);
        return $pdo;
    } catch (PDOException $e) {
        error_log('Railway database connection failed: ' . $e->getMessage());
        throw $e;
    }
}

// Railway logging configuration
function setup_railway_logging() {
    if (is_railway_environment()) {
        // Railway captures stdout/stderr automatically
        ini_set('log_errors', 1);
        ini_set('error_log', 'php://stderr');
    }
}

// Initialize Railway configuration
if (is_railway_environment()) {
    setup_railway_logging();
}
?>
EOF

# Create Railway deployment script
cat > "$PROJECT_ROOT/scripts/railway/deploy.sh" << 'EOF'
#!/bin/bash

# Film Price Guide - Railway Deployment Script

echo "🚂 Deploying Film Price Guide to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
railway login

# Link to Railway project (if not already linked)
echo "🔗 Linking to Railway project..."
railway link

# Set environment variables
echo "⚙️  Setting environment variables..."
railway variables set APP_ENV=production
railway variables set APP_DEBUG=false

# Deploy to Railway
echo "🚀 Deploying..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your app is available at your Railway domain"
EOF

chmod +x "$PROJECT_ROOT/scripts/railway/deploy.sh"

# Create Railway post-deployment script
cat > "$PROJECT_ROOT/scripts/railway/post-deploy.php" << 'EOF'
<?php
/**
 * Railway Post-Deployment Script
 * Runs after successful deployment to set up database and cache
 */

echo "🚂 Running Railway post-deployment setup...\n";

try {
    // Check if we're in Railway environment
    if (!isset($_ENV['DATABASE_URL'])) {
        echo "⚠️  DATABASE_URL not found - skipping database setup\n";
        exit(0);
    }
    
    // Include Railway configuration
    require_once __DIR__ . '/../../config/railway-config.php';
    
    // Test database connection
    echo "🔗 Testing database connection...\n";
    $pdo = get_railway_database_connection();
    echo "✅ Database connection successful\n";
    
    // Check if tables exist
    $tables_exist = $pdo->query("SHOW TABLES LIKE 'users'")->rowCount() > 0;
    
    if (!$tables_exist) {
        echo "📊 Setting up database tables...\n";
        
        // Run database migrations
        $schema_file = __DIR__ . '/../../database/schema.sql';
        if (file_exists($schema_file)) {
            $sql = file_get_contents($schema_file);
            $pdo->exec($sql);
            echo "✅ Database schema created\n";
        } else {
            echo "⚠️  Schema file not found\n";
        }
    } else {
        echo "✅ Database tables already exist\n";
    }
    
    // Create upload directories
    $upload_dirs = [
        __DIR__ . '/../../public/uploads',
        __DIR__ . '/../../public/uploads/avatars',
        __DIR__ . '/../../public/uploads/movies'
    ];
    
    foreach ($upload_dirs as $dir) {
        if (!is_dir($dir)) {
            mkdir($dir, 0755, true);
            echo "📁 Created directory: $dir\n";
        }
    }
    
    echo "🎉 Post-deployment setup complete!\n";
    
} catch (Exception $e) {
    echo "❌ Post-deployment setup failed: " . $e->getMessage() . "\n";
    exit(1);
}
?>
EOF

# Create Railway environment template
cat > "$PROJECT_ROOT/.env.railway" << 'EOF'
# Film Price Guide - Railway Environment Variables
# Set these in your Railway dashboard under "Variables"

# Application
APP_ENV=production
APP_DEBUG=false
APP_URL=https://your-app-name.railway.app

# Database (Automatically set by Railway MySQL service)
# DATABASE_URL=mysql://user:password@host:port/database

# API Keys (Set these in Railway dashboard)
OMDB_API_KEY=your-omdb-api-key
TMDB_API_KEY=your-tmdb-api-key
EBAY_APP_ID=your-ebay-app-id
EBAY_CLIENT_SECRET=your-ebay-client-secret
HERITAGE_API_KEY=your-heritage-api-key

# Security
SECRET_KEY=your-production-secret-key

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FROM_EMAIL=noreply@yourdomain.com
EOF

# Create Railway deployment README
cat > "$PROJECT_ROOT/RAILWAY-DEPLOYMENT.md" << 'EOF'
# 🚂 Railway Deployment Guide

## Quick Deploy to Railway

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial Film Price Guide commit"
git branch -M main
git remote add origin https://github.com/yourusername/film-price-guide.git
git push -u origin main
```

### 2. Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Choose "Deploy from GitHub repo"
4. Select your `film-price-guide` repository
5. Railway will auto-detect your PHP app

### 3. Add MySQL Database
1. In your Railway project dashboard
2. Click "Add Service" → "Database" → "MySQL"
3. Railway will automatically set `DATABASE_URL`

### 4. Configure Environment Variables
In Railway dashboard → "Variables" tab, add:

```bash
# Required API Keys
OMDB_API_KEY=your-omdb-api-key
TMDB_API_KEY=your-tmdb-api-key
EBAY_APP_ID=your-ebay-app-id
EBAY_CLIENT_SECRET=your-ebay-client-secret

# Application Settings
APP_ENV=production
APP_DEBUG=false
SECRET_KEY=your-production-secret-key-here
```

### 5. Custom Domain (Optional)
1. In Railway dashboard → "Settings" → "Domains"
2. Add your custom domain
3. Configure DNS CNAME to point to Railway

## 🔧 Railway Benefits

✅ **Automatic Deployments** - Push to GitHub = instant deploy  
✅ **Built-in Database** - MySQL included, no separate hosting  
✅ **Environment Variables** - Secure API key management  
✅ **Composer Support** - All PHP dependencies work  
✅ **Free Tier** - $5/month free credits  
✅ **Instant Scaling** - Handles traffic spikes automatically  

## 📊 Monitoring

Railway provides built-in monitoring:
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, network usage
- **Deployments**: Track deployment history
- **Database**: Query performance and usage

## 🛠️ Development Workflow

1. **Local Development**:
   ```bash
   composer install
   npm install
   php -S localhost:8080 -t public
   ```

2. **Deploy Changes**:
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   # Railway auto-deploys!
   ```

3. **View Logs**:
   ```bash
   railway logs
   ```

## 🔍 Troubleshooting

### Database Connection Issues
1. Check `DATABASE_URL` is set in Railway variables
2. Verify MySQL service is running
3. Check logs for connection errors

### API Integration Issues
1. Verify all API keys are set in Railway variables
2. Check API key permissions and quotas
3. Review application logs for API errors

### Build Failures
1. Check `composer.json` syntax
2. Verify PHP version compatibility
3. Review build logs in Railway dashboard

## 🎯 Production Tips

- Use Railway's built-in SSL certificates
- Enable health checks at `/health` endpoint
- Monitor resource usage in Railway dashboard
- Set up error alerting via Railway webhooks
- Use Railway's backup features for database

---

🎬 **Your Film Price Guide will be live at**: `https://your-app-name.railway.app`
EOF

# Create GitHub Actions for Railway
mkdir -p "$PROJECT_ROOT/.github/workflows"

cat > "$PROJECT_ROOT/.github/workflows/railway-deploy.yml" << 'EOF'
name: Deploy to Railway

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup PHP
      uses: shivammathur/setup-php@v2
      with:
        php-version: '8.1'
        extensions: mbstring, xml, ctype, iconv, intl, pdo, mysql
        
    - name: Validate composer.json
      run: composer validate
      
    - name: Install PHP dependencies
      run: composer install --prefer-dist --no-progress
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        
    - name: Install NPM dependencies
      run: npm install
      
    - name: Build assets
      run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Railway
      uses: bervProject/railway-deploy@v1.0.6
      with:
        railway_token: ${{ secrets.RAILWAY_TOKEN }}
        service: ${{ secrets.RAILWAY_SERVICE_ID }}
EOF

# Create file organization for Railway
cat > "$PROJECT_ROOT/scripts/organize-for-railway.sh" << 'EOF'
#!/bin/bash

# Film Price Guide - Railway File Organization

echo "🚂 Organizing files for Railway deployment..."

# Move existing files to proper locations
echo "📁 Moving existing project files..."

# Main PHP files
[ -f "index.php" ] && mv "index.php" "public/"
[ -f "login.php" ] && mv "login.php" "src/auth/"
[ -f "logout.php" ] && mv "logout.php" "src/auth/"

# Page content
[ -f "*_content.php" ] && mv *_content.php "src/"
[ -f "search_content.php" ] && mv "search_content.php" "src/search/"
[ -f "admin_content.php" ] && mv "admin_content.php" "src/admin/"

# Database files
[ -f "schema.sql" ] && mv "schema.sql" "database/"
[ -f "*.sql" ] && mv *.sql "database/migrations/" 2>/dev/null

# Static assets
[ -f "*.html" ] && mv *.html "assets/templates/" 2>/dev/null
[ -f "*.css" ] && mv *.css "public/css/" 2>/dev/null
[ -f "*.js" ] && mv *.js "public/js/" 2>/dev/null
[ -f "*.png" ] && mv *.png "public/images/" 2>/dev/null
[ -f "*.jpg" ] && mv *.jpg "public/images/" 2>/dev/null

echo "✅ Files organized for Railway!"
echo ""
echo "🚀 Next steps:"
echo "1. git init && git add . && git commit -m 'Initial commit'"
echo "2. Push to GitHub"
echo "3. Deploy on Railway"
echo "4. Add environment variables in Railway dashboard"
EOF

chmod +x "$PROJECT_ROOT/scripts/organize-for-railway.sh"

echo -e "${GREEN}✅ Railway deployment setup complete!${NC}"
echo ""
echo -e "${BLUE}🚂 Railway Deployment Benefits:${NC}"
echo -e "${YELLOW}   ✅ Full composer & npm support${NC}"
echo -e "${YELLOW}   ✅ Built-in MySQL database${NC}"
echo -e "${YELLOW}   ✅ Automatic Git deployments${NC}"
echo -e "${YELLOW}   ✅ Environment variable management${NC}"
echo -e "${YELLOW}   ✅ Free tier with $5/month credits${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "${YELLOW}1.${NC} Run organization script:"
echo -e "   ${BLUE}cd $PROJECT_NAME && ./scripts/organize-for-railway.sh${NC}"
echo ""
echo -e "${YELLOW}2.${NC} Initialize Git repository:"
echo -e "   ${BLUE}git init && git add . && git commit -m 'Initial commit'${NC}"
echo ""
echo -e "${YELLOW}3.${NC} Push to GitHub:"
echo -e "   ${BLUE}git remote add origin https://github.com/yourusername/film-price-guide.git${NC}"
echo -e "   ${BLUE}git push -u origin main${NC}"
echo ""
echo -e "${YELLOW}4.${NC} Deploy on Railway:"
echo -e "   ${BLUE}Visit railway.app → Deploy from GitHub repo${NC}"
echo ""
echo -e "${YELLOW}5.${NC} Add MySQL database:"
echo -e "   ${BLUE}Railway dashboard → Add Service → Database → MySQL${NC}"
echo ""
echo -e "${GREEN}🎬 Your Film Price Guide will be live with full functionality!${NC}"

echo ""
echo -e "${BLUE}📁 Railway project created at: $PROJECT_ROOT${NC}"
echo -e "${PURPLE}📖 Read RAILWAY-DEPLOYMENT.md for detailed instructions${NC}"