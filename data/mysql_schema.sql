-- ================================
-- Film Price Guide - MySQL Database Schema
-- ================================
-- This schema supports tracking movie prices across VHS, DVD, and Blu-ray formats
-- with user watchlists, price alerts, and comprehensive movie metadata

-- Create database
CREATE DATABASE IF NOT EXISTS film_price_guide CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE film_price_guide;

-- ================================
-- 1. FILMS TABLE
-- ================================
-- Core movie/film information with format and metadata
CREATE TABLE films (
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Basic Film Information
    title VARCHAR(255) NOT NULL,
    subtitle VARCHAR(255) NULL,
    format ENUM('VHS', 'DVD', 'Blu-ray', 'Digital', '4K UHD', 'Laserdisc') NOT NULL,
    release_year YEAR NULL,
    
    -- Movie Details
    studio VARCHAR(100) NULL,
    director VARCHAR(100) NULL,
    genre VARCHAR(50) NULL,
    runtime_minutes INT NULL,
    rating VARCHAR(10) NULL COMMENT 'MPAA rating: G, PG, PG-13, R, etc.',
    
    -- Technical Details
    aspect_ratio VARCHAR(20) NULL COMMENT 'e.g., 16:9, 4:3, 2.35:1',
    audio_format VARCHAR(50) NULL COMMENT 'e.g., Dolby Digital, DTS, Stereo',
    special_features TEXT NULL COMMENT 'Director commentary, deleted scenes, etc.',
    
    -- eBay Integration
    ebay_category_id VARCHAR(20) NULL COMMENT 'eBay category for searches',
    ebay_product_id VARCHAR(50) NULL COMMENT 'eBay ePID if available',
    
    -- Visual Assets
    image_url TEXT NULL,
    thumbnail_url TEXT NULL,
    
    -- Collectibility
    rarity_score TINYINT DEFAULT 1 COMMENT '1-10 scale, 10 being extremely rare',
    is_limited_edition BOOLEAN DEFAULT FALSE,
    edition_details VARCHAR(255) NULL COMMENT 'Special edition info',
    
    -- Condition and Variants
    sealed_available BOOLEAN DEFAULT FALSE COMMENT 'Are sealed copies available',
    variants_count INT DEFAULT 1 COMMENT 'Number of different releases',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_price_update TIMESTAMP NULL,
    
    -- Indexes
    INDEX idx_title (title),
    INDEX idx_format (format),
    INDEX idx_release_year (release_year),
    INDEX idx_studio (studio),
    INDEX idx_rarity_score (rarity_score),
    INDEX idx_updated_at (updated_at),
    
    -- Full-text search
    FULLTEXT(title, subtitle, director)
) ENGINE=InnoDB;

-- ================================
-- 2. PRICE HISTORY TABLE
-- ================================
-- Tracks all sold prices from eBay, Heritage Auctions, etc.
CREATE TABLE price_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Film Reference
    film_id INT NOT NULL,
    
    -- Price Information
    price DECIMAL(10,2) NOT NULL,
    currency CHAR(3) DEFAULT 'USD',
    shipping_cost DECIMAL(8,2) DEFAULT 0.00,
    total_cost DECIMAL(10,2) GENERATED ALWAYS AS (price + shipping_cost) STORED,
    
    -- Item Condition
    condition_name VARCHAR(50) NULL COMMENT 'New, Very Good, Good, Acceptable, etc.',
    condition_id VARCHAR(10) NULL COMMENT 'eBay condition ID',
    condition_description TEXT NULL COMMENT 'Detailed condition notes',
    
    -- Sale Details
    sale_date DATETIME NOT NULL,
    platform ENUM('eBay', 'Heritage', 'Mercari', 'Facebook', 'Other') DEFAULT 'eBay',
    listing_type ENUM('Auction', 'FixedPrice', 'BestOffer', 'StoreInventory') NULL,
    
    -- Seller Information
    seller_rating INT NULL COMMENT 'Seller feedback score',
    seller_location VARCHAR(100) NULL,
    
    -- Listing Details
    listing_title VARCHAR(500) NULL,
    external_listing_id VARCHAR(100) NULL COMMENT 'eBay item ID, etc.',
    external_listing_url TEXT NULL,
    
    -- Quantity and Variations
    total_sold_quantity INT DEFAULT 1,
    is_auction BOOLEAN DEFAULT FALSE,
    starting_price DECIMAL(10,2) NULL COMMENT 'For auctions',
    bid_count INT NULL COMMENT 'Number of bids for auctions',
    
    -- Additional Metadata
    has_original_packaging BOOLEAN NULL,
    includes_extras BOOLEAN NULL COMMENT 'Manuals, inserts, etc.',
    
    -- Tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (film_id) REFERENCES films(id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_film_id (film_id),
    INDEX idx_sale_date (sale_date),
    INDEX idx_platform (platform),
    INDEX idx_price (price),
    INDEX idx_film_date (film_id, sale_date),
    INDEX idx_condition (condition_name),
    INDEX idx_platform_date (platform, sale_date)
) ENGINE=InnoDB;

