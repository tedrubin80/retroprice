<?php
/*
FILE LOCATION: /pages/search_content.php
SAVE AS: search_content.php (in the pages/ directory)

Search page content
*/

// Search page content
$search_query = $_GET['q'] ?? '';
?>
<div class="card">
    <h1>🔍 Search Films & Movies</h1>
    <p>Search across multiple databases and APIs for VHS, DVD, and movie prices</p>
    
    <form method="GET" action="index.php">
        <input type="hidden" name="page" value="search">
        <div class="search-box">
            <input type="text" name="q" class="search-input" placeholder="Search for movies, directors, titles..." value="<?= htmlspecialchars($search_query) ?>">
            <button type="submit" class="btn">🔍 Search</button>
        </div>
    </form>
</div>

<?php if ($search_query): ?>
<div class="card">
    <h2>📊 Search Results for "<?= htmlspecialchars($search_query) ?>"</h2>
    
    <div class="status-grid">
        <div class="status-card status-warning">
            <h3>🗄️ Database Search</h3>
            <p>Database not connected</p>
            <small>Connect database to search local film records</small>
        </div>
        
        <div class="status-card status-warning">
            <h3>🛒 eBay Search</h3>
            <p>eBay API not configured</p>
            <small>Configure eBay API to search current listings</small>
        </div>
        
        <div class="status-card status-warning">
            <h3>🎬 Movie Database</h3>
            <p>Movie APIs not configured</p>
            <small>Configure OMDb/TMDb for movie metadata</small>
        </div>
        
        <div class="status-card status-success">
            <h3>✅ Search Ready</h3>
            <p>System ready for API integration</p>
            <small>Configure APIs in admin panel</small>
        </div>
    </div>
    
    <!-- Mock search results for demonstration -->
    <div style="margin-top: 2rem;">
        <h3>🎯 Mock Results (Demo)</h3>
        <div style="display: grid; gap: 1rem;">
            
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px; display: flex; gap: 1rem; align-items: center;">
                <div style="width: 80px; height: 120px; background: linear-gradient(45deg, #ff6b6b, #4ecdc4); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 2rem;">🎬</div>
                <div style="flex: 1;">
                    <h4 style="color: #4ecdc4; margin-bottom: 0.5rem;">Sample Movie Title (1985)</h4>
                    <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 0.5rem;">VHS • Good Condition</p>
                    <p style="color: #ff6b6b; font-weight: bold;">$15.99 - $45.00</p>
                    <small style="color: rgba(255, 255, 255, 0.6);">Based on recent eBay sales</small>
                </div>
                <div>
                    <button class="btn" style="font-size: 14px; padding: 8px 16px;">View Details</button>
                </div>
            </div>
            
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px; display: flex; gap: 1rem; align-items: center;">
                <div style="width: 80px; height: 120px; background: linear-gradient(45deg, #4ecdc4, #ff6b6b); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 2rem;">📀</div>
                <div style="flex: 1;">
                    <h4 style="color: #4ecdc4; margin-bottom: 0.5rem;">Another Movie (1992)</h4>
                    <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 0.5rem;">DVD • New Sealed</p>
                    <p style="color: #ff6b6b; font-weight: bold;">$8.99 - $25.00</p>
                    <small style="color: rgba(255, 255, 255, 0.6);">Based on recent eBay sales</small>
                </div>
                <div>
                    <button class="btn" style="font-size: 14px; padding: 8px 16px;">View Details</button>
                </div>
            </div>
            
        </div>
        
        <div style="margin-top: 2rem; padding: 1rem; background: rgba(255, 193, 7, 0.2); border-radius: 10px; border: 1px solid rgba(255, 193, 7, 0.5);">
            <h4 style="color: #ffc107; margin-bottom: 0.5rem;">⚠️ Demo Mode</h4>
            <p>These are sample results. Real search functionality requires:</p>
            <ul style="margin-left: 1rem; margin-top: 0.5rem;">
                <li>Database connection for stored film data</li>
                <li>eBay API integration for live pricing</li>
                <li>Movie database APIs for film metadata</li>
            </ul>
            <a href="index.php?page=admin" class="btn" style="margin-top: 1rem; font-size: 14px; padding: 8px 16px;">Configure APIs</a>
        </div>
    </div>
</div>

<?php else: ?>
<div class="card">
    <h2>🎯 Search Features</h2>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
        
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
            <h3 style="color: #4ecdc4;">🛒 eBay Integration</h3>
            <p>Search current and completed eBay listings for real-time pricing data</p>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
            <h3 style="color: #4ecdc4;">🎬 Movie Metadata</h3>
            <p>Get detailed movie information from OMDb and TMDb databases</p>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
            <h3 style="color: #4ecdc4;">💾 Local Database</h3>
            <p>Store and search your own curated film price database</p>
        </div>
        
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 10px;">
            <h3 style="color: #4ecdc4;">📊 Price Tracking</h3>
            <p>Track price trends and get alerts for movies on your watchlist</p>
        </div>
        
    </div>
</div>

<div class="card">
    <h2>🔍 Search Tips</h2>
    <ul class="feature-list">
        <li>Try searching by movie title, director, or year</li>
        <li>Use specific formats like "VHS", "DVD", "Blu-ray"</li>
        <li>Include condition keywords: "sealed", "mint", "good"</li>
        <li>Search for collections: "Disney", "Criterion", "Studio Ghibli"</li>
        <li>Try partial matches: "Star Wars" will find all Star Wars movies</li>
    </ul>
</div>
<?php endif; ?>