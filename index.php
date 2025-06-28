<?php
/*
FILE LOCATION: /index.php (replace your existing index.php)
SAVE AS: index.php (in your website root)

PHP Wrapper for Flask Backend - Main Router
*/

// Start session
session_start();

// Include configuration and API client
require_once 'config/flask_config.php';
require_once 'includes/api_client.php';

// Get page parameter
$page = $_GET['page'] ?? 'home';
$page = preg_replace('/[^a-zA-Z0-9\-]/', '', $page);

// Check Flask backend status
$flask_status = flask_api()->isFlaskAvailable();

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Film Price Guide - Multi-API Search Engine</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
            min-height: 100vh;
            color: white;
        }

        .navbar {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }

        .navbar-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 1.5rem;
            font-weight: bold;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .nav-links {
            display: flex;
            gap: 2rem;
        }

        .nav-links a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            transition: all 0.3s ease;
        }

        .nav-links a:hover, .nav-links a.active {
            background: rgba(255, 255, 255, 0.1);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
        }

        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .status-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .status-success { border-color: rgba(76, 205, 196, 0.5); }
        .status-warning { border-color: rgba(255, 193, 7, 0.5); }
        .status-error { border-color: rgba(255, 107, 107, 0.5); }

        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            text-decoration: none;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
            margin: 0.5rem;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(78, 205, 196, 0.4);
        }

        .search-box {
            width: 100%;
            max-width: 600px;
            margin: 2rem auto;
            display: flex;
            gap: 1rem;
        }

        .search-input {
            flex: 1;
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 16px;
        }

        .search-input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }

        h1, h2, h3 {
            margin-bottom: 1rem;
            color: #4ecdc4;
        }

        .feature-list {
            list-style: none;
            padding: 0;
        }

        .feature-list li {
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .feature-list li:before {
            content: "✅ ";
            margin-right: 0.5rem;
        }

        .flask-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            z-index: 1000;
        }

        .flask-online {
            background: rgba(76, 205, 196, 0.2);
            color: #4ecdc4;
            border: 1px solid rgba(76, 205, 196, 0.3);
        }

        .flask-offline {
            background: rgba(255, 107, 107, 0.2);
            color: #ff6b6b;
            border: 1px solid rgba(255, 107, 107, 0.3);
        }
    </style>