-- ================================
-- 3. USERS TABLE
-- ================================
-- User accounts for personalized tracking
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Authentication
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Personal Information
    first_name VARCHAR(50) NULL,
    last_name VARCHAR(50) NULL,
    display_name VARCHAR(100) NULL,
    
    -- User Preferences
    preferred_currency CHAR(3) DEFAULT 'USD',
    timezone VARCHAR(50) DEFAULT 'UTC',
    email_notifications BOOLEAN DEFAULT TRUE,
    price_alert_frequency ENUM('Immediate', 'Daily', 'Weekly') DEFAULT 'Immediate',
    
    -- Account Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(255) NULL,
    
    -- Profile
    avatar_url TEXT NULL,
    bio TEXT NULL,
    location VARCHAR(100) NULL,
    
    -- Collecting Preferences
    preferred_formats SET('VHS', 'DVD', 'Blu-ray', 'Digital', '4K UHD', 'Laserdisc') NULL,
    collecting_focus VARCHAR(255) NULL COMMENT 'Horror, Disney, Criterion, etc.',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    email_verified_at TIMESTAMP NULL,
    
    -- Indexes
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_active (is_active),
    INDEX idx_last_login (last_login)
) ENGINE=InnoDB;

-- ================================
-- 4. WATCHLIST TABLE
-- ================================
-- User's tracked movies with price targets
CREATE TABLE watchlist (
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- References
    user_id INT NOT NULL,
    film_id INT NOT NULL,
    
    -- Price Targeting
    target_price DECIMAL(10,2) NULL COMMENT 'Desired price point',
    max_price DECIMAL(10,2) NULL COMMENT 'Maximum willing to pay',
    
    -- Preferences
    preferred_condition ENUM('Any', 'New', 'Very Good', 'Good', 'Acceptable') DEFAULT 'Any',
    alert_enabled BOOLEAN DEFAULT TRUE,
    notes TEXT NULL COMMENT 'Personal notes about this item',
    
    -- Priority
    priority TINYINT DEFAULT 5 COMMENT '1-10 scale, 10 being highest priority',
    
    -- Status
    status ENUM('Active', 'Purchased', 'Paused', 'Removed') DEFAULT 'Active',
    purchased_date DATE NULL,
    purchased_price DECIMAL(10,2) NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (film_id) REFERENCES films(id) ON DELETE CASCADE,
    
    -- Constraints
    UNIQUE KEY unique_user_film (user_id, film_id),
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_film_id (film_id),
    INDEX idx_target_price (target_price),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB;

-- ================================
-- 5. PRICE ALERTS TABLE
-- ================================
-- Price alert notifications and history
CREATE TABLE price_alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- References
    watchlist_id INT NOT NULL,
    price_history_id INT NULL COMMENT 'The sale that triggered this alert',
    
    -- Alert Details
    alert_type ENUM('Price Drop', 'Target Met', 'New Listing', 'Price Increase') NOT NULL,
    triggered_price DECIMAL(10,2) NOT NULL,
    target_price DECIMAL(10,2) NULL COMMENT 'User\'s target that was met',
    
    -- Notification Status
    notified BOOLEAN DEFAULT FALSE,
    notification_method ENUM('Email', 'SMS', 'Push', 'In-App') DEFAULT 'Email',
    notification_sent_at TIMESTAMP NULL,
    notification_opened BOOLEAN DEFAULT FALSE,
    notification_clicked BOOLEAN DEFAULT FALSE,
    
    -- Alert Content
    alert_title VARCHAR(255) NULL,
    alert_message TEXT NULL,
    
    -- Timestamps
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL COMMENT 'When this alert becomes stale',
    
    -- Foreign Keys
    FOREIGN KEY (watchlist_id) REFERENCES watchlist(id) ON DELETE CASCADE,
    FOREIGN KEY (price_history_id) REFERENCES price_history(id) ON DELETE SET NULL,
    
    -- Indexes
    INDEX idx_watchlist_id (watchlist_id),
    INDEX idx_triggered_at (triggered_at),
    INDEX idx_notified (notified),
    INDEX idx_alert_type (alert_type),
    INDEX idx_notification_status (notified, notification_sent_at)
) ENGINE=InnoDB;

