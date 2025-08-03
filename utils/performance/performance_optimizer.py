"""
Performance optimization utilities for the weather dashboard application.

This module provides caching, connection pooling, and performance monitoring
to improve application responsiveness and reduce API calls.
"""

import time
import logging
import threading
from typing import Dict, Any, Optional, Callable, List
from functools import wraps, lru_cache
from datetime import datetime, timedelta
from collections import OrderedDict
import sqlite3
import requests

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and log performance metrics for the application."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.lock = threading.Lock()
    
    def record_metric(self, operation: str, duration: float) -> None:
        """Record a performance metric."""
        with self.lock:
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
    
    def get_average_time(self, operation: str) -> Optional[float]:
        """Get average execution time for an operation."""
        with self.lock:
            if operation in self.metrics and self.metrics[operation]:
                return sum(self.metrics[operation]) / len(self.metrics[operation])
        return None
    
    def get_slowest_operations(self, limit: int = 5) -> List[tuple]:
        """Get the slowest operations by average time."""
        with self.lock:
            averages = []
            for operation, times in self.metrics.items():
                if times:
                    avg_time = sum(times) / len(times)
                    averages.append((operation, avg_time, len(times)))
            
            return sorted(averages, key=lambda x: x[1], reverse=True)[:limit]
    
    def log_performance_report(self) -> None:
        """Log a performance report."""
        slowest = self.get_slowest_operations()
        if slowest:
            logger.info("Performance Report:")
            for operation, avg_time, count in slowest:
                logger.info(f"  {operation}: {avg_time:.3f}s avg ({count} calls)")

# Global performance monitor
performance_monitor = PerformanceMonitor()

def monitor_performance(operation_name: str):
    """Decorator to monitor function performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                performance_monitor.record_metric(operation_name, duration)
                if duration > 1.0:  # Log slow operations
                    logger.warning(f"Slow operation detected: {operation_name} took {duration:.3f}s")
        return wrapper
    return decorator

class LRUCache:
    """Simple LRU cache implementation for API responses."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: OrderedDict = OrderedDict()
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
        return None
    
    def put(self, key: str, value: Any) -> None:
        """Put a value in cache."""
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
            else:
                # Remove oldest if cache is full
                if len(self.cache) >= self.max_size:
                    self.cache.popitem(last=False)
            self.cache[key] = value
    
    def clear(self) -> None:
        """Clear the cache."""
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        with self.lock:
            return len(self.cache)

class ConnectionPool:
    """Connection pool for database and HTTP connections."""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.db_connections: List[sqlite3.Connection] = []
        self.http_sessions: List[requests.Session] = []
        self.lock = threading.Lock()
    
    def get_db_connection(self, db_path: str) -> sqlite3.Connection:
        """Get a database connection from the pool."""
        with self.lock:
            if self.db_connections:
                conn = self.db_connections.pop()
                try:
                    # Test if connection is still valid
                    conn.execute("SELECT 1")
                    return conn
                except sqlite3.Error:
                    # Connection is invalid, create new one
                    pass
            
            # Create new connection
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    def return_db_connection(self, conn: sqlite3.Connection) -> None:
        """Return a database connection to the pool."""
        with self.lock:
            if len(self.db_connections) < self.max_connections:
                try:
                    # Reset connection state
                    conn.rollback()
                    self.db_connections.append(conn)
                except sqlite3.Error:
                    # Connection is broken, don't return it
                    pass
            else:
                # Pool is full, close the connection
                conn.close()
    
    def get_http_session(self) -> requests.Session:
        """Get an HTTP session from the pool."""
        with self.lock:
            if self.http_sessions:
                return self.http_sessions.pop()
            else:
                session = requests.Session()
                # Configure session for better performance
                session.headers.update({
                    'User-Agent': 'WeatherDashboard/1.0',
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate'
                })
                return session
    
    def return_http_session(self, session: requests.Session) -> None:
        """Return an HTTP session to the pool."""
        with self.lock:
            if len(self.http_sessions) < self.max_connections:
                # Clear any response data
                session.close()
                self.http_sessions.append(session)
            else:
                # Pool is full, close the session
                session.close()

