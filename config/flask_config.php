<?php
/*
FILE LOCATION: /config/flask_config.php
SAVE AS: flask_config.php (in the config/ directory)

Flask Backend Configuration for PHP Wrapper
*/

// Flask Backend Configuration
define('FLASK_ENABLED', true);
define('FLASK_BASE_URL', 'http://localhost:5000'); // Update this
define('FLASK_TIMEOUT', 30);

// Flask Deployment Options
$flask_config = [
    'deployment_mode' => 'subdirectory', // 'subdirectory', 'port', 'separate_domain'
    
    // Subdirectory mode: yourdomain.com/flask/
    'subdirectory_path' => '/flask',
    
    // Port mode: yourdomain.com:5000
    'port' => 5000,
    
    // Separate domain mode: api.yourdomain.com
    'api_domain' => 'api.yourdomain.com',
    
    // Auto-detection
    'auto_detect' => true,
];

// Flask API Endpoints Mapping
$flask_endpoints = [
    'health' => '/api/health',
    'status' => '/api/status',
    'search' => '/api/search',
    'movie_details' => '/api/search/films/{id}',
    'watchlist' => '/api/search/watchlist',
    'admin_status' => '/api/admin/status',
    'admin_api_keys' => '/api/admin/api-keys',
    'auth_login' => '/api/auth/login',
    'auth_logout' => '/api/auth/logout',
    'ebay_search' => '/api/ebay/search',
];

function get_flask_url() {
    global $flask_config;
    
    $base_domain = $_SERVER['HTTP_HOST'];
    $protocol = isset($_SERVER['HTTPS']) ? 'https' : 'http';
    
    switch ($flask_config['deployment_mode']) {
        case 'subdirectory':
            return $protocol . '://' . $base_domain . $flask_config['subdirectory_path'];
            
        case 'port':
            return $protocol . '://' . $base_domain . ':' . $flask_config['port'];
            
        case 'separate_domain':
            return $protocol . '://' . $flask_config['api_domain'];
            
        default:
            // Auto-detect
            $possible_urls = [
                $protocol . '://' . $base_domain . '/flask',
                $protocol . '://' . $base_domain . ':5000',
                'http://localhost:5000',
                'http://127.0.0.1:5000'
            ];
            
            foreach ($possible_urls as $url) {
                if (test_flask_connection($url)) {
                    return $url;
                }
            }
            
            // Fallback
            return 'http://localhost:5000';
    }
}

function test_flask_connection($url) {
    $context = stream_context_create([
        'http' => [
            'timeout' => 3,
            'method' => 'GET'
        ]
    ]);
    
    $result = @file_get_contents($url . '/api/health', false, $context);
    return $result !== false;
}

function get_flask_endpoint($endpoint_name) {
    global $flask_endpoints;
    return $flask_endpoints[$endpoint_name] ?? null;
}

function is_flask_available() {
    $flask_url = get_flask_url();
    return test_flask_connection($flask_url);
}

// Initialize Flask connection check
$FLASK_AVAILABLE = is_flask_available();
$FLASK_URL = get_flask_url();

// Configuration for different deployment scenarios

// OPTION 1: Flask as Subdirectory (Recommended for Dreamhost)
// yourdomain.com/flask/ -> Flask app
// Requires .htaccess redirect rules

// OPTION 2: Flask on Different Port
// yourdomain.com:5000 -> Flask app
// May not work on shared hosting

// OPTION 3: Flask on Separate Subdomain
// api.yourdomain.com -> Flask app
// Requires DNS configuration
?>