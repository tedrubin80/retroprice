<?php
/*
FILE LOCATION: /pages/admin_content.php
SAVE AS: admin_content.php (in the pages/ directory)

Admin panel content - SECURE VERSION
*/
session_start();

// Check if user is logged in and is admin
if (!isset($_SESSION['user_id']) || !isset($_SESSION['is_admin']) || !$_SESSION['is_admin']) {
    // Not logged in or not admin - redirect to login
    header('Location: login.php?redirect=admin');
    exit;
}

// Admin is authenticated - show admin panel
?>
<div class="card">
    <h1>⚙️ System Administration</h1>
    <p>Manage technical configuration, API keys, and system monitoring</p>
</div>

<div class="status-grid">
    <div class="status-card <?= $flask_status ? 'status-success' : 'status-error' ?>">
        <h3><?= $flask_status ? '✅' : '❌' ?> Flask Backend</h3>
        <p>API Status: <?= $flask_status ? 'Connected' : 'Disconnected' ?></p>
        <p>URL: <?= $FLASK_URL ?></p>
        <?php if (!$flask_status): ?>
            <small>Check Flask app deployment</small>
        <?php endif; ?>
    </div>
    
    <div class="status-card status-warning">
        <h3>🗄️ Database Configuration</h3>
        <p>MySQL Connection Management</p>
        <p>User: <?= isset($_SESSION['db_user']) ? 'Connected' : 'Not configured' ?></p>
        <a href="config/database.php" class="btn" style="font-size: 12px; padding: 8px 16px;">Configure Database</a>
    </div>
    
    <div class="status-card status-success">
        <h3>🖥️ System Status</h3>
        <p>PHP Version: <?= phpversion() ?></p>
        <p>Sessions: <?= session_status() === PHP_SESSION_ACTIVE ? 'Active' : 'Inactive' ?></p>
        <p>Memory: <?= ini_get('memory_limit') ?></p>
    </div>
    
    <div class="status-card status-warning">
        <h3>👥 User Management</h3>
        <p>Registered Users: Loading...</p>
        <p>Active Sessions: <?= session_status() === PHP_SESSION_ACTIVE ? '1+' : '0' ?></p>
        <button class="btn" style="font-size: 12px; padding: 8px 16px;" onclick="showUserManagement()">Manage Users</button>
    </div>
</div>

<!-- Sensitive API Configuration Section -->
<div class="card">
    <h2>🔐 API Key Management</h2>
    <p style="color: #ffc107; margin-bottom: 20px;">⚠️ Sensitive Configuration - Admin Access Only</p>
    
    <div class="status-grid">
        <div class="status-card status-warning">
            <h3>🛒 eBay API</h3>
            <p>Status: Not configured</p>
            <button class="btn" style="font-size: 12px; padding: 8px 16px; margin: 8px 0;" onclick="showApiConfig('ebay')">Configure eBay</button>
        </div>
        
        <div class="status-card status-warning">
            <h3>🎬 Movie APIs</h3>
            <p>OMDb & TMDb: Not configured</p>
            <button class="btn" style="font-size: 12px; padding: 8px 16px; margin: 8px 0;" onclick="showApiConfig('movie')">Configure Movie APIs</button>
        </div>
        
        <div class="status-card status-warning">
            <h3>📧 Email Settings</h3>
            <p>SMTP: Not configured</p>
            <button class="btn" style="font-size: 12px; padding: 8px 16px; margin: 8px 0;" onclick="showApiConfig('email')">Configure Email</button>
        </div>
        
        <div class="status-card status-warning">
            <h3>🔄 Background Jobs</h3>
            <p>Price Updates: Manual</p>
            <button class="btn" style="font-size: 12px; padding: 8px 16px; margin: 8px 0;" onclick="showApiConfig('jobs')">Configure Jobs</button>
        </div>
    </div>
</div>
<div id="ebay-config" class="card" style="display: none;">
    <h2>🔑 eBay API Configuration</h2>
    <form id="ebayApiForm">
        <div style="margin-bottom: 1rem;">
            <label style="display: block; margin-bottom: 0.5rem; color: #4ecdc4;">App ID:</label>
            <input type="text" name="ebay_app_id" class="search-input" placeholder="Your eBay App ID" style="width: 100%; margin-bottom: 1rem;">
        </div>
        
        <div style="margin-bottom: 1rem;">
            <label style="display: block; margin-bottom: 0.5rem; color: #4ecdc4;">Cert ID:</label>
            <input type="text" name="ebay_cert_id" class="search-input" placeholder="Your eBay Cert ID" style="width: 100%; margin-bottom: 1rem;">
        </div>
        
        <div style="margin-bottom: 1rem;">
            <label style="display: block; margin-bottom: 0.5rem; color: #4ecdc4;">Dev ID:</label>
            <input type="text" name="ebay_dev_id" class="search-input" placeholder="Your eBay Dev ID" style="width: 100%; margin-bottom: 1rem;">
        </div>
        
        <button type="submit" class="btn">💾 Save eBay API Keys</button>
        <button type="button" class="btn" onclick="hideApiConfig()" style="background: rgba(255, 255, 255, 0.2);">Cancel</button>
    </form>
    
    <div style="margin-top: 2rem; padding: 1rem; background: rgba(255, 255, 255, 0.05); border-radius: 10px;">
        <h3>📋 How to Get eBay API Keys:</h3>
        <ol>
            <li>Go to <a href="https://developer.ebay.com/my/keys" target="_blank" style="color: #4ecdc4;">eBay Developer Program</a></li>
            <li>Create a developer account if you don't have one</li>
            <li>Create a new application</li>
            <li>Copy the App ID, Cert ID, and Dev ID</li>
            <li>Paste them in the form above</li>
        </ol>
    </div>
