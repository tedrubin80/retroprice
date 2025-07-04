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
