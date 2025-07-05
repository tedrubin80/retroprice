# ================================
# eBay API Backend Setup for VHS/DVD Price Tracker
# ================================

# requirements.txt
"""
flask==2.3.3
requests==2.31.0
python-dotenv==1.0.0
sqlite3
schedule==1.2.0
flask-cors==4.0.0
"""

# ================================
# 1. Environment Configuration
# ================================

# .env file
"""
EBAY_APP_ID=your_app_id_here
EBAY_CERT_ID=your_cert_id_here
EBAY_DEV_ID=your_dev_id_here
EBAY_USER_TOKEN=your_user_token_here
EBAY_SANDBOX=True
DATABASE_URL=sqlite:///retroprice.db
"""

# ================================
# 2. eBay API Client
# ================================

import requests
import json
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class EbayAPIClient:
    def __init__(self):
        self.app_id = os.getenv('EBAY_APP_ID')
        self.cert_id = os.getenv('EBAY_CERT_ID')
        self.dev_id = os.getenv('EBAY_DEV_ID')
        self.user_token = os.getenv('EBAY_USER_TOKEN')
        self.sandbox = os.getenv('EBAY_SANDBOX', 'True').lower() == 'true'
        
        # API URLs
        if self.sandbox:
            self.base_url = "https://api.sandbox.ebay.com"
        else:
            self.base_url = "https://api.ebay.com"
    
    def get_oauth_token(self):
        """Get OAuth 2.0 token for API access"""
        url = f"{self.base_url}/identity/v1/oauth2/token"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self._get_basic_auth()}'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception(f"OAuth failed: {response.text}")
    
    def search_completed_listings(self, keywords, category_id=None, limit=100):
        """Search for completed/sold listings"""
        token = self.get_oauth_token()
        
        url = f"{self.base_url}/buy/browse/v1/item_summary/search"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        params = {
            'q': keywords,
            'filter': 'buyingOptions:{AUCTION},buyingOptions:{FIXED_PRICE},conditionIds:{1000|1500|2000|2500|3000}',
            'sort': 'endTimeSoonest',
            'limit': min(limit, 200),  # eBay max is 200
            'offset': 0
        }
        
        # Add category filter for VHS/DVD
        if category_id:
            params['category_ids'] = category_id
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Search failed: {response.status_code} - {response.text}")
            return None
    
    def get_item_details(self, item_id):
        """Get detailed information about a specific item"""
        token = self.get_oauth_token()
        
        url = f"{self.base_url}/buy/browse/v1/item/{item_id}"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    
    def _get_basic_auth(self):
        """Generate basic auth string for OAuth"""
        import base64
        credentials = f"{self.app_id}:{self.cert_id}"
        return base64.b64encode(credentials.encode()).decode()

# ================================
# 3. Database Models
# ================================

import sqlite3
from contextlib import contextmanager

class Database:
    def __init__(self, db_path='retroprice.db'):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Create database tables"""
        with self.get_connection() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ebay_id TEXT UNIQUE,
                    title TEXT NOT NULL,
                    subtitle TEXT,
                    format TEXT, -- VHS, DVD, etc.
                    year INTEGER,
                    studio TEXT,
                    category_id INTEGER,
                    condition_id INTEGER,
                    image_url TEXT,
                    rarity_score INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_id INTEGER,
                    price DECIMAL(10,2),
                    shipping_cost DECIMAL(10,2),
                    condition_name TEXT,
                    sale_date TIMESTAMP,
                    platform TEXT DEFAULT 'eBay',
                    listing_type TEXT, -- auction, buy_it_now
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES items (id)
                );

                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item_id INTEGER,
                    target_price DECIMAL(10,2),
                    alert_enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (item_id) REFERENCES items (id)
                );

                CREATE TABLE IF NOT EXISTS price_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    watchlist_id INTEGER,
                    triggered_price DECIMAL(10,2),
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notified BOOLEAN DEFAULT 0,
                    FOREIGN KEY (watchlist_id) REFERENCES watchlist (id)
                );

                CREATE INDEX IF NOT EXISTS idx_items_title ON items(title);
                CREATE INDEX IF NOT EXISTS idx_price_history_item_date ON price_history(item_id, sale_date);
                CREATE INDEX IF NOT EXISTS idx_price_history_date ON price_history(sale_date);
            ''')
            conn.commit()
    
    def save_item(self, item_data):
        """Save or update an item"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO items 
                (ebay_id, title, subtitle, format, year, studio, category_id, condition_id, image_url, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                item_data.get('ebay_id'),
                item_data.get('title'),
                item_data.get('subtitle'),
                item_data.get('format'),
                item_data.get('year'),
                item_data.get('studio'),
                item_data.get('category_id'),
                item_data.get('condition_id'),
                item_data.get('image_url')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def save_price_data(self, item_id, price_data):
        """Save price history data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO price_history 
                (item_id, price, shipping_cost, condition_name, sale_date, platform, listing_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item_id,
                price_data.get('price'),
                price_data.get('shipping_cost', 0),
                price_data.get('condition'),
                price_data.get('sale_date'),
                price_data.get('platform', 'eBay'),
                price_data.get('listing_type')
            ))
            conn.commit()
    
    def search_items(self, query, format_filter=None, limit=50):
        """Search items in database"""
        with self.get_connection() as conn:
            where_clause = "WHERE title LIKE ?"
            params = [f"%{query}%"]
            
            if format_filter:
                where_clause += " AND format = ?"
                params.append(format_filter)
            
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT i.*, 
                       AVG(ph.price) as avg_price,
                       MAX(ph.sale_date) as last_sale,
                       COUNT(ph.id) as sale_count
                FROM items i
                LEFT JOIN price_history ph ON i.id = ph.item_id
                {where_clause}
                GROUP BY i.id
                ORDER BY last_sale DESC
                LIMIT ?
            ''', params + [limit])
            
            return [dict(row) for row in cursor.fetchall()]

# ================================
# 4. Data Processing Service
# ================================

class PriceDataProcessor:
    def __init__(self):
        self.ebay_client = EbayAPIClient()
        self.db = Database()
    
    def process_search_results(self, search_term, format_type=None):
        """Process eBay search results and save to database"""
        print(f"Searching eBay for: {search_term}")
        
        # Category IDs for VHS/DVD
        category_map = {
            'VHS': '309',  # VHS movies
            'DVD': '617'   # DVD movies
        }
        
        category_id = category_map.get(format_type.upper()) if format_type else None
        
        results = self.ebay_client.search_completed_listings(
            keywords=search_term,
            category_id=category_id,
            limit=100
        )
        
        if not results or 'itemSummaries' not in results:
            print("No results found")
            return []
        
        processed_items = []
        
        for item in results['itemSummaries']:
            try:
                # Extract item data
                item_data = self._extract_item_data(item)
                item_id = self.db.save_item(item_data)
                
                # Extract price data
                price_data = self._extract_price_data(item)
                if price_data:
                    self.db.save_price_data(item_id, price_data)
                
                processed_items.append({
                    'id': item_id,
                    'title': item_data['title'],
                    'current_price': price_data.get('price') if price_data else None,
                    'ebay_id': item_data['ebay_id']
                })
                
            except Exception as e:
                print(f"Error processing item {item.get('itemId')}: {e}")
                continue
        
        print(f"Processed {len(processed_items)} items")
        return processed_items
    
    def _extract_item_data(self, ebay_item):
        """Extract item information from eBay API response"""
        title = ebay_item.get('title', '')
        
        # Determine format from title
        format_type = 'Unknown'
        if 'VHS' in title.upper():
            format_type = 'VHS'
        elif 'DVD' in title.upper():
            format_type = 'DVD'
        elif 'BLU-RAY' in title.upper() or 'BLURAY' in title.upper():
            format_type = 'Blu-ray'
        
        # Extract year (simple regex)
        import re
        year_match = re.search(r'\((\d{4})\)|\b(19\d{2}|20\d{2})\b', title)
        year = int(year_match.group(1) or year_match.group(2)) if year_match else None
        
        return {
            'ebay_id': ebay_item.get('itemId'),
            'title': title,
            'subtitle': ebay_item.get('subtitle'),
            'format': format_type,
            'year': year,
            'studio': self._extract_studio(title),
            'category_id': ebay_item.get('categories', [{}])[0].get('categoryId'),
            'condition_id': ebay_item.get('condition', {}).get('conditionId'),
            'image_url': ebay_item.get('image', {}).get('imageUrl')
        }
    
    def _extract_price_data(self, ebay_item):
        """Extract price information from eBay item"""
        price_info = ebay_item.get('price')
        if not price_info:
            return None
        
        price = float(price_info.get('value', 0))
        
        shipping_info = ebay_item.get('shippingOptions', [{}])[0]
        shipping_cost = 0
        if shipping_info.get('shippingCost'):
            shipping_cost = float(shipping_info['shippingCost'].get('value', 0))
        
        return {
            'price': price,
            'shipping_cost': shipping_cost,
            'condition': ebay_item.get('condition', {}).get('conditionDisplayName'),
            'sale_date': ebay_item.get('itemEndDate', datetime.now().isoformat()),
            'listing_type': ebay_item.get('buyingOptions', [None])[0]
        }
    
    def _extract_studio(self, title):
        """Extract movie studio from title (basic implementation)"""
        studios = [
            'Universal', 'Disney', 'Warner', 'Paramount', 'Sony', 
            'MGM', 'Fox', '20th Century', 'Columbia', 'Lionsgate'
        ]
        
        title_upper = title.upper()
        for studio in studios:
            if studio.upper() in title_upper:
                return studio
        return None

# ================================
# 5. Flask API Endpoints
# ================================

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize services
processor = PriceDataProcessor()
db = Database()

@app.route('/api/search', methods=['GET'])
def search_items():
    """Search for items"""
    query = request.args.get('q', '')
    format_filter = request.args.get('format')
    source = request.args.get('source', 'database')  # 'database' or 'ebay'
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    try:
        if source == 'ebay':
            # Live eBay search
            results = processor.process_search_results(query, format_filter)
        else:
            # Database search
            results = db.search_items(query, format_filter)
        
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/item/<int:item_id>', methods=['GET'])
def get_item_details(item_id):
    """Get detailed item information with price history"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get item details
            cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
            item = cursor.fetchone()
            
            if not item:
                return jsonify({'error': 'Item not found'}), 404
            
            # Get price history
            cursor.execute('''
                SELECT price, shipping_cost, condition_name, sale_date, platform, listing_type
                FROM price_history 
                WHERE item_id = ? 
                ORDER BY sale_date DESC
                LIMIT 50
            ''', (item_id,))
            
            price_history = [dict(row) for row in cursor.fetchall()]
            
            # Calculate statistics
            prices = [p['price'] for p in price_history if p['price']]
            current_price = prices[0] if prices else 0
            avg_price = sum(prices) / len(prices) if prices else 0
            
            return jsonify({
                'item': dict(item),
                'price_history': price_history,
                'stats': {
                    'current_price': current_price,
                    'avg_price': round(avg_price, 2),
                    'min_price': min(prices) if prices else 0,
                    'max_price': max(prices) if prices else 0,
                    'total_sales': len(price_history)
                }
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    """Add item to watchlist"""
    data = request.json
    item_id = data.get('item_id')
    target_price = data.get('target_price')
    user_id = data.get('user_id', 1)  # Simplified user system
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO watchlist (user_id, item_id, target_price)
                VALUES (?, ?, ?)
            ''', (user_id, item_id, target_price))
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Added to watchlist'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/watchlist/<int:user_id>', methods=['GET'])
def get_watchlist(user_id):
    """Get user's watchlist"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT w.*, i.title, i.format, i.image_url,
                       AVG(ph.price) as current_price,
                       MAX(ph.sale_date) as last_sale
                FROM watchlist w
                JOIN items i ON w.item_id = i.id
                LEFT JOIN price_history ph ON i.id = ph.item_id
                WHERE w.user_id = ?
                GROUP BY w.id
                ORDER BY w.created_at DESC
            ''', (user_id,))
            
            watchlist = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'watchlist': watchlist,
                'count': len(watchlist)
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ================================
# 6. Background Job Scheduler
# ================================

import schedule
import threading
import time

def update_prices():
    """Background job to update prices for watched items"""
    print("Running price update job...")
    
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT i.title, i.format 
                FROM items i
                JOIN watchlist w ON i.id = w.item_id
                WHERE w.alert_enabled = 1
            ''')
            
            items_to_update = cursor.fetchall()
        
        for item in items_to_update:
            search_term = f"{item['title']} {item['format']}"
            processor.process_search_results(search_term, item['format'])
            time.sleep(2)  # Rate limiting
        
        print(f"Updated prices for {len(items_to_update)} items")
    
    except Exception as e:
        print(f"Error updating prices: {e}")

def run_scheduler():
    """Run the background scheduler"""
    schedule.every(1).hours.do(update_prices)
    schedule.every().day.at("09:00").do(update_prices)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start background scheduler
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# ================================
# 7. Usage Example
# ================================

"""
# Example usage:

# 1. Search for items from eBay
response = requests.get('http://localhost:5000/api/search?q=jurassic park&format=VHS&source=ebay')

# 2. Get item details
response = requests.get('http://localhost:5000/api/item/1')

# 3. Add to watchlist
response = requests.post('http://localhost:5000/api/watchlist', json={
    'item_id': 1,
    'target_price': 25.00,
    'user_id': 1
})

# 4. Get watchlist
response = requests.get('http://localhost:5000/api/watchlist/1')
"""