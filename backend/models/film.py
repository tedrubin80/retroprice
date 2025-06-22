# backend/models/film.py
"""
Film Database Model
Handles movie/film data storage and retrieval for Film Price Guide
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, DateTime, Decimal, Boolean, Index
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

# Import db from app (will be initialized in app.py)
from app import db

class Film(db.Model):
    """
    Film model for storing movie information
    Supports VHS, DVD, Blu-ray, and other formats
    """
    
    __tablename__ = 'films'
    
    # Primary key
    id = Column(Integer, primary_key=True)
    
    # Basic film information
    title = Column(String(255), nullable=False, index=True)
    format = Column(String(50), nullable=False, index=True)  # VHS, DVD, Blu-ray, etc.
    year = Column(Integer, index=True)
    
    # External IDs for API integration
    imdb_id = Column(String(20), index=True)  # IMDb ID (e.g., tt0107290)
    tmdb_id = Column(Integer, index=True)     # TMDb ID
    omdb_id = Column(String(20), index=True)  # OMDb ID
    
    # Film details
    director = Column(String(255))
    genre = Column(String(255))           # Comma-separated genres
    runtime_minutes = Column(Integer)
    mpaa_rating = Column(String(10))      # G, PG, PG-13, R, etc.
    plot = Column(Text)
    
    # Technical details specific to physical media
    aspect_ratio = Column(String(20))     # 16:9, 4:3, etc.
    audio_format = Column(String(100))    # Stereo, 5.1, DTS, etc.
    video_format = Column(String(50))     # NTSC, PAL, etc.
    region_code = Column(String(10))      # DVD/Blu-ray region
    
    # Collection information
    studio = Column(String(100))          # Production studio
    distributor = Column(String(100))     # Distribution company
    catalog_number = Column(String(50))   # Product catalog number
    barcode = Column(String(20))          # UPC/EAN barcode
    
    # Special editions and variants
    edition_type = Column(String(100))    # Special Edition, Director's Cut, etc.
    packaging_type = Column(String(100))  # Standard, Steelbook, Digipak, etc.
    is_sealed = Column(Boolean, default=False)
    is_graded = Column(Boolean, default=False)
    grade = Column(String(20))            # CGC, VGA grade if applicable
    
    # Pricing information (current market stats)
    current_avg_price = Column(Decimal(10, 2))
    current_min_price = Column(Decimal(10, 2))
    current_max_price = Column(Decimal(10, 2))
    last_sold_price = Column(Decimal(10, 2))
    last_sold_date = Column(DateTime)
    total_sales_count = Column(Integer, default=0)
    
    # Rarity and collectibility
    rarity_score = Column(Integer)        # 1-10 rarity scale
    popularity_score = Column(Integer)    # Based on search frequency
    is_rare = Column(Boolean, default=False)
    is_collectible = Column(Boolean, default=False)
    
    # Images and media
    poster_url = Column(String(500))      # Primary poster image
    thumbnail_url = Column(String(500))   # Thumbnail image
    images_json = Column(Text)            # JSON array of additional images
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_price_update = Column(DateTime)  # When prices were last updated
    
    # Status flags
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Data has been verified
    needs_update = Column(Boolean, default=False) # Flagged for data refresh
    
    # Relationships
    price_history = relationship('PriceHistory', back_populates='film', lazy='dynamic')
    watchlist_items = relationship('Watchlist', back_populates='film', lazy='dynamic')
    
    # Database indexes for performance
    __table_args__ = (
        Index('idx_film_title_format', 'title', 'format'),
        Index('idx_film_year_format', 'year', 'format'),
        Index('idx_film_updated', 'updated_at'),
        Index('idx_film_pricing', 'current_avg_price', 'format'),
        Index('idx_film_external_ids', 'imdb_id', 'tmdb_id'),
    )
    
    def __repr__(self):
        return f'<Film {self.title} ({self.format}, {self.year})>'
    
    @classmethod
    def find_or_create_by_title_format(cls, title: str, format: str, **kwargs) -> 'Film':
        """
        Find existing film by title and format, or create new one
        
        Args:
            title: Movie title
            format: Physical format (VHS, DVD, Blu-ray, etc.)
            **kwargs: Additional film attributes
        
        Returns:
            Film instance (existing or newly created)
        """
        try:
            # Clean and normalize title
            normalized_title = cls._normalize_title(title)
            normalized_format = format.strip().title()
            
            # Try to find existing film
            existing_film = cls.query.filter_by(
                title=normalized_title,
                format=normalized_format
            ).first()
            
            if existing_film:
                return existing_film
            
            # Create new film
            new_film = cls(
                title=normalized_title,
                format=normalized_format,
                **kwargs
            )
            
            db.session.add(new_film)
            db.session.commit()
            
            return new_film
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    @classmethod
    def _normalize_title(cls, title: str) -> str:
        """Normalize movie title for consistent storage"""
        if not title:
            return ""
        
        # Remove extra whitespace and common suffixes
        cleaned = title.strip()
        
        # Remove format indicators from title if present
        format_indicators = [' VHS', ' DVD', ' Blu-ray', ' BluRay', ' 4K', ' UHD']
        for indicator in format_indicators:
            if cleaned.upper().endswith(indicator.upper()):
                cleaned = cleaned[:-len(indicator)].strip()
        
        # Remove year from title if present at the end
        import re
        cleaned = re.sub(r'\s*\(\d{4}\)$', '', cleaned)
        
        return cleaned
    
    @classmethod
    def search_by_title(cls, title: str, format: Optional[str] = None) -> List['Film']:
        """
        Search films by title with optional format filter
        
        Args:
            title: Search term for movie title
            format: Optional format filter
        
        Returns:
            List of matching Film instances
        """
        query = cls.query.filter(cls.title.ilike(f'%{title}%'))
        
        if format:
            query = query.filter(cls.format == format)
        
        return query.order_by(cls.title, cls.year).all()
    
    @classmethod
    def get_by_external_id(cls, imdb_id: str = None, tmdb_id: int = None) -> Optional['Film']:
        """Find film by external API ID"""
        if imdb_id:
            return cls.query.filter_by(imdb_id=imdb_id).first()
        elif tmdb_id:
            return cls.query.filter_by(tmdb_id=tmdb_id).first()
        return None
    
    @classmethod
    def get_trending(cls, days: int = 7, limit: int = 20) -> List['Film']:
        """
        Get trending films based on recent activity
        
        Args:
            days: Number of days to look back
            limit: Maximum number of results
        
        Returns:
            List of trending Film instances
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Query films with recent price updates, ordered by popularity
        trending = cls.query.filter(
            cls.last_price_update >= cutoff_date,
            cls.is_active == True
        ).order_by(
            cls.popularity_score.desc(),
            cls.total_sales_count.desc()
        ).limit(limit).all()
        
        return trending
    
    @classmethod
    def get_by_format(cls, format: str, limit: int = 100) -> List['Film']:
        """Get films by format with optional limit"""
        return cls.query.filter_by(
            format=format,
            is_active=True
        ).order_by(cls.title).limit(limit).all()
    
    @classmethod
    def get_collectibles(cls, min_rarity: int = 7) -> List['Film']:
        """Get highly collectible films"""
        return cls.query.filter(
            cls.rarity_score >= min_rarity,
            cls.is_collectible == True,
            cls.is_active == True
        ).order_by(cls.rarity_score.desc()).all()
    
    def update_pricing_stats(self, price_data: List[Dict[str, Any]]) -> None:
        """
        Update current pricing statistics from recent sales
        
        Args:
            price_data: List of price dictionaries with 'value' keys
        """
        try:
            if not price_data:
                return
            
            prices = [float(item['value']) for item in price_data if item.get('value')]
            
            if prices:
                self.current_avg_price = sum(prices) / len(prices)
                self.current_min_price = min(prices)
                self.current_max_price = max(prices)
                self.total_sales_count += len(prices)
                self.last_price_update = datetime.utcnow()
                
                # Update rarity score based on price trends
                self._update_rarity_score()
                
                db.session.commit()
                
        except Exception as e:
            db.session.rollback()
            raise e
    
    def _update_rarity_score(self) -> None:
        """Update rarity score based on pricing and availability"""
        score = 1  # Base score
        
        # Price-based scoring
        if self.current_avg_price:
            if self.current_avg_price > 100:
                score += 3
            elif self.current_avg_price > 50:
                score += 2
            elif self.current_avg_price > 25:
                score += 1
        
        # Sales frequency scoring (inverse relationship)
        if self.total_sales_count:
            if self.total_sales_count < 5:
                score += 3
            elif self.total_sales_count < 20:
                score += 2
            elif self.total_sales_count < 50:
                score += 1
        
        # Format-based scoring
        if self.format == 'VHS':
            score += 2  # VHS is generally rarer
        elif self.format == 'LaserDisc':
            score += 3  # LaserDisc is very rare
        
        # Year-based scoring
        if self.year and self.year < 1990:
            score += 2
        elif self.year and self.year < 2000:
            score += 1
        
        self.rarity_score = min(score, 10)  # Cap at 10
        self.is_rare = score >= 7
        self.is_collectible = score >= 6
    
    def enrich_with_api_data(self, api_data: Dict[str, Any], source: str = 'omdb') -> None:
        """
        Enrich film data with information from external APIs
        
        Args:
            api_data: Data from OMDb or TMDb API
            source: API source ('omdb' or 'tmdb')
        """
        try:
            if source == 'omdb':
                self._enrich_from_omdb(api_data)
            elif source == 'tmdb':
                self._enrich_from_tmdb(api_data)
            
            self.is_verified = True
            self.needs_update = False
            self.updated_at = datetime.utcnow()
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise e
    
    def _enrich_from_omdb(self, omdb_data: Dict[str, Any]) -> None:
        """Enrich with OMDb API data"""
        if omdb_data.get('imdbID'):
            self.imdb_id = omdb_data['imdbID']
        if omdb_data.get('Director'):
            self.director = omdb_data['Director']
        if omdb_data.get('Genre'):
            self.genre = omdb_data['Genre']
        if omdb_data.get('Runtime'):
            # Extract minutes from "XX min" format
            runtime_str = omdb_data['Runtime'].replace(' min', '')
            try:
                self.runtime_minutes = int(runtime_str)
            except ValueError:
                pass
        if omdb_data.get('Rated'):
            self.mpaa_rating = omdb_data['Rated']
        if omdb_data.get('Plot'):
            self.plot = omdb_data['Plot']
        if omdb_data.get('Poster'):
            self.poster_url = omdb_data['Poster']
    
    def _enrich_from_tmdb(self, tmdb_data: Dict[str, Any]) -> None:
        """Enrich with TMDb API data"""
        if tmdb_data.get('id'):
            self.tmdb_id = tmdb_data['id']
        if tmdb_data.get('overview'):
            self.plot = tmdb_data['overview']
        if tmdb_data.get('runtime'):
            self.runtime_minutes = tmdb_data['runtime']
        if tmdb_data.get('poster_path'):
            self.poster_url = f"https://image.tmdb.org/t/p/w500{tmdb_data['poster_path']}"
        if tmdb_data.get('genres'):
            genres = [g['name'] for g in tmdb_data['genres']]
            self.genre = ', '.join(genres)
    
    def to_dict(self, include_relationships: bool = False) -> Dict[str, Any]:
        """Convert film to dictionary for API responses"""
        data = {
            'id': self.id,
            'title': self.title,
            'format': self.format,
            'year': self.year,
            'director': self.director,
            'genre': self.genre,
            'runtime_minutes': self.runtime_minutes,
            'mpaa_rating': self.mpaa_rating,
            'plot': self.plot,
            'studio': self.studio,
            'current_avg_price': float(self.current_avg_price) if self.current_avg_price else None,
            'current_min_price': float(self.current_min_price) if self.current_min_price else None,
            'current_max_price': float(self.current_max_price) if self.current_max_price else None,
            'rarity_score': self.rarity_score,
            'is_rare': self.is_rare,
            'is_collectible': self.is_collectible,
            'poster_url': self.poster_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relationships:
            data['recent_prices'] = [
                price.to_dict() for price in self.price_history.limit(10).all()
            ]
        
        return data
    
    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """Get overall film database statistics"""
        total_films = cls.query.count()
        
        format_counts = db.session.query(
            cls.format, 
            db.func.count(cls.id)
        ).group_by(cls.format).all()
        
        avg_price = db.session.query(
            db.func.avg(cls.current_avg_price)
        ).scalar()
        
        return {
            'total_films': total_films,
            'formats': dict(format_counts),
            'average_price': float(avg_price) if avg_price else 0,
            'collectible_count': cls.query.filter_by(is_collectible=True).count(),
            'rare_count': cls.query.filter_by(is_rare=True).count()
        }