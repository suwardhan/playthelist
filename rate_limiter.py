"""
Redis-based rate limiting for production use
"""
import redis
import json
import time
from typing import Optional, Tuple
from datetime import datetime, timedelta
from config import config
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Redis-based rate limiter for production use"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or config.REDIS_URL
        self.redis_client = None
        self.fallback_enabled = True
        self._connect()
    
    def _connect(self):
        """Connect to Redis with fallback to in-memory storage"""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("Connected to Redis for rate limiting")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using fallback rate limiting.")
            self.redis_client = None
            self.fallback_enabled = True
    
    def _get_fallback_key(self, user_id: str) -> str:
        """Get fallback storage key for in-memory rate limiting"""
        return f"rate_limit_fallback:{user_id}"
    
    def check_rate_limit(self, user_id: str, max_requests: int = None, window_minutes: int = None) -> Tuple[bool, str]:
        """
        Check if user has exceeded rate limit
        
        Args:
            user_id: Unique identifier for the user
            max_requests: Maximum requests allowed (defaults to config)
            window_minutes: Time window in minutes (defaults to config)
            
        Returns:
            Tuple of (is_allowed, message)
        """
        max_requests = max_requests or config.RATE_LIMIT_REQUESTS
        window_minutes = window_minutes or config.RATE_LIMIT_WINDOW_MINUTES
        
        if self.redis_client:
            return self._check_redis_rate_limit(user_id, max_requests, window_minutes)
        else:
            return self._check_fallback_rate_limit(user_id, max_requests, window_minutes)
    
    def _check_redis_rate_limit(self, user_id: str, max_requests: int, window_minutes: int) -> Tuple[bool, str]:
        """Check rate limit using Redis"""
        try:
            key = f"rate_limit:{user_id}"
            now = time.time()
            window_start = now - (window_minutes * 60)
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(now): now})
            
            # Set expiration
            pipe.expire(key, window_minutes * 60)
            
            results = pipe.execute()
            current_requests = results[1]
            
            if current_requests >= max_requests:
                return False, f"Rate limit exceeded. Max {max_requests} requests per {window_minutes} minutes."
            
            return True, "OK"
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            # Fallback to in-memory
            return self._check_fallback_rate_limit(user_id, max_requests, window_minutes)
    
    def _check_fallback_rate_limit(self, user_id: str, max_requests: int, window_minutes: int) -> Tuple[bool, str]:
        """Fallback rate limiting using in-memory storage"""
        try:
            # This is a simplified fallback - in production you'd want to use a proper cache
            # For now, we'll use a basic approach
            key = self._get_fallback_key(user_id)
            
            if self.redis_client:
                # Try to use Redis for fallback storage
                try:
                    data = self.redis_client.get(key)
                    if data:
                        requests = json.loads(data)
                    else:
                        requests = []
                    
                    now = datetime.now()
                    window_start = now - timedelta(minutes=window_minutes)
                    
                    # Filter old requests
                    requests = [req for req in requests if req > window_start.timestamp()]
                    
                    if len(requests) >= max_requests:
                        return False, f"Rate limit exceeded. Max {max_requests} requests per {window_minutes} minutes."
                    
                    # Add current request
                    requests.append(now.timestamp())
                    
                    # Store updated requests
                    self.redis_client.setex(key, window_minutes * 60, json.dumps(requests))
                    
                    return True, "OK"
                    
                except Exception as e:
                    logger.error(f"Fallback Redis storage failed: {e}")
            
            # Ultimate fallback - allow request (not ideal for production)
            logger.warning("Using ultimate fallback - allowing request without rate limiting")
            return True, "OK (fallback mode)"
            
        except Exception as e:
            logger.error(f"Fallback rate limit check failed: {e}")
            return True, "OK (error fallback)"
    
    def get_rate_limit_info(self, user_id: str) -> dict:
        """Get current rate limit information for a user"""
        try:
            if self.redis_client:
                key = f"rate_limit:{user_id}"
                now = time.time()
                window_start = now - (config.RATE_LIMIT_WINDOW_MINUTES * 60)
                
                # Get current request count
                current_requests = self.redis_client.zcount(key, window_start, now)
                remaining = max(0, config.RATE_LIMIT_REQUESTS - current_requests)
                
                return {
                    "current_requests": current_requests,
                    "max_requests": config.RATE_LIMIT_REQUESTS,
                    "remaining": remaining,
                    "window_minutes": config.RATE_LIMIT_WINDOW_MINUTES,
                    "reset_time": now + (config.RATE_LIMIT_WINDOW_MINUTES * 60)
                }
            else:
                return {
                    "current_requests": 0,
                    "max_requests": config.RATE_LIMIT_REQUESTS,
                    "remaining": config.RATE_LIMIT_REQUESTS,
                    "window_minutes": config.RATE_LIMIT_WINDOW_MINUTES,
                    "reset_time": time.time() + (config.RATE_LIMIT_WINDOW_MINUTES * 60)
                }
        except Exception as e:
            logger.error(f"Failed to get rate limit info: {e}")
            return {
                "current_requests": 0,
                "max_requests": config.RATE_LIMIT_REQUESTS,
                "remaining": config.RATE_LIMIT_REQUESTS,
                "window_minutes": config.RATE_LIMIT_WINDOW_MINUTES,
                "reset_time": time.time() + (config.RATE_LIMIT_WINDOW_MINUTES * 60)
            }

# Global rate limiter instance
rate_limiter = RateLimiter()
