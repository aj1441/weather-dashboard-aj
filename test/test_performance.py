#!/usr/bin/env python3
"""
Performance tests for the weather dashboard application.

This script tests the performance optimizations including:
- API caching
- Database connection pooling
- Performance monitoring
- Memory usage
"""

import unittest
import time
import threading
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.performance.performance_optimizer import (
    PerformanceMonitor, LRUCache, ConnectionPool, APICache,
    monitor_performance, cache_api_response, connection_pool, api_cache
)
from config import Config
from core.database.database import WeatherDatabase
from core.weather.api import WeatherAPI

class TestPerformanceOptimizations(unittest.TestCase):
    """Test performance optimization features."""
    
    def setUp(self):
        """Set up test environment."""
        self.config = Config.from_environment()
        self.db = WeatherDatabase(":memory:")  # Use in-memory database for testing
    
    def test_performance_monitor(self):
        """Test performance monitoring functionality."""
        monitor = PerformanceMonitor()
        
        # Record some metrics
        monitor.record_metric("test_op", 0.5)
        monitor.record_metric("test_op", 1.0)
        monitor.record_metric("test_op", 1.5)
        
        # Check average time
        avg_time = monitor.get_average_time("test_op")
        self.assertAlmostEqual(avg_time, 1.0, places=1)
        
        # Check slowest operations
        slowest = monitor.get_slowest_operations()
        self.assertEqual(len(slowest), 1)
        self.assertEqual(slowest[0][0], "test_op")
    
    def test_lru_cache(self):
        """Test LRU cache functionality."""
        cache = LRUCache(max_size=3)
        
        # Add items
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # Check size
        self.assertEqual(cache.size(), 3)
        
        # Access key1 to make it most recently used
        self.assertEqual(cache.get("key1"), "value1")
        
        # Add another item - should evict key2 (least recently used)
        cache.put("key4", "value4")
        self.assertEqual(cache.size(), 3)
        self.assertIsNone(cache.get("key2"))  # Should be evicted
        self.assertIsNotNone(cache.get("key1"))  # Should still be there
    
    def test_api_cache(self):
        """Test API cache with TTL."""
        cache = APICache(default_ttl=1)  # 1 second TTL for testing
        
        # Add item
        cache.put("test_key", "test_value")
        self.assertEqual(cache.get("test_key"), "test_value")
        
        # Wait for expiration
        time.sleep(1.1)
        self.assertIsNone(cache.get("test_key"))
    
    def test_cache_decorator(self):
        """Test the cache decorator."""
        call_count = 0
        
        @cache_api_response(ttl=60)
        def test_function(param):
            nonlocal call_count
            call_count += 1
            return f"result_{param}"
        
        # First call should execute function
        result1 = test_function("test")
        self.assertEqual(result1, "result_test")
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result2 = test_function("test")
        self.assertEqual(result2, "result_test")
        self.assertEqual(call_count, 1)  # Should not increment
    
    def test_monitor_decorator(self):
        """Test the performance monitor decorator."""
        monitor = PerformanceMonitor()
        
        @monitor_performance("test_function")
        def slow_function():
            time.sleep(0.1)  # Simulate slow operation
            return "done"
        
        # Call function
        result = slow_function()
        self.assertEqual(result, "done")
        
        # Check if metric was recorded
        avg_time = monitor.get_average_time("test_function")
        self.assertIsNotNone(avg_time)
        self.assertGreater(avg_time, 0.09)  # Should be close to 0.1s
    
    def test_connection_pool(self):
        """Test connection pooling."""
        pool = ConnectionPool(max_connections=2)
        
        # Get connections
        conn1 = pool.get_db_connection(":memory:")
        conn2 = pool.get_db_connection(":memory:")
        
        # Pool should be empty now
        self.assertEqual(len(pool.db_connections), 0)
        
        # Return connections
        pool.return_db_connection(conn1)
        pool.return_db_connection(conn2)
        
        # Pool should have connections now
        self.assertEqual(len(pool.db_connections), 2)
    
    def test_database_performance(self):
        """Test database performance with optimizations."""
        # Test database operations with monitoring
        start_time = time.time()
        
        # Perform multiple database operations
        for i in range(10):
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should be reasonably fast (less than 1 second for 10 operations)
        self.assertLess(total_time, 1.0)
    
    def test_concurrent_access(self):
        """Test concurrent access to performance components."""
        results = []
        errors = []
        
        def worker(worker_id):
            try:
                # Test cache access
                api_cache.put(f"key_{worker_id}", f"value_{worker_id}")
                value = api_cache.get(f"key_{worker_id}")
                results.append((worker_id, value == f"value_{worker_id}"))
            except Exception as e:
                errors.append((worker_id, str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 10)
        for worker_id, success in results:
            self.assertTrue(success, f"Worker {worker_id} failed")
    
    def test_memory_usage(self):
        """Test memory usage of performance components."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create and use performance components
        cache = LRUCache(max_size=1000)
        for i in range(1000):
            cache.put(f"key_{i}", f"value_{i}" * 100)  # Large values
        
        # Check memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        self.assertLess(memory_increase, 50 * 1024 * 1024)
    
    def test_cleanup_functionality(self):
        """Test cleanup functionality."""
        # Add some data to cache
        api_cache.put("test_key", "test_value", ttl=1)
        self.assertEqual(api_cache.get("test_key"), "test_value")
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Clear expired entries
        cleared = api_cache.clear_expired()
        self.assertEqual(cleared, 1)
        self.assertIsNone(api_cache.get("test_key"))

def run_performance_benchmark():
    """Run a comprehensive performance benchmark."""
    print("Running Performance Benchmark...")
    print("=" * 50)
    
    # Test API cache performance
    print("Testing API Cache Performance...")
    start_time = time.time()
    
    for i in range(1000):
        api_cache.put(f"benchmark_key_{i}", f"benchmark_value_{i}")
        api_cache.get(f"benchmark_key_{i}")
    
    cache_time = time.time() - start_time
    print(f"API Cache: 1000 operations in {cache_time:.3f}s")
    
    # Test database performance
    print("\nTesting Database Performance...")
    db = WeatherDatabase(":memory:")
    start_time = time.time()
    
    for i in range(100):
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
    
    db_time = time.time() - start_time
    print(f"Database: 100 operations in {db_time:.3f}s")
    
    # Test connection pool performance
    print("\nTesting Connection Pool Performance...")
    pool = ConnectionPool()
    start_time = time.time()
    
    for i in range(50):
        session = pool.get_http_session()
        pool.return_http_session(session)
    
    pool_time = time.time() - start_time
    print(f"Connection Pool: 50 operations in {pool_time:.3f}s")
    
    print("\nBenchmark Complete!")
    print("=" * 50)

if __name__ == "__main__":
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run benchmark
    run_performance_benchmark() 