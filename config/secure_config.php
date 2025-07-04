<?php
/*
FILE LOCATION: /config/secure_config.php
SAVE AS: secure_config.php (in the config/ directory)

SECURE DATABASE CONFIGURATION
This file should be placed OUTSIDE the web root or protected with .htaccess
*/

// Prevent direct access
if (!defined('FILM_PRICE_GUIDE_ACCESS')) {
    die('Direct access not permitted');
}

// Database Configuration - UPDATE WITH YOUR ACTUAL CREDENTIALS
$secure_db_config = [
    'host' => 'mysql.dreamhost.com',           // Your Dreamhost MySQL host
    'dbname' => 'yourusername_filmguide',      // Your actual database name
    'username' => 'yourusername_dbadmin',      // Your actual database username  
    'password' => 'your_actual_password_here', // Your actual database password
    'charset' => 'utf8mb4',
    'options' => [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES => false,
        PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4"
    ]
];

// API Keys Configuration (encrypted storage recommended)
$secure_api_config = [
    'ebay' => [
        'app_id' => '',     // Your eBay App ID
        'cert_id' => '',    // Your eBay Cert ID  
        'dev_id' => '',     // Your eBay Dev ID
    ],
    'omdb' => [
        'api_key' => '',    // Your OMDb API Key
    ],
    'tmdb' => [
        'api_key' => '',    // Your TMDb API Key
    ],
    'email' => [
        'smtp_host' => '',      // SMTP server
        'smtp_port' => 587,     // SMTP port
        'smtp_user' => '',      // SMTP username
        'smtp_pass' => '',      // SMTP password
    ]
];

// Application Security Settings
$secure_app_config = [
    'secret_key' => 'your-super-secret-application-key-here',
    'jwt_secret' => 'your-jwt-secret-key-here',
    'encryption_key' => 'your-encryption-key-for-api-storage',
    'session_name' => 'FILMPRICEGUIDE_SESSION',
    'cookie_domain' => '.yourdomain.com',
    'admin_email' => 'admin@yourdomain.com'
];

// Environment Detection
$secure_environment = [
    'is_production' => $_SERVER['HTTP_HOST'] !== 'localhost',
    'debug_mode' => $_SERVER['HTTP_HOST'] === 'localhost',
    'log_level' => $_SERVER['HTTP_HOST'] === 'localhost' ? 'DEBUG' : 'WARNING'
];

// Return configuration based on what's requested
function get_secure_config($type = 'database') {
    global $secure_db_config, $secure_api_config, $secure_app_config, $secure_environment;
    
    switch($type) {
        case 'database':
            return $secure_db_config;
        case 'api':
            return $secure_api_config;
        case 'app':
            return $secure_app_config;
        case 'environment':
            return $secure_environment;
        case 'all':
            return [
                'database' => $secure_db_config,
                'api' => $secure_api_config,
                'app' => $secure_app_config,
                'environment' => $secure_environment
            ];
        default:
            return null;
    }
}
?>