<?php
/*
FILE LOCATION: /pages/dashboard_content.php
SAVE AS: dashboard_content.php (in the pages/ directory)

Dashboard content - SECURE VERSION
*/
session_start();

// Check if user is logged in
$is_logged_in = isset($_SESSION['user_id']);

// If not logged in, redirect to login page
if (!$is_logged_in) {
    header('Location: login.php?redirect=dashboard');
    exit;
}
?>

<?php if ($is_logged_in): ?>
    <!-- Logged in user dashboard -->
    <div class="card">
        <h1>📊 Welcome back, <?= htmlspecialchars($_SESSION['username'] ?? 'User') ?>!</h1>
        <p>Your personal Film Price Guide dashboard</p>
    </div>

    <div class="status-grid">
        <div class="status-card status-success">
            <h3>👤 Profile</h3>
            <p>Logged in as: <?= htmlspecialchars($_SESSION['username'] ?? 'User') ?></p>
            <p>Email: <?= htmlspecialchars($_SESSION['email'] ?? 'Not set') ?></p>
        </div>
        
        <div class="status-card status-warning">
            <h3>📝 Watchlist</h3>
            <p>0 items tracked</p>
            <small>Database connection required</small>
        </div>
        
        <div class="status-card status-warning">
            <h3>🔔 Price Alerts</h3>
            <p>0 active alerts</p>
            <small>Configure APIs for alerts</small>
        </div>
        
        <div class="status-card status-success">
            <h3>📈 Activity</h3>
            <p>Session active</p>
            <p>Last login: Today</p>
        </div>
    </div>

    <!-- Mock watchlist for demonstration -->
    <div class="card">
        <h2>📝 Your Watchlist</h2>
        
        <div style="background: rgba(255, 193, 7, 0.2); padding: 1rem; border-radius: 10px; border: 1px solid rgba(255, 193, 7, 0.5); margin-bottom: 2rem;">
            <h4 style="color: #ffc107;">⚠️ Demo Mode - Database Required</h4>
            <p>Watchlist functionality requires database connection. Once configured, you'll be able to:</p>
            <ul style="margin-left: 1rem; margin-top: 0.5rem;">
                <li>Add movies to your personal watchlist</li>
                <li>Set target prices for price alerts</li>
                <li>Track price history and trends</li>
                <li>Get notifications when prices drop</li>
            </ul>
        </div>
        
        <!-- Mock watchlist items -->
        <div style="display: grid; gap: 1rem;">
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px; display: flex; gap: 1rem; align-items: center; opacity: 0.6;">
                <div style="width: 60px; height: 90px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">🎬</div>
                <div style="flex: 1;">
                    <h4 style="color: #4ecdc4; margin-bottom: 0.5rem;">The Thing (1982) - VHS</h4>
                    <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 0.5rem;">Target Price: $25.00 | Current: $35.00</p>
                    <p style="color: #ff6b6b; font-size: 0.9rem;">📈 Price increased 15% this week</p>
                </div>
                <div>
                    <button class="btn" style="font-size: 12px; padding: 6px 12px; opacity: 0.7;" disabled>Edit Alert</button>
                </div>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px; display: flex; gap: 1rem; align-items: center; opacity: 0.6;">
                <div style="width: 60px; height: 90px; background: linear-gradient(45deg, #4ecdc4, #ff6b6b); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">📀</div>
                <div style="flex: 1;">
                    <h4 style="color: #4ecdc4; margin-bottom: 0.5rem;">Akira (1988) - DVD Collectors Edition</h4>
                    <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 0.5rem;">Target Price: $40.00 | Current: $38.00</p>
                    <p style="color: #4ecdc4; font-size: 0.9rem;">🎯 Close to target price!</p>
                </div>
                <div>
                    <button class="btn" style="font-size: 12px; padding: 6px 12px; opacity: 0.7;" disabled>Edit Alert</button>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 2rem;">
            <button class="btn" onclick="alert('Database connection required to add items to watchlist')" style="opacity: 0.7;">➕ Add Movie to Watchlist</button>
        </div>
    </div>

    <div class="card">
        <h2>📊 Recent Activity</h2>
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
            <p style="color: rgba(255, 255, 255, 0.8); text-align: center;">No recent activity</p>
            <p style="color: rgba(255, 255, 255, 0.6); text-align: center; font-size: 0.9rem;">Activity will appear here once APIs are configured</p>
        </div>
    </div>

<?php else: ?>
    <!-- Not logged in -->
    <div class="card">
        <h1>📊 Dashboard</h1>
        <p>Access your personal film price tracking dashboard</p>
        
        <div style="text-align: center; margin: 2rem 0;">
            <div style="background: rgba(255, 193, 7, 0.2); padding: 2rem; border-radius: 15px; border: 1px solid rgba(255, 193, 7, 0.5);">
                <h3 style="color: #ffc107; margin-bottom: 1rem;">🔒 Login Required</h3>
                <p style="margin-bottom: 2rem;">Please log in to access your dashboard and manage your movie watchlist</p>
                <a href="login.php" class="btn" style="margin-right: 1rem;">🔑 Login</a>
                <a href="login.php" class="btn" style="background: rgba(255, 255, 255, 0.2);">📝 Create Account</a>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>🎯 Dashboard Features</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
            
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                <h3 style="color: #4ecdc4;">📝 Personal Watchlist</h3>
                <p>Track your favorite movies and get notified when prices drop</p>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                <h3 style="color: #4ecdc4;">🔔 Price Alerts</h3>
                <p>Set target prices and receive alerts when movies hit your price point</p>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                <h3 style="color: #4ecdc4;">📊 Price History</h3>
                <p>View detailed price trends and market analysis for tracked movies</p>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
                <h3 style="color: #4ecdc4;">📈 Collection Value</h3>
                <p>Track the total value of your movie collection over time</p>
            </div>
            
        </div>
    </div>

    <div class="card">
        <h2>🚀 Getting Started</h2>
        <ol style="color: rgba(255, 255, 255, 0.9); line-height: 1.6;">
            <li><strong>Create an account</strong> or log in to get started</li>
            <li><strong>Search for movies</strong> using the search feature</li>
            <li><strong>Add movies</strong> to your personal watchlist</li>
            <li><strong>Set target prices</strong> for movies you want to buy</li>
            <li><strong>Get alerts</strong> when prices drop to your target</li>
        </ol>
    </div>
<?php endif; ?>