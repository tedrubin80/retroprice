#!/bin/bash

# Film Price Guide - Setup Script
# Automated installation and environment setup

set -e  # Exit on any error

echo "🎬 Film Price Guide - Setup Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    else
        print_error "pip3 is not installed. Please install pip and try again."
        exit 1
    fi
}

# Create project directories
create_directories() {
    print_status "Creating project directories..."
    
    # Backend directories
    mkdir -p backend/{config,endpoints,services,models,utils,migrations/versions,tests,static/{css,js,images},logs}
    
    # Frontend directories  
    mkdir -p frontend/{css,js,images}
    
    # Database and docs
    mkdir -p database/backups
    mkdir -p docs
    mkdir -p scripts
    
    # Create __init__.py files for Python packages
    touch backend/__init__.py
    touch backend/config/__init__.py
    touch backend/endpoints/__init__.py
    touch backend/services/__init__.py
    touch backend/models/__init__.py
    touch backend/utils/__init__.py
    touch backend/tests/__init__.py
    
    print_success "Project directories created"
}

# Create virtual environment
create_venv() {
    print_status "Creating Python virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Skipping creation."
    else
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
}

# Activate virtual environment and install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies from requirements.txt
    if [ -f "backend/requirements.txt" ]; then
        pip install -r backend/requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found in backend/ directory"
        exit 1
    fi
}

# Create environment file from template
create_env_file() {
    print_status "Setting up environment configuration..."
    
    if [ -f "backend/.env" ]; then
        print_warning ".env file already exists. Skipping creation."
    else
        if [ -f "backend/.env.example" ]; then
            cp backend/.env.example backend/.env
            print_success "Created .env file from template"
            print_warning "Please edit backend/.env and add your API keys!"
        else
            # Create basic .env file
            cat > backend/.env << EOF
# Film Price Guide Environment Configuration
# Edit these values with your actual API keys and settings

# Flask Configuration
SECRET_KEY=change-this-secret-key-in-production
FLASK_ENV=development
DEBUG=True

# Database Configuration
DATABASE_TYPE=mysql
DATABASE_URL=mysql://username:password@localhost:3306/film_price_guide

# eBay API Configuration (Required)
EBAY_APP_ID=your_ebay_app_id_here
EBAY_CERT_ID=your_ebay_cert_id_here
EBAY_DEV_ID=your_ebay_dev_id_here
EBAY_USER_TOKEN=your_ebay_user_token_here
EBAY_ENVIRONMENT=sandbox

# eBay Deletion Notifications (Required for compliance)
EBAY_VERIFICATION_TOKEN=your_32_to_80_char_token_here
EBAY_DELETION_ENDPOINT_URL=https://yourdomain.com/api/ebay/deletion/notifications

# OMDb API Configuration (Optional)
OMDB_API_KEY=your_omdb_api_key_here
OMDB_PLAN_TYPE=free

# TMDb API Configuration (Optional)
TMDB_API_KEY=your_tmdb_api_key_here
TMDB_API_VERSION=3

# Application Settings
APP_NAME=Film Price Guide
ADMIN_EMAIL=admin@yoursite.com

# Feature Flags
ENABLE_PRICE_UPDATES=True
ENABLE_RATE_LIMITING=True
ENABLE_EMAIL_ALERTS=True
EOF
            print_success "Created basic .env file"
            print_warning "Please edit backend/.env and add your actual API keys!"
        fi
    fi
}

# Create basic gitignore
create_gitignore() {
    print_status "Creating .gitignore file..."
    
    if [ -f ".gitignore" ]; then
        print_warning ".gitignore already exists. Skipping creation."
    else
        cat > .gitignore << EOF
# Environment variables
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# Database
*.db
*.sqlite3
database/backups/*.sql

# Logs
logs/*.log
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Flask
instance/
.webassets-cache

# Testing
.coverage
.pytest_cache/
htmlcov/

# Node.js (if using npm for frontend tools)
node_modules/
npm-debug.log
yarn-error.log

# Production files
*.pid
*.sock
EOF
        print_success ".gitignore created"
    fi
}

# Database setup helper
setup_database() {
    print_status "Database setup information..."
    
    print_warning "Manual database setup required:"
    echo "1. Install MySQL/MariaDB on your system"
    echo "2. Create database: CREATE DATABASE film_price_guide;"
    echo "3. Import schema: mysql -u username -p film_price_guide < database/schema.sql"
    echo "4. Update DATABASE_URL in backend/.env"
    echo ""
}

# Create basic README
create_readme() {
    print_status "Creating README.md..."
    
    if [ -f "README.md" ]; then
        print_warning "README.md already exists. Skipping creation."
    else
        cat > README.md << EOF
# Film Price Guide

Track real-time movie prices from eBay with comprehensive film data.

## Quick Start

1. Run setup script: \`./setup.sh\`
2. Edit \`backend/.env\` with your API keys
3. Set up MySQL database
4. Run the application: \`./run.sh\`

## Features

- eBay sold price tracking
- Movie metadata from OMDb/TMDb
- Admin configuration panel
- eBay compliance (deletion notifications)

## API Keys Required

- eBay Developer (App ID, Cert ID, Dev ID)
- OMDb API Key (optional)
- TMDb API Key (optional)

## Setup

\`\`\`bash
chmod +x setup.sh
./setup.sh
\`\`\`

## Run

\`\`\`bash
chmod +x run.sh
./run.sh
\`\`\`

## Documentation

See \`docs/\` directory for detailed documentation.
EOF
        print_success "README.md created"
    fi
}

# Create run script
create_run_script() {
    print_status "Creating run script..."
    
    cat > run.sh << EOF
#!/bin/bash

# Film Price Guide - Run Script

echo "🎬 Starting Film Price Guide..."

# Activate virtual environment
source venv/bin/activate

# Set Flask app
export FLASK_APP=backend/app.py

# Run the application
cd backend && python app.py
EOF

    chmod +x run.sh
    print_success "Run script created (run.sh)"
}

# Main setup function
main() {
    echo ""
    print_status "Starting Film Price Guide setup..."
    echo ""
    
    # System checks
    check_python
    check_pip
    
    # Project setup
    create_directories
    create_venv
    install_dependencies
    create_env_file
    create_gitignore
    create_readme
    create_run_script
    
    # Information
    setup_database
    
    echo ""
    print_success "Setup completed successfully! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Edit backend/.env with your API keys"
    echo "2. Set up MySQL database using database/schema.sql"
    echo "3. Run the application: ./run.sh"
    echo ""
    print_warning "Don't forget to configure your eBay, OMDb, and TMDb API keys!"
    echo ""
}

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
EOF