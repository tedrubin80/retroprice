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