</head>
<body>
    <!-- Flask Status Indicator -->
    <div class="flask-status <?= $flask_status ? 'flask-online' : 'flask-offline' ?>">
        🐍 Flask: <?= $flask_status ? 'Online' : 'Offline' ?>
    </div>

    <nav class="navbar">
        <div class="navbar-content">
            <div class="logo">🎬 Film Price Guide</div>
            <div class="nav-links">
                <a href="index.php?page=home" <?= $page === 'home' ? 'class="active"' : '' ?>>Home</a>
                <a href="index.php?page=search" <?= $page === 'search' ? 'class="active"' : '' ?>>Search</a>
                <a href="index.php?page=dashboard" <?= $page === 'dashboard' ? 'class="active"' : '' ?>>Dashboard</a>
                <?php if (isset($_SESSION['is_admin']) && $_SESSION['is_admin']): ?>
                    <a href="index.php?page=admin" <?= $page === 'admin' ? 'class="active"' : '' ?>>Admin</a>
                <?php endif; ?>
                <?php if (isset($_SESSION['user_id'])): ?>
                    <a href="logout.php">Logout (<?= htmlspecialchars($_SESSION['username'] ?? 'User') ?>)</a>
                <?php else: ?>
                    <a href="login.php">Login</a>
                <?php endif; ?>
            </div>
        </div>
    </nav>

    <div class="container">
        <?php
        switch($page) {
            case 'home':
                ?>
                <div class="card">
                    <h1>🎬 Welcome to Film Price Guide</h1>
                    <p>PHP Frontend with Flask Backend - Multi-API search engine for VHS, DVD, and Graded Movies</p>
                    
                    <div class="search-box">
                        <input type="text" class="search-input" placeholder="Search for movies, directors, or titles..." id="searchInput">
                        <button class="btn" onclick="performSearch()">🔍 Search</button>
                    </div>
                </div>

                <div class="status-grid">
                    <div class="status-card status-success">
                        <h3>✅ PHP Frontend</h3>
                        <p>Running PHP <?= phpversion() ?></p>
                        <p>Sessions: <?= isset($_SESSION) ? 'Working' : 'Failed' ?></p>
                    </div>
                    
                    <div class="status-card <?= $flask_status ? 'status-success' : 'status-error' ?>">
                        <h3><?= $flask_status ? '✅' : '❌' ?> Flask Backend</h3>
                        <p>API Status: <?= $flask_status ? 'Connected' : 'Disconnected' ?></p>
                        <p>URL: <?= $FLASK_URL ?></p>
                        <?php if (!$flask_status): ?>
                            <small>Check Flask app deployment</small>
                        <?php endif; ?>
                    </div>
                    
                    <div class="status-card status-warning">
                        <h3>🗄️ Database</h3>
                        <p>Configure MySQL connection</p>
                        <a href="config/database.php" class="btn" style="font-size: 12px; padding: 8px 16px;">Configure</a>
                    </div>
                    
                    <div class="status-card status-warning">
                        <h3>🔑 API Keys</h3>
                        <p>Configure eBay, OMDb, TMDb APIs</p>
                        <?php if (isset($_SESSION['is_admin']) && $_SESSION['is_admin']): ?>
                            <a href="index.php?page=admin" class="btn" style="font-size: 12px; padding: 8px 16px;">Setup APIs</a>
                        <?php else: ?>
                            <small>Admin login required</small>
                        <?php endif; ?>
                    </div>
                </div>

                <div class="card">
                    <h2>🔧 Architecture</h2>
                    <ul class="feature-list">
                        <li><strong>PHP Frontend:</strong> Handles authentication, routing, and web interface</li>
                        <li><strong>Flask Backend:</strong> Processes API calls, database operations, and business logic</li>
                        <li><strong>MySQL Database:</strong> Stores user data, movie information, and price history</li>
                        <li><strong>External APIs:</strong> eBay, OMDb, TMDb integration via Flask</li>
                    </ul>
                </div>
                <?php
                break;

            case 'search':
                if (file_exists('pages/search_content.php')) {
                    include 'pages/search_content.php';
                } else {
                    echo '<div class="card"><h1>Search page content not found</h1></div>';
                }
                break;

            case 'dashboard':
                if (file_exists('pages/dashboard_content.php')) {
                    include 'pages/dashboard_content.php';
                } else {
                    echo '<div class="card"><h1>Dashboard page content not found</h1></div>';
                }
                break;

            case 'admin':
                if (file_exists('pages/admin_content.php')) {
                    include 'pages/admin_content.php';
                } else {
                    echo '<div class="card"><h1>Admin page content not found</h1></div>';
                }
                break;

            default:
                include 'pages/home_content.php';
                break;
        }
        ?>
    </div>

    <script>
        function performSearch() {
            const query = document.getElementById('searchInput').value;
            if (query.trim()) {
                window.location.href = `index.php?page=search&q=${encodeURIComponent(query)}`;
            }
        }

        document.getElementById('searchInput')?.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });

        // Test Flask connection periodically
        setInterval(function() {
            fetch('api_proxy.php?action=health_check')
                .then(response => response.json())
                .then(data => {
                    const statusEl = document.querySelector('.flask-status');
                    if (data.success) {
                        statusEl.className = 'flask-status flask-online';
                        statusEl.innerHTML = '🐍 Flask: Online';
                    } else {
                        statusEl.className = 'flask-status flask-offline';
                        statusEl.innerHTML = '🐍 Flask: Offline';
                    }
                })
                .catch(() => {
                    const statusEl = document.querySelector('.flask-status');
                    statusEl.className = 'flask-status flask-offline';
                    statusEl.innerHTML = '🐍 Flask: Offline';
                });
        }, 30000); // Check every 30 seconds
    </script>
</body>
</html>