</div>

<div id="movie-config" class="card" style="display: none;">
    <h2>🎬 Movie API Configuration</h2>
    <form id="movieApiForm">
        <div style="margin-bottom: 1rem;">
            <label style="display: block; margin-bottom: 0.5rem; color: #4ecdc4;">OMDb API Key:</label>
            <input type="text" name="omdb_api_key" class="search-input" placeholder="Your OMDb API Key" style="width: 100%; margin-bottom: 1rem;">
            <small style="color: rgba(255, 255, 255, 0.7);">Get free key at: <a href="http://www.omdbapi.com/apikey.aspx" target="_blank" style="color: #4ecdc4;">omdbapi.com</a></small>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <label style="display: block; margin-bottom: 0.5rem; color: #4ecdc4;">TMDb API Key:</label>
            <input type="text" name="tmdb_api_key" class="search-input" placeholder="Your TMDb API Key" style="width: 100%; margin-bottom: 1rem;">
            <small style="color: rgba(255, 255, 255, 0.7);">Get free key at: <a href="https://www.themoviedb.org/settings/api" target="_blank" style="color: #4ecdc4;">themoviedb.org</a></small>
        </div>
        
        <button type="submit" class="btn">💾 Save Movie API Keys</button>
        <button type="button" class="btn" onclick="hideApiConfig()" style="background: rgba(255, 255, 255, 0.2);">Cancel</button>
    </form>
</div>

<div class="card">
    <h2>🔧 System Tools</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
        <a href="debug.php" class="btn" style="text-align: center;">🔍 System Debug</a>
        <a href="config/database.php" class="btn" style="text-align: center;">🗄️ Database Tools</a>
        <a href="config/session.php" class="btn" style="text-align: center;">🔧 Session Config</a>
        <a href="https://panel.dreamhost.com/" target="_blank" class="btn" style="text-align: center;">🏠 Dreamhost Panel</a>
        <button class="btn" onclick="testFlaskConnection()" style="text-align: center;">🐍 Test Flask API</button>
        <button class="btn" onclick="showSystemLogs()" style="text-align: center;">📝 View Logs</button>
    </div>
</div>

<!-- User Management Section -->
<div id="user-management" class="card" style="display: none;">
    <h2>👥 User Management</h2>
    <div style="margin-bottom: 2rem;">
        <button class="btn" onclick="loadUserList()">📋 View All Users</button>
        <button class="btn" onclick="showCreateUser()">➕ Create User</button>
        <button class="btn" onclick="exportUserData()">📊 Export Data</button>
    </div>
    <div id="user-list" style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
        <p>Click "View All Users" to load user list...</p>
    </div>
</div>

<!-- System Logs Section -->
<div id="system-logs" class="card" style="display: none;">
    <h2>📝 System Logs</h2>
    <div style="margin-bottom: 1rem;">
        <select id="logType" style="padding: 8px; border-radius: 5px; margin-right: 1rem;">
            <option value="php">PHP Errors</option>
            <option value="flask">Flask API</option>
            <option value="access">Access Logs</option>
            <option value="database">Database</option>
        </select>
        <button class="btn" onclick="loadLogs()" style="font-size: 14px; padding: 8px 16px;">Load Logs</button>
        <button class="btn" onclick="clearLogs()" style="font-size: 14px; padding: 8px 16px; background: rgba(255, 107, 107, 0.8);">Clear Logs</button>
    </div>
    <div id="log-content" style="background: rgba(0, 0, 0, 0.3); padding: 1rem; border-radius: 10px; font-family: monospace; font-size: 12px; max-height: 400px; overflow-y: auto;">
        Select log type and click "Load Logs"...
    </div>
</div>

<script>
function showApiConfig(type) {
    // Hide all config sections
    document.getElementById('ebay-config').style.display = 'none';
    document.getElementById('movie-config').style.display = 'none';
    document.getElementById('email-config').style.display = 'none';
    document.getElementById('jobs-config').style.display = 'none';
    
    // Show the requested config section
    if (document.getElementById(type + '-config')) {
        document.getElementById(type + '-config').style.display = 'block';
        document.getElementById(type + '-config').scrollIntoView({ behavior: 'smooth' });
    }
}

