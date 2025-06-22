# backend/utils/gocollect_rate_limiter.py
"""
Specialized rate limiter for GoCollect API's strict daily limits
Handles 50-100 requests per day limits with database tracking
"""

import os
from datetime import datetime, date
from typing import Optional, Dict, Any
import logging
from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, UniqueConstraint
from database import db

logger = logging.getLogger(__name__)

class GoCollectAPIUsage(db.Model):
    """Track GoCollect API usage per day"""
    __tablename__ = 'gocollect_api_usage'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    endpoint = Column(String(100), nullable=False)
    calls_made = Column(Integer, default=1)
    daily_limit_hit = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('date', 'endpoint', name='unique_date_endpoint'),
    )

class GoCollectRateLimiter:
    """
    Manages GoCollect API rate limits with database persistence
    """
    
    def __init__(self):
        # Get configuration from environment
        self.subscription_type = os.getenv('GOCOLLECT_SUBSCRIPTION_TYPE', 'basic')
        self.daily_limit = int(os.getenv('GOCOLLECT_DAILY_LIMIT', '50'))
        
        # Set limits based on subscription
        if self.subscription_type == 'pro':
            self.daily_limit = 100
        else:
            self.daily_limit = 50
        
        # Reserve some calls for user requests
        self.batch_limit = int(os.getenv('GOCOLLECT_MAX_BATCH_CALLS', '45'))
        self.user_reserve = self.daily_limit - self.batch_limit
        
        logger.info(f"GoCollect rate limiter initialized: {self.daily_limit} calls/day ({self.subscription_type})")
    
    def can_make_request(self, endpoint: str, is_batch_request: bool = False) -> bool:
        """
        Check if we can make a GoCollect API request today
        
        Args:
            endpoint: API endpoint (search, insights, etc.)
            is_batch_request: If this is part of batch processing
            
        Returns:
            True if request is allowed, False if daily limit would be exceeded
        """
        try:
            today = date.today()
            
            # Get or create usage record for today
            usage = GoCollectAPIUsage.query.filter_by(
                date=today,
                endpoint=endpoint
            ).first()
            
            if not usage:
                # First request of the day for this endpoint
                return True
            
            current_calls = usage.calls_made
            
            # Check daily limit
            if current_calls >= self.daily_limit:
                logger.warning(f"GoCollect daily limit reached for {endpoint}: {current_calls}/{self.daily_limit}")
                return False
            
            # For batch requests, check batch limit
            if is_batch_request and current_calls >= self.batch_limit:
                logger.warning(f"GoCollect batch limit reached for {endpoint}: {current_calls}/{self.batch_limit}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking GoCollect rate limit: {str(e)}")
            return False  # Fail safe - don't make request if we can't check limit
    
    def record_request(self, endpoint: str, success: bool = True) -> None:
        """
        Record that we made a GoCollect API request
        
        Args:
            endpoint: API endpoint that was called
            success: Whether the request was successful
        """
        try:
            today = date.today()
            
            # Get or create usage record
            usage = GoCollectAPIUsage.query.filter_by(
                date=today,
                endpoint=endpoint
            ).first()
            
            if usage:
                usage.calls_made += 1
                if usage.calls_made >= self.daily_limit:
                    usage.daily_limit_hit = True
            else:
                usage = GoCollectAPIUsage(
                    date=today,
                    endpoint=endpoint,
                    calls_made=1,
                    daily_limit_hit=(1 >= self.daily_limit)
                )
                db.session.add(usage)
            
            db.session.commit()
            
            logger.info(f"GoCollect API call recorded: {endpoint} ({usage.calls_made}/{self.daily_limit})")
            
            # Warn when approaching limit
            if usage.calls_made >= (self.daily_limit * 0.8):
                logger.warning(f"GoCollect API approaching daily limit: {usage.calls_made}/{self.daily_limit}")
                
        except Exception as e:
            logger.error(f"Error recording GoCollect API usage: {str(e)}")
            db.session.rollback()
    
    def get_daily_usage(self, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get GoCollect API usage for a specific date
        
        Args:
            target_date: Date to check (defaults to today)
            
        Returns:
            Dictionary with usage statistics
        """
        if target_date is None:
            target_date = date.today()
        
        try:
            usage_records = GoCollectAPIUsage.query.filter_by(date=target_date).all()
            
            total_calls = sum(record.calls_made for record in usage_records)
            
            endpoint_breakdown = {
                record.endpoint: record.calls_made 
                for record in usage_records
            }
            
            remaining_calls = max(0, self.daily_limit - total_calls)
            remaining_batch_calls = max(0, self.batch_limit - total_calls)
            
            return {
                'date': target_date.isoformat(),
                'total_calls': total_calls,
                'daily_limit': self.daily_limit,
                'remaining_calls': remaining_calls,
                'remaining_batch_calls': remaining_batch_calls,
                'limit_hit': total_calls >= self.daily_limit,
                'endpoint_breakdown': endpoint_breakdown,
                'subscription_type': self.subscription_type
            }
            
        except Exception as e:
            logger.error(f"Error getting GoCollect daily usage: {str(e)}")
            return {
                'date': target_date.isoformat(),
                'total_calls': 0,
                'daily_limit': self.daily_limit,
                'remaining_calls': self.daily_limit,
                'error': str(e)
            }
    
    def reset_daily_limits(self, target_date: Optional[date] = None) -> bool:
        """
        Reset daily limits (for testing or manual override)
        
        Args:
            target_date: Date to reset (defaults to today)
            
        Returns:
            True if reset successful
        """
        if target_date is None:
            target_date = date.today()
        
        try:
            GoCollectAPIUsage.query.filter_by(date=target_date).delete()
            db.session.commit()
            
            logger.info(f"GoCollect daily limits reset for {target_date}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting GoCollect daily limits: {str(e)}")
            db.session.rollback()
            return False
    
    def get_weekly_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary for the last 7 days"""
        from datetime import timedelta
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=6)  # Last 7 days
            
            usage_records = GoCollectAPIUsage.query.filter(
                GoCollectAPIUsage.date >= start_date,
                GoCollectAPIUsage.date <= end_date
            ).all()
            
            daily_totals = {}
            endpoint_totals = {}
            
            for record in usage_records:
                # Daily totals
                date_str = record.date.isoformat()
                if date_str not in daily_totals:
                    daily_totals[date_str] = 0
                daily_totals[date_str] += record.calls_made
                
                # Endpoint totals
                if record.endpoint not in endpoint_totals:
                    endpoint_totals[record.endpoint] = 0
                endpoint_totals[record.endpoint] += record.calls_made
            
            total_calls = sum(daily_totals.values())
            avg_daily_calls = total_calls / 7 if total_calls > 0 else 0
            
            return {
                'period': f"{start_date} to {end_date}",
                'total_calls': total_calls,
                'avg_daily_calls': round(avg_daily_calls, 1),
                'daily_breakdown': daily_totals,
                'endpoint_breakdown': endpoint_totals,
                'daily_limit': self.daily_limit,
                'efficiency_percent': round((avg_daily_calls / self.daily_limit) * 100, 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting weekly usage summary: {str(e)}")
            return {'error': str(e)}

# Utility functions for Flask endpoints

def check_gocollect_quota(endpoint: str, is_batch: bool = False) -> bool:
    """
    Decorator-friendly function to check GoCollect API quota
    """
    rate_limiter = GoCollectRateLimiter()
    return rate_limiter.can_make_request(endpoint, is_batch)

def record_gocollect_call(endpoint: str, success: bool = True) -> None:
    """
    Record a GoCollect API call
    """
    rate_limiter = GoCollectRateLimiter()
    rate_limiter.record_request(endpoint, success)

# Flask route for monitoring API usage
def create_gocollect_monitoring_routes(app):
    """
    Add monitoring routes to Flask app
    """
    
    @app.route('/api/admin/gocollect/usage')
    def gocollect_usage():
        """Get current GoCollect API usage"""
        rate_limiter = GoCollectRateLimiter()
        usage = rate_limiter.get_daily_usage()
        return jsonify(usage)
    
    @app.route('/api/admin/gocollect/usage/weekly')
    def gocollect_weekly_usage():
        """Get weekly GoCollect API usage summary"""
        rate_limiter = GoCollectRateLimiter()
        summary = rate_limiter.get_weekly_usage_summary()
        return jsonify(summary)
    
    @app.route('/api/admin/gocollect/reset', methods=['POST'])
    def reset_gocollect_usage():
        """Reset daily GoCollect API usage (admin only)"""
        rate_limiter = GoCollectRateLimiter()
        success = rate_limiter.reset_daily_limits()
        return jsonify({'success': success})

# Example usage in GoCollect service
class GoCollectServiceWithRateLimit:
    """
    Enhanced GoCollect service with rate limiting
    """
    
    def __init__(self):
        self.rate_limiter = GoCollectRateLimiter()
        # ... other initialization
    
    def search_collectibles_safe(self, query: str, cam: str = "comics", limit: int = 20) -> Optional[List[Dict]]:
        """
        Search with rate limiting protection
        """
        endpoint = "search"
        
        # Check if we can make the request
        if not self.rate_limiter.can_make_request(endpoint):
            logger.warning(f"GoCollect search blocked - daily limit reached")
            return None
        
        try:
            # Make the actual API call
            results = self.search_collectibles(query, cam, limit)
            
            # Record successful call
            self.rate_limiter.record_request(endpoint, success=True)
            
            return results
            
        except Exception as e:
            # Record failed call (still counts toward limit)
            self.rate_limiter.record_request(endpoint, success=False)
            raise e
    
    def get_item_insights_safe(self, item_id: int, grade: str = "9.8") -> Optional[Dict]:
        """
        Get insights with rate limiting protection
        """
        endpoint = "insights"
        
        if not self.rate_limiter.can_make_request(endpoint):
            logger.warning(f"GoCollect insights blocked - daily limit reached")
            return None
        
        try:
            insights = self.get_item_insights(item_id, grade)
            self.rate_limiter.record_request(endpoint, success=True)
            return insights
            
        except Exception as e:
            self.rate_limiter.record_request(endpoint, success=False)
            raise e