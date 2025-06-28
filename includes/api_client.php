<?php
/*
FILE LOCATION: /includes/api_client.php
SAVE AS: api_client.php (in the includes/ directory)

PHP API Client - Bridge to Flask Backend
*/

class FlaskApiClient {
    private $base_url;
    private $timeout;
    
    public function __construct($base_url = null) {
        // Flask backend URL - adjust based on your setup
        $this->base_url = $base_url ?: $this->detectFlaskUrl();
        $this->timeout = 30;
    }
    
    private function detectFlaskUrl() {
        // Try different Flask backend locations
        $possible_urls = [
            'http://localhost:5000',           // Local development
            'https://' . $_SERVER['HTTP_HOST'] . '/flask',  // Subdirectory
            'https://' . $_SERVER['HTTP_HOST'] . ':5000',   // Different port
            'http://127.0.0.1:5000',          // Internal
        ];
        
        foreach ($possible_urls as $url) {
            if ($this->testConnection($url)) {
                return $url;
            }
        }
        
        // Fallback - assume Flask is at /flask subdirectory
        return 'https://' . $_SERVER['HTTP_HOST'] . '/flask';
    }
    
    private function testConnection($url) {
        try {
            $context = stream_context_create([
                'http' => [
                    'timeout' => 3,
                    'method' => 'GET'
                ]
            ]);
            
            $result = @file_get_contents($url . '/api/health', false, $context);
            return $result !== false;
        } catch (Exception $e) {
            return false;
        }
    }
    
    public function makeRequest($endpoint, $method = 'GET', $data = null, $headers = []) {
        $url = $this->base_url . $endpoint;
        
        // Default headers
        $default_headers = [
            'Content-Type: application/json',
            'Accept: application/json',
            'User-Agent: PHP-Wrapper/1.0'
        ];
        
        $headers = array_merge($default_headers, $headers);
        
        // Setup cURL
        $ch = curl_init();
        
        curl_setopt_array($ch, [
            CURLOPT_URL => $url,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => $this->timeout,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_SSL_VERIFYPEER => false, // For development
            CURLOPT_FOLLOWLOCATION => true,
        ]);
        
        // Set method and data
        switch (strtoupper($method)) {
            case 'POST':
                curl_setopt($ch, CURLOPT_POST, true);
                if ($data) {
                    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
                }
                break;
                
            case 'PUT':
                curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'PUT');
                if ($data) {
                    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
                }
                break;
                
            case 'DELETE':
                curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'DELETE');
                break;
        }
        
        // Execute request
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        
        curl_close($ch);
        
        // Handle errors
        if ($response === false) {
            return [
                'success' => false,
                'error' => 'cURL Error: ' . $error,
                'data' => null
            ];
        }
        
        // Parse JSON response
        $data = json_decode($response, true);
        
        return [
            'success' => $http_code >= 200 && $http_code < 300,
            'http_code' => $http_code,
            'data' => $data,
            'raw_response' => $response
        ];
    }
    
    // Convenience methods for common operations
    public function get($endpoint, $headers = []) {
        return $this->makeRequest($endpoint, 'GET', null, $headers);
    }
    
    public function post($endpoint, $data = null, $headers = []) {
        return $this->makeRequest($endpoint, 'POST', $data, $headers);
    }
    
    public function put($endpoint, $data = null, $headers = []) {
        return $this->makeRequest($endpoint, 'PUT', $data, $headers);
    }
    
    public function delete($endpoint, $headers = []) {
        return $this->makeRequest($endpoint, 'DELETE', null, $headers);
    }
    
    // Specific API methods
    public function healthCheck() {
        return $this->get('/api/health');
    }
    
    public function searchMovies($query, $filters = []) {
        $params = array_merge(['q' => $query], $filters);
        $endpoint = '/api/search?' . http_build_query($params);
        return $this->get($endpoint);
    }
    
    public function getMovieDetails($movie_id) {
        return $this->get("/api/search/films/{$movie_id}");
    }
    
    public function getUserWatchlist($user_id) {
        return $this->get("/api/search/watchlist", ['Authorization: Bearer ' . $this->getUserToken()]);
    }
    
    public function addToWatchlist($user_id, $movie_id, $target_price = null) {
        $data = [
            'film_id' => $movie_id,
            'target_price' => $target_price
        ];
        return $this->post('/api/search/watchlist', $data, ['Authorization: Bearer ' . $this->getUserToken()]);
    }
    
    public function getSystemStatus() {
        return $this->get('/api/admin/status');
    }
    
    public function updateApiKeys($api_keys) {
        return $this->post('/api/admin/api-keys', $api_keys);
    }
    
    private function getUserToken() {
        // Generate or retrieve user token for Flask authentication
        // This could be stored in PHP session
        return $_SESSION['flask_token'] ?? 'php-session-' . session_id();
    }
    
    public function getBaseUrl() {
        return $this->base_url;
    }
    
    public function isFlaskAvailable() {
        $health = $this->healthCheck();
        return $health['success'];
    }
}

// Global instance
$flask_api = new FlaskApiClient();

// Helper function
function flask_api() {
    global $flask_api;
    return $flask_api;
}
?>