function hideApiConfig() {
    document.getElementById('ebay-config').style.display = 'none';
    document.getElementById('movie-config').style.display = 'none';
    document.getElementById('email-config').style.display = 'none';
    document.getElementById('jobs-config').style.display = 'none';
}

function showUserManagement() {
    document.getElementById('user-management').style.display = 'block';
    document.getElementById('user-management').scrollIntoView({ behavior: 'smooth' });
}

function showSystemLogs() {
    document.getElementById('system-logs').style.display = 'block';
    document.getElementById('system-logs').scrollIntoView({ behavior: 'smooth' });
}

function testFlaskConnection() {
    fetch('api_proxy.php?action=test_flask_connection')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Flask Connection Test:\n\nURL: ${data.data.flask_url}\nStatus: ${data.data.is_available ? 'Online' : 'Offline'}\nTime: ${data.data.timestamp}`);
            } else {
                alert('Flask connection test failed: ' + data.error);
            }
        })
        .catch(error => {
            alert('Error testing Flask connection: ' + error);
        });
}

function loadUserList() {
    document.getElementById('user-list').innerHTML = '<p>Loading users...</p>';
    
    // Mock user data - replace with actual API call
    setTimeout(() => {
        document.getElementById('user-list').innerHTML = `
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.2);">
                    <th style="text-align: left; padding: 8px;">Username</th>
                    <th style="text-align: left; padding: 8px;">Email</th>
                    <th style="text-align: left; padding: 8px;">Role</th>
                    <th style="text-align: left; padding: 8px;">Last Login</th>
                    <th style="text-align: left; padding: 8px;">Actions</th>
                </tr>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                    <td style="padding: 8px;"><?= htmlspecialchars($_SESSION['username'] ?? 'admin') ?></td>
                    <td style="padding: 8px;"><?= htmlspecialchars($_SESSION['email'] ?? 'admin@example.com') ?></td>
                    <td style="padding: 8px;">Admin</td>
                    <td style="padding: 8px;">Now</td>
                    <td style="padding: 8px;">
                        <button class="btn" style="font-size: 10px; padding: 4px 8px;">Edit</button>
                    </td>
                </tr>
            </table>
        `;
    }, 1000);
}

function loadLogs() {
    const logType = document.getElementById('logType').value;
    document.getElementById('log-content').innerHTML = `Loading ${logType} logs...`;
    
    // Mock log data - replace with actual log loading
    setTimeout(() => {
        const mockLogs = {
            php: `[${new Date().toISOString()}] PHP Notice: Session started successfully
[${new Date().toISOString()}] PHP Info: User login successful
[${new Date().toISOString()}] PHP Info: Admin panel accessed`,
            flask: `[${new Date().toISOString()}] Flask INFO: Health check endpoint accessed
[${new Date().toISOString()}] Flask INFO: Search API called
[${new Date().toISOString()}] Flask WARNING: eBay API rate limit approaching`,
            access: `${new Date().toISOString()} - GET /index.php - 200
${new Date().toISOString()} - POST /login.php - 302
${new Date().toISOString()} - GET /api_proxy.php - 200`,
            database: `[${new Date().toISOString()}] Database: Connection established
[${new Date().toISOString()}] Database: Query executed successfully
[${new Date().toISOString()}] Database: Connection closed`
        };
        
        document.getElementById('log-content').innerHTML = mockLogs[logType] || 'No logs available';
    }, 500);
}

function clearLogs() {
    if (confirm('Are you sure you want to clear the logs? This action cannot be undone.')) {
        document.getElementById('log-content').innerHTML = 'Logs cleared.';
    }
}

// Handle form submissions
document.getElementById('ebayApiForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const apiData = {
        ebay: {
            app_id: formData.get('ebay_app_id'),
            cert_id: formData.get('ebay_cert_id'),
            dev_id: formData.get('ebay_dev_id')
        }
    };
    
    // Send to Flask backend via proxy
    fetch('api_proxy.php?action=update_api_keys', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('eBay API keys saved successfully!');
            hideApiConfig();
        } else {
            alert('Failed to save eBay API keys: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        alert('Error saving API keys: ' + error);
    });
});

document.getElementById('movieApiForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const apiData = {
        omdb: {
            api_key: formData.get('omdb_api_key')
        },
        tmdb: {
            api_key: formData.get('tmdb_api_key')
        }
    };
    
    fetch('api_proxy.php?action=update_api_keys', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Movie API keys saved successfully!');
            hideApiConfig();
        } else {
            alert('Failed to save movie API keys: ' + (data.error || 'Unknown error'));
        }
    });
});
</script>