class APICache:
    """Cache for API responses with TTL (Time To Live)."""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = LRUCache(max_size=200)
        self.ttl = default_ttl
        self.timestamps: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cached API response if not expired."""
        with self.lock:
            if key in self.timestamps:
                if time.time() - self.timestamps[key] > self.ttl:
                    # Expired, remove from cache
                    self.cache.get(key)  # Remove from LRU cache
                    del self.timestamps[key]
                    return None
            
            return self.cache.get(key)
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Cache an API response with TTL."""
        with self.lock:
            self.cache.put(key, value)
            self.timestamps[key] = time.time()
            if ttl is not None:
                # Store custom TTL for this key
                self.timestamps[f"{key}_ttl"] = ttl
    
    def clear_expired(self) -> int:
        """Clear expired entries and return count of cleared items."""
        current_time = time.time()
        cleared = 0
        
        with self.lock:
            expired_keys = []
            for key, timestamp in self.timestamps.items():
                if not key.endswith('_ttl'):
                    ttl = self.timestamps.get(f"{key}_ttl", self.ttl)
                    if current_time - timestamp > ttl:
                        expired_keys.append(key)
            
            for key in expired_keys:
                self.cache.get(key)  # Remove from LRU cache
                del self.timestamps[key]
                if f"{key}_ttl" in self.timestamps:
                    del self.timestamps[f"{key}_ttl"]
                cleared += 1
        
        if cleared > 0:
            logger.debug(f"Cleared {cleared} expired cache entries")
        
        return cleared

# Global instances
connection_pool = ConnectionPool()
api_cache = APICache()

def cache_api_response(ttl: int = 300):
    """Decorator to cache API responses."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache first
            cached_result = api_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            if result is not None and not isinstance(result, dict) or 'error' not in result:
                api_cache.put(cache_key, result, ttl)
                logger.debug(f"Cached result for {func.__name__}")
            
            return result
        return wrapper
    return decorator

def optimize_database_queries():
    """Apply database optimizations."""
    logger.info("Applying database optimizations...")
    
    # These optimizations should be applied to the database
    optimizations = [
        "PRAGMA journal_mode=WAL;",  # Write-Ahead Logging for better concurrency
        "PRAGMA synchronous=NORMAL;",  # Faster writes with reasonable safety
        "PRAGMA cache_size=10000;",  # Increase cache size
        "PRAGMA temp_store=MEMORY;",  # Store temp tables in memory
        "PRAGMA mmap_size=268435456;",  # 256MB memory mapping
    ]
    
    return optimizations

def batch_database_operations(operations: List[Callable]) -> None:
    """Execute database operations in batches for better performance."""
    if not operations:
        return
    
    # Group operations by type for better batching
    batch_size = 50  # SQLite recommended batch size
    
    for i in range(0, len(operations), batch_size):
        batch = operations[i:i + batch_size]
        try:
            for operation in batch:
                operation()
        except Exception as e:
            logger.error(f"Error in batch operation {i//batch_size}: {e}")
            # Continue with next batch instead of failing completely

def cleanup_performance_data():
    """Clean up old performance data and expired cache entries."""
    logger.info("Cleaning up performance data...")
    
    # Clear expired API cache entries
    cleared = api_cache.clear_expired()
    logger.info(f"Cleared {cleared} expired cache entries")
    
    # Log performance report
    performance_monitor.log_performance_report()
    
    # Clear old performance metrics (keep last 1000 entries per operation)
    with performance_monitor.lock:
        for operation in performance_monitor.metrics:
            if len(performance_monitor.metrics[operation]) > 1000:
                performance_monitor.metrics[operation] = performance_monitor.metrics[operation][-1000:] 