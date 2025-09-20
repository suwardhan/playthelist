"""
Health check endpoints and monitoring for PlayTheList
"""
import time
import logging
from typing import Dict, Any
from datetime import datetime
import requests
from config import config
from rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

class HealthChecker:
    """Health check system for monitoring application status"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.checks = {}
    
    def check_redis_connection(self) -> Dict[str, Any]:
        """Check Redis connection status"""
        try:
            if rate_limiter.redis_client:
                rate_limiter.redis_client.ping()
                return {
                    "status": "healthy",
                    "message": "Redis connection successful",
                    "response_time_ms": 0
                }
            else:
                return {
                    "status": "degraded",
                    "message": "Redis not available, using fallback",
                    "response_time_ms": 0
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Redis connection failed: {str(e)}",
                "response_time_ms": 0
            }
    
    def check_spotify_api(self) -> Dict[str, Any]:
        """Check Spotify API connectivity"""
        try:
            start_time = time.time()
            # Simple connectivity check
            response = requests.get("https://api.spotify.com/v1/search?q=test&type=track&limit=1", 
                                  timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code in [200, 401]:  # 401 is expected without auth
                return {
                    "status": "healthy",
                    "message": "Spotify API accessible",
                    "response_time_ms": round(response_time, 2)
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Spotify API returned status {response.status_code}",
                    "response_time_ms": round(response_time, 2)
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Spotify API check failed: {str(e)}",
                "response_time_ms": 0
            }
    
    def check_openai_api(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity"""
        try:
            start_time = time.time()
            # Simple connectivity check
            response = requests.get("https://api.openai.com/v1/models", 
                                  headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"},
                                  timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "message": "OpenAI API accessible",
                    "response_time_ms": round(response_time, 2)
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"OpenAI API returned status {response.status_code}",
                    "response_time_ms": round(response_time, 2)
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"OpenAI API check failed: {str(e)}",
                "response_time_ms": 0
            }
    
    def check_youtube_api(self) -> Dict[str, Any]:
        """Check YouTube API connectivity"""
        try:
            start_time = time.time()
            # Simple connectivity check
            response = requests.get("https://www.googleapis.com/youtube/v3/search", 
                                  params={"key": config.YOUTUBE_API_KEY, "q": "test", "maxResults": 1},
                                  timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "message": "YouTube API accessible",
                    "response_time_ms": round(response_time, 2)
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"YouTube API returned status {response.status_code}",
                    "response_time_ms": round(response_time, 2)
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"YouTube API check failed: {str(e)}",
                "response_time_ms": 0
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        uptime = datetime.now() - self.start_time
        return {
            "uptime_seconds": int(uptime.total_seconds()),
            "environment": config.ENVIRONMENT,
            "debug_mode": config.DEBUG,
            "log_level": config.LOG_LEVEL,
            "rate_limit_requests": config.RATE_LIMIT_REQUESTS,
            "rate_limit_window_minutes": config.RATE_LIMIT_WINDOW_MINUTES
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status"""
        checks = {
            "redis": self.check_redis_connection(),
            "spotify": self.check_spotify_api(),
            "openai": self.check_openai_api(),
            "youtube": self.check_youtube_api()
        }
        
        # Determine overall health
        statuses = [check["status"] for check in checks.values()]
        if "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "degraded" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_info(),
            "checks": checks
        }

# Global health checker instance
health_checker = HealthChecker()

def get_health_status() -> Dict[str, Any]:
    """Get current health status"""
    return health_checker.run_all_checks()

def get_health_summary() -> Dict[str, Any]:
    """Get simplified health summary"""
    full_status = get_health_status()
    return {
        "status": full_status["status"],
        "timestamp": full_status["timestamp"],
        "uptime_seconds": full_status["system"]["uptime_seconds"],
        "checks_passed": sum(1 for check in full_status["checks"].values() if check["status"] == "healthy"),
        "total_checks": len(full_status["checks"])
    }
