# 🎯 GoCollect API Integration - Updated for OpenAPI Spec

## 🚨 **Critical Rate Limit Information**

**GoCollect has VERY strict rate limits:**
- **Non-subscribers**: 50 requests/day for search & insights
- **Pro subscribers**: 100 requests/day for search & insights  
- **Sold Examples API**: 500 requests/hour
- **Staged Sales API**: 500 requests/hour

⚠️ **This means we must be extremely strategic about API calls!**

---

## 📊 **Updated Market Information (From OpenAPI Spec)**

### **Valid Markets (CAM values):**
- `comics` - Comic books and graphic novels
- `video-games` - Video games and gaming collectibles
- `concert-posters` - Concert and promotional posters
- `trading-cards` - Trading card games (Pokemon, Magic, etc.)
- `sports-cards` - Sports trading cards
- `magazines` - Collectible magazines

### **Movie-Relevant Markets:**
For film collectibles, focus on:
1. **`comics`** - Movie tie-in comics, adaptations
2. **`video-games`** - Movie-based video games
3. **`concert-posters`** - Movie promotional posters

### **Certification Companies by Market:**
```json
{
  "comics": ["cbcs", "cgc"],
  "concert-posters": ["cgc", "not-certified"],
  "magazines": ["cbcs", "cgc"],  
  "sports-cards": ["bgs", "cgc", "psa", "sgc"],
  "trading-cards": ["bgs", "cgc", "psa"],
  "video-games": ["cgc", "vga", "wata"]
}
```

---

## 💰 **Pricing Format (IMPORTANT!)**

**All prices in GoCollect API are returned in CENTS:**
- API returns: `"fmv": 5500`
- Actual value: $55.00 (divide by 100)
- Must convert: `price_dollars = api_price / 100`

---

## 🔧 **Updated Service Implementation**

### **Conservative Rate Limiting Strategy:**

```python
# Updated search strategy for rate limits
def search_movie_collectibles_conservative(self, movie_title: str) -> Dict[str, List[Dict]]:
    """
    Ultra-conservative search to respect 50-100 requests/day limit
    """
    
    # Only search the most relevant markets for movies
    priority_markets = ["comics", "video-games"]  # Skip concert-posters initially
    results = {}
    
    for market in priority_markets:
        try:
            # Sleep 2 seconds between calls (very conservative)
            time.sleep(2)
            
            # Limit results to save on insights API calls
            market_results = self.search_collectibles(movie_title, market, limit=10)
            
            if market_results:
                results[market] = market_results
                
                # Only get insights for TOP result to save API calls
                if len(market_results) > 0:
                    time.sleep(2)  # Rate limit pause
                    insights = self.get_item_insights(market_results[0]['item_id'])
                    if insights:
                        market_results[0]['pricing_insights'] = insights
            
        except Exception as e:
            logger.error(f"Error in conservative search: {str(e)}")
            results[market] = []
    
    return results
```

### **Caching Strategy (Essential!):**

```python
# Cache GoCollect responses aggressively
class GoCollectCache:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 86400  # 24 hours (since we have so few API calls)
    
    def get_cached_search(self, movie_title: str, market: str) -> Optional[List[Dict]]:
        cache_key = f"search_{movie_title}_{market}"
        cached = self.cache.get(cache_key)
        
        if cached and (time.time() - cached['timestamp']) < self.cache_ttl:
            return cached['data']
        return None
    
    def cache_search_results(self, movie_title: str, market: str, results: List[Dict]):
        cache_key = f"search_{movie_title}_{market}"
        self.cache[cache_key] = {
            'data': results,
            'timestamp': time.time()
        }
```

---

## 🎯 **Strategic API Usage for Film Price Guide**

### **Approach 1: On-Demand (Recommended)**
```python
# Only call GoCollect when user specifically requests collectible data
@app.route('/api/collectibles/<int:film_id>')
def get_collectible_context(film_id):
    # Only make API calls when user clicks "Show Collectibles"
    film = Film.get_by_id(film_id)
    
    # Check cache first
    cached = get_cached_collectible_data(film.title)
    if cached:
        return cached
    
    # Make conservative API calls
    collectible_data = gocollect_service.search_movie_collectibles_conservative(film.title)
    
    # Cache for 24 hours
    cache_collectible_data(film.title, collectible_data)
    
    return collectible_data
```

### **Approach 2: Batch Processing**
```python
# Process popular movies in batches during off-peak hours
def batch_process_collectibles():
    """
    Run daily batch job to update collectible data for top 20 most viewed films
    Uses entire daily API quota strategically
    """
    
    popular_films = Film.get_most_viewed(limit=20)  # Top 20 films
    api_calls_used = 0
    max_daily_calls = 45  # Conservative limit (save 5 for user requests)
    
    for film in popular_films:
        if api_calls_used >= max_daily_calls:
            break
            
        try:
            # 2 API calls per film (1 search + 1 insights)
            collectible_data = gocollect_service.search_collectibles(film.title, "comics", limit=5)
            api_calls_used += 1
            
            if collectible_data and len(collectible_data) > 0:
                time.sleep(3)  # Rate limiting
                insights = gocollect_service.get_item_insights(collectible_data[0]['item_id'])
                api_calls_used += 1
                
                # Store in database for later use
                store_collectible_insights(film.id, collectible_data, insights)
            
        except Exception as e:
            logger.error(f"Batch processing error for {film.title}: {str(e)}")
            continue
    
    logger.info(f"Batch processing complete. Used {api_calls_used} API calls.")
```

---

## 📱 **Frontend Integration Updates**

### **Progressive Enhancement Strategy:**

```javascript
// Only load collectible data when user shows interest
class CollectibleContext {
    constructor(filmId) {
        this.filmId = filmId;
        this.loaded = false;
    }
    
    async loadOnDemand() {
        if (this.loaded) return;
        
        try {
            // Show loading indicator
            this.showLoadingState();
            
            const response = await fetch(`/api/collectibles/${this.filmId}`);
            const data = await response.json();
            
            if (data.success) {
                this.displayCollectibleData(data);
                this.loaded = true;
            } else {
                this.showNoCollectiblesMessage();
            }
            
        } catch (error) {
            this.showErrorMessage();
        }
    }
    
    showLoadingState() {
        const placeholder = `
            <div class="collectible-loading">
                <div class="spinner"></div>
                <p>Checking collectible markets...</p>
            </div>
        `;
        document.getElementById('collectible-section').innerHTML = placeholder;
    }
    
    displayCollectibleData(data) {
        const hasCollectibles = Object.keys(data.collectible_data).length > 0;
        
        if (!hasCollectibles) {
            this.showNoCollectiblesMessage();
            return;
        }
        
        const collectibleHtml = `
            <div class="collectible-context">
                <h3>🎯 Related Collectibles Found</h3>
                ${this.formatCollectibleSummary(data)}
                <div class="collectible-markets">
                    ${this.formatMarketData(data.collectible_data)}
                </div>
            </div>
        `;
        
        document.getElementById('collectible-section').innerHTML = collectibleHtml;
    }
}

// Initialize on item detail page
document.addEventListener('DOMContentLoaded', () => {
    const filmId = getFilmIdFromURL();
    const collectibleContext = new CollectibleContext(filmId);
    
    // Add "Show Collectibles" button
    const showCollectiblesBtn = document.getElementById('show-collectibles-btn');
    showCollectiblesBtn?.addEventListener('click', () => {
        collectibleContext.loadOnDemand();
    });
});
```

---

## 🔄 **Database Schema Updates for Caching**

```sql
-- Cache table for GoCollect responses (essential due to rate limits)
CREATE TABLE gocollect_api_cache (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cache_key VARCHAR(255) NOT NULL UNIQUE,
    cache_data JSON NOT NULL,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    api_calls_used INT DEFAULT 1,
    
    INDEX idx_cache_key (cache_key),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB;

-- API usage tracking (critical for rate limit management)
CREATE TABLE gocollect_api_usage (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE NOT NULL,
    endpoint VARCHAR(100) NOT NULL,
    calls_made INT DEFAULT 1,
    daily_limit_hit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_date_endpoint (date, endpoint),
    INDEX idx_date (date)
) ENGINE=InnoDB;
```

---

## ⚙️ **Environment Variables Updates**

```bash
# GoCollect API Configuration (Updated)
GOCOLLECT_API_TOKEN=your_bearer_token_here
GOCOLLECT_SUBSCRIPTION_TYPE=basic  # or "pro"
GOCOLLECT_DAILY_LIMIT=50  # 50 for basic, 100 for pro
GOCOLLECT_CACHE_TTL=86400  # 24 hours (aggressive caching)

# Rate Limiting Strategy
GOCOLLECT_BATCH_PROCESSING=true
GOCOLLECT_BATCH_SCHEDULE=0 2 * * *  # Run at 2 AM daily
GOCOLLECT_MAX_BATCH_CALLS=45  # Save 5 calls for user requests

# Feature Flags
ENABLE_GOCOLLECT_INTEGRATION=true
GOCOLLECT_ON_DEMAND_ONLY=true  # Only load when user requests
```

---

## 📊 **Updated API Response Examples**

### **Search Response (Comics Market):**
```json
[
  {
    "item_id": 223124,
    "uuid": "468dff51-cbf6-415a-8236-b157e50ec6dd",
    "slug": "incredible-hulk-181",
    "name": "Incredible Hulk #181",
    "variant_of_item_id": null,
    "variant_description": null
  }
]
```

### **Insights Response (Prices in CENTS!):**
```json
{
  "item_id": 223124,
  "title": "Incredible Hulk",
  "issue_number": "181",
  "cam": "comics",
  "company": "cgc",
  "label": "universal",
  "grade": "9.8",
  "metrics": {
    "30": {
      "sold_count": 4,
      "low_price": 3600,     // $36.00
      "high_price": 4195,    // $41.95
      "average_price": 3936  // $39.36
    },
    "90": {
      "sold_count": 11,
      "low_price": 3600,     // $36.00
      "high_price": 4700,    // $47.00
      "average_price": 4149.91  // $41.50
    }
  },
  "fmv": 5500  // $55.00 (Fair Market Value)
}
```

---

## 🎯 **Recommended Implementation Plan**

### **Phase 1: Conservative Integration (Week 1)**
- Implement caching system
- Add on-demand collectible loading
- Set up rate limit tracking
- Test with 10-15 API calls/day

### **Phase 2: Strategic Enhancement (Week 2)**
- Implement batch processing for popular films
- Add user preference for collectible data
- Optimize cache hit rates
- Monitor API usage patterns

### **Phase 3: Full Integration (Week 3)**
- Add collectible context to search results
- Implement investment potential analysis
- Add collectible market trend indicators
- Fine-tune rate limiting strategy

---

## 🚨 **Critical Success Factors**

1. **Aggressive Caching**: Cache everything for 24+ hours
2. **User-Driven Loading**: Only call API when user requests collectible data
3. **Batch Processing**: Update popular films during off-peak hours
4. **Rate Limit Monitoring**: Track daily usage carefully
5. **Graceful Degradation**: App works perfectly without GoCollect data

This updated integration respects GoCollect's strict rate limits while still providing valuable collectible context to enhance your Film Price Guide! 🎬