-- ================================
-- 6. FILM CATEGORIES TABLE
-- ================================
-- Hierarchical categories for films (Genre, Studio, Collection, etc.)
CREATE TABLE film_categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Category Details
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL,
    
    -- Hierarchy
    parent_id INT NULL,
    category_type ENUM('Genre', 'Studio', 'Collection', 'Series', 'Director', 'Era') NOT NULL,
    
    -- Display
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (parent_id) REFERENCES film_categories(id) ON DELETE SET NULL,
    
    -- Indexes
    INDEX idx_parent_id (parent_id),
    INDEX idx_category_type (category_type),
    INDEX idx_slug (slug),
    INDEX idx_active (is_active)
) ENGINE=InnoDB;

-- ================================
-- 7. FILM_CATEGORY_MAPPINGS TABLE
-- ================================
-- Many-to-many relationship between films and categories
CREATE TABLE film_category_mappings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    film_id INT NOT NULL,
    category_id INT NOT NULL,
    
    -- Relationship strength (for algorithms)
    relevance_score DECIMAL(3,2) DEFAULT 1.00 COMMENT '0.00-1.00 relevance',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (film_id) REFERENCES films(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES film_categories(id) ON DELETE CASCADE,
    
    -- Constraints
    UNIQUE KEY unique_film_category (film_id, category_id),
    
    -- Indexes
    INDEX idx_film_id (film_id),
    INDEX idx_category_id (category_id)
) ENGINE=InnoDB;

-- ================================
-- 8. SEARCH_QUERIES TABLE
-- ================================
-- Track user searches for analytics and improvement
CREATE TABLE search_queries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Query Details
    user_id INT NULL COMMENT 'NULL for anonymous searches',
    query_text VARCHAR(500) NOT NULL,
    filters_applied JSON NULL COMMENT 'Format, price range, etc.',
    
    -- Results
    results_count INT DEFAULT 0,
    clicked_film_id INT NULL COMMENT 'Which result was clicked',
    
    -- Context
    search_source ENUM('Homepage', 'Navigation', 'API', 'Autocomplete') DEFAULT 'Homepage',
    user_agent TEXT NULL,
    ip_address VARCHAR(45) NULL,
    
    -- Timestamps
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (clicked_film_id) REFERENCES films(id) ON DELETE SET NULL,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_query_text (query_text(100)),
    INDEX idx_searched_at (searched_at),
    INDEX idx_results_count (results_count)
) ENGINE=InnoDB;

-- ================================
-- 9. MARKET_INSIGHTS TABLE
-- ================================
-- Aggregate market data and trends
CREATE TABLE market_insights (
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Time Period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    period_type ENUM('Daily', 'Weekly', 'Monthly', 'Quarterly') NOT NULL,
    
    -- Scope
    film_id INT NULL COMMENT 'NULL for overall market',
    category_id INT NULL COMMENT 'Category-specific insights',
    format ENUM('VHS', 'DVD', 'Blu-ray', 'All') DEFAULT 'All',
    
    -- Metrics
    total_sales INT DEFAULT 0,
    avg_price DECIMAL(10,2) DEFAULT 0.00,
    median_price DECIMAL(10,2) DEFAULT 0.00,
    min_price DECIMAL(10,2) DEFAULT 0.00,
    max_price DECIMAL(10,2) DEFAULT 0.00,
    
    -- Trends
    price_trend ENUM('Increasing', 'Decreasing', 'Stable', 'Volatile') DEFAULT 'Stable',
    trend_percentage DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Percentage change',
    
    -- Volume
    volume_trend ENUM('Increasing', 'Decreasing', 'Stable') DEFAULT 'Stable',
    
    -- Metadata
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (film_id) REFERENCES films(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES film_categories(id) ON DELETE CASCADE,
    
    -- Constraints
    UNIQUE KEY unique_period_scope (period_start, period_end, film_id, category_id, format),
    
    -- Indexes
    INDEX idx_period (period_start, period_end),
    INDEX idx_film_id (film_id),
    INDEX idx_category_id (category_id),
    INDEX idx_format (format),
    INDEX idx_calculated_at (calculated_at)
) ENGINE=InnoDB;

-- ================================
-- SAMPLE DATA INSERTS
-- ================================

-- Insert sample film categories
INSERT INTO film_categories (name, slug, category_type, description) VALUES
('Action', 'action', 'Genre', 'Action and adventure films'),
('Horror', 'horror', 'Genre', 'Horror and thriller movies'),
('Disney', 'disney', 'Studio', 'Walt Disney Studios releases'),
('Universal Studios', 'universal', 'Studio', 'Universal Pictures releases'),
('Criterion Collection', 'criterion', 'Collection', 'Criterion Collection releases'),
('1980s', '1980s', 'Era', 'Films from the 1980s'),
('1990s', '1990s', 'Era', 'Films from the 1990s');

-- Insert sample films
INSERT INTO films (title, format, release_year, studio, director, genre, runtime_minutes, rating, ebay_category_id, rarity_score) VALUES
('Jurassic Park', 'VHS', 1993, 'Universal Studios', 'Steven Spielberg', 'Action', 127, 'PG-13', '309', 3),
('Jurassic Park', 'DVD', 1993, 'Universal Studios', 'Steven Spielberg', 'Action', 127, 'PG-13', '617', 2),
('Star Wars: A New Hope', 'VHS', 1977, '20th Century Fox', 'George Lucas', 'Sci-Fi', 121, 'PG', '309', 8),
('The Lion King', 'VHS', 1994, 'Disney', 'Roger Allers', 'Animation', 88, 'G', '309', 4),
('Blade Runner: The Final Cut', 'Blu-ray', 1982, 'Warner Bros', 'Ridley Scott', 'Sci-Fi', 117, 'R', '2649', 6);

-- ================================
-- USEFUL VIEWS
-- ================================

-- Current market prices view
CREATE VIEW current_market_prices AS
SELECT 
    f.id,
    f.title,
    f.format,
    f.release_year,
    f.studio,
    COUNT(ph.id) as total_sales,
    AVG(ph.price) as avg_price,
    MIN(ph.price) as min_price,
    MAX(ph.price) as max_price,
    MAX(ph.sale_date) as last_sale_date
FROM films f
LEFT JOIN price_history ph ON f.id = ph.film_id
WHERE ph.sale_date >= DATE_SUB(NOW(), INTERVAL 90 DAY)
GROUP BY f.id, f.title, f.format, f.release_year, f.studio;

-- User watchlist with current prices
CREATE VIEW user_watchlist_with_prices AS
SELECT 
    w.*,
    f.title,
    f.format,
    f.release_year,
    f.studio,
    f.rarity_score,
    cmp.avg_price as current_avg_price,
    cmp.min_price as current_min_price,
    cmp.last_sale_date,
    CASE 
        WHEN w.target_price IS NOT NULL AND cmp.min_price <= w.target_price THEN 'Target Met'
        WHEN cmp.avg_price IS NULL THEN 'No Recent Sales'
        ELSE 'Tracking'
    END as alert_status
FROM watchlist w
JOIN films f ON w.film_id = f.id
LEFT JOIN current_market_prices cmp ON f.id = cmp.id
WHERE w.status = 'Active';

-- ================================
-- INDEXES FOR PERFORMANCE
-- ================================

-- Composite indexes for common queries
CREATE INDEX idx_price_history_film_date_price ON price_history(film_id, sale_date DESC, price);
CREATE INDEX idx_films_format_year ON films(format, release_year);
CREATE INDEX idx_watchlist_user_status_priority ON watchlist(user_id, status, priority DESC);

-- ================================
-- STORED PROCEDURES
-- ================================

DELIMITER $$

-- Calculate rarity score based on sales volume and price trends
CREATE PROCEDURE CalculateRarityScore(IN film_id_param INT)
BEGIN
    DECLARE sales_count INT DEFAULT 0;
    DECLARE avg_price DECIMAL(10,2) DEFAULT 0;
    DECLARE new_rarity_score TINYINT DEFAULT 1;
    
    -- Count sales in last 6 months
    SELECT COUNT(*), AVG(price) INTO sales_count, avg_price
    FROM price_history 
    WHERE film_id = film_id_param 
    AND sale_date >= DATE_SUB(NOW(), INTERVAL 6 MONTH);
    
    -- Calculate rarity score
    SET new_rarity_score = CASE
        WHEN sales_count = 0 THEN 10  -- No sales = extremely rare
        WHEN sales_count <= 2 THEN 8  -- Very few sales = very rare  
        WHEN sales_count <= 5 THEN 6  -- Few sales = rare
        WHEN sales_count <= 10 THEN 4 -- Some sales = uncommon
        WHEN sales_count <= 25 THEN 3 -- Regular sales = somewhat common
        ELSE 1                        -- Many sales = common
    END;
    
    -- Adjust for high prices (expensive items tend to be rarer)
    IF avg_price > 100 THEN
        SET new_rarity_score = LEAST(10, new_rarity_score + 2);
    ELSEIF avg_price > 50 THEN
        SET new_rarity_score = LEAST(10, new_rarity_score + 1);
    END IF;
    
    -- Update the film record
    UPDATE films 
    SET rarity_score = new_rarity_score,
        last_price_update = NOW()
    WHERE id = film_id_param;
    
END$$

DELIMITER ;

-- ================================
-- TRIGGERS
-- ================================

DELIMITER $$

-- Update film's last_price_update when new price history is added
CREATE TRIGGER update_film_price_timestamp
    AFTER INSERT ON price_history
    FOR EACH ROW
BEGIN
    UPDATE films 
    SET last_price_update = NOW() 
    WHERE id = NEW.film_id;
END$$

-- Auto-calculate total_cost when price or shipping changes
CREATE TRIGGER calculate_total_cost
    BEFORE INSERT ON price_history
    FOR EACH ROW
BEGIN
    SET NEW.total_cost = NEW.price + NEW.shipping_cost;
END$$

DELIMITER ;

-- ================================
-- GRANTS AND PERMISSIONS
-- ================================
-- Note: Adjust these based on your application's needs

-- Create application user (run with admin privileges)
-- CREATE USER 'film_price_app'@'localhost' IDENTIFIED BY 'secure_password_here';
-- GRANT SELECT, INSERT, UPDATE ON film_price_guide.* TO 'film_price_app'@'localhost';
-- GRANT DELETE ON film_price_guide.search_queries TO 'film_price_app'@'localhost';
-- FLUSH PRIVILEGES;