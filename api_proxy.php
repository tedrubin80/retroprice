<?php
/*
FILE LOCATION: /api_proxy.php
SAVE AS: api_proxy.php (in your website root)

API Proxy - Bridges PHP frontend to Flask backend
*/

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

// Include API client
require_once 'includes/api_client.php';

session_start();

$action = $_GET['action'] ?? $_POST['action'] ?? '';
$method = $_SERVER['REQUEST_METHOD'];

// Get request data
$input_data = null;
if ($method === 'POST' || $method === 'PUT') {
    $input_data = json_decode(file_get_contents('php://input'), true) ?: $_POST;
}

// Route requests to Flask backend
try {
    $response = null;
    
    switch ($action) {
        case 'health_check':
            $response = flask_api()->healthCheck();
            break;
            
        case 'system_status':
            $response = flask_api()->getSystemStatus();
            break;
            
        case 'search_movies':
            $query = $_GET['q'] ?? $input_data['query'] ?? '';
            $filters = [
                'format' => $_GET['format'] ?? $input_data['format'] ?? null,
                'limit' => $_GET['limit'] ?? $input_data['limit'] ?? 50,
                'source' => $_GET['source'] ?? $input_data['source'] ?? 'database'
            ];
            $response = flask_api()->searchMovies($query, array_filter($filters));
            break;
            
        case 'movie_details':
            $movie_id = $_GET['id'] ?? $input_data['id'] ?? null;
            if ($movie_id) {
                $response = flask_api()->getMovieDetails($movie_id);
            } else {
                $response = ['success' => false, 'error' => 'Movie ID required'];
            }
            break;
            
        case