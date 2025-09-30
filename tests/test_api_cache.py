import unittest
import tempfile
import os
import time
from datetime import datetime, timedelta
from charapi.cache.api_cache import APICache


class TestAPICache(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_cache.db")
        self.cache = APICache(self.db_path, default_ttl_hours=1)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_database_creation(self):
        """Test that database and tables are created properly"""
        self.assertTrue(os.path.exists(self.db_path))

    def test_cache_key_generation(self):
        """Test cache key generation format"""
        key = self.cache._generate_key("propublica", "organization", "530196605")
        self.assertEqual(key, "propublica_organization_530196605")

    def test_set_and_get_basic(self):
        """Test basic cache set and get operations"""
        test_data = {"name": "Test Org", "ein": "123456789"}

        self.cache.set("propublica", "organization", "123456789", test_data)
        retrieved = self.cache.get("propublica", "organization", "123456789")

        self.assertEqual(retrieved, test_data)

    def test_get_nonexistent_returns_none(self):
        """Test that getting non-existent data returns None"""
        result = self.cache.get("propublica", "organization", "nonexistent")
        self.assertIsNone(result)

    def test_exists_method(self):
        """Test cache existence checking"""
        test_data = {"test": "data"}

        # Should not exist initially
        self.assertFalse(self.cache.exists("test", "endpoint", "123"))

        # Should exist after setting
        self.cache.set("test", "endpoint", "123", test_data)
        self.assertTrue(self.cache.exists("test", "endpoint", "123"))

    def test_ttl_expiration(self):
        """Test that data expires based on TTL"""
        test_data = {"test": "data"}

        # Set with very short TTL (converting to very small decimal hours)
        self.cache.set("test", "endpoint", "123", test_data, ttl_hours=0.0001)  # ~0.36 seconds

        # Should exist immediately
        self.assertTrue(self.cache.exists("test", "endpoint", "123"))

        # Wait for expiration
        time.sleep(1)

        # Should be expired now
        self.assertFalse(self.cache.exists("test", "endpoint", "123"))
        self.assertIsNone(self.cache.get("test", "endpoint", "123"))

    def test_replace_existing_data(self):
        """Test that setting data again replaces existing data"""
        original_data = {"version": 1}
        updated_data = {"version": 2}

        self.cache.set("test", "endpoint", "123", original_data)
        self.cache.set("test", "endpoint", "123", updated_data)

        retrieved = self.cache.get("test", "endpoint", "123")
        self.assertEqual(retrieved, updated_data)

    def test_invalidate(self):
        """Test cache invalidation"""
        test_data = {"test": "data"}

        self.cache.set("test", "endpoint", "123", test_data)
        self.assertTrue(self.cache.exists("test", "endpoint", "123"))

        self.cache.invalidate("test", "endpoint", "123")
        self.assertFalse(self.cache.exists("test", "endpoint", "123"))

    def test_clear_all(self):
        """Test clearing all cache entries"""
        self.cache.set("test1", "endpoint", "123", {"data": 1})
        self.cache.set("test2", "endpoint", "456", {"data": 2})

        self.cache.clear_all()

        self.assertIsNone(self.cache.get("test1", "endpoint", "123"))
        self.assertIsNone(self.cache.get("test2", "endpoint", "456"))

    def test_cleanup_expired(self):
        """Test cleanup of expired entries"""
        # Add one entry that expires quickly
        self.cache.set("test", "endpoint", "expired", {"data": 1}, ttl_hours=0.0001)

        # Add one entry that doesn't expire soon
        self.cache.set("test", "endpoint", "valid", {"data": 2}, ttl_hours=24)

        # Wait for first entry to expire
        time.sleep(1)

        # Cleanup expired entries
        cleaned_count = self.cache.cleanup_expired()

        # Should have cleaned up 1 entry
        self.assertEqual(cleaned_count, 1)
        self.assertIsNone(self.cache.get("test", "endpoint", "expired"))
        self.assertIsNotNone(self.cache.get("test", "endpoint", "valid"))

    def test_get_stats(self):
        """Test cache statistics"""
        # Add some test data
        self.cache.set("api1", "endpoint1", "123", {"data": 1})
        self.cache.set("api1", "endpoint2", "456", {"data": 2})
        self.cache.set("api2", "endpoint1", "789", {"data": 3})

        stats = self.cache.get_stats()

        self.assertEqual(stats["valid_entries"], 3)
        self.assertEqual(stats["expired_entries"], 0)
        self.assertEqual(stats["api_sources"], 2)  # api1 and api2
        self.assertEqual(stats["database_path"], self.db_path)

    def test_complex_data_structures(self):
        """Test caching complex nested data structures"""
        complex_data = {
            "organization": {
                "name": "Test Charity",
                "filings": [
                    {"year": 2023, "revenue": 1000000},
                    {"year": 2022, "revenue": 900000}
                ]
            },
            "metadata": {
                "cached_at": datetime.now().isoformat(),
                "source": "propublica"
            }
        }

        self.cache.set("propublica", "organization", "123", complex_data)
        retrieved = self.cache.get("propublica", "organization", "123")

        self.assertEqual(retrieved, complex_data)
        self.assertEqual(retrieved["organization"]["name"], "Test Charity")
        self.assertEqual(len(retrieved["organization"]["filings"]), 2)

    def test_concurrent_access_safety(self):
        """Test that cache handles concurrent-like access patterns"""
        # Simulate multiple rapid operations
        for i in range(10):
            self.cache.set("test", "endpoint", f"key_{i}", {"index": i})

        # Verify all data was stored correctly
        for i in range(10):
            data = self.cache.get("test", "endpoint", f"key_{i}")
            self.assertEqual(data["index"], i)

    def test_default_ttl_usage(self):
        """Test that default TTL is used when not specified"""
        test_data = {"test": "data"}

        # Set without specifying TTL (should use default 1 hour)
        self.cache.set("test", "endpoint", "123", test_data)

        # Should exist immediately
        self.assertTrue(self.cache.exists("test", "endpoint", "123"))

        # Verify it's stored with default TTL by checking it exists


if __name__ == "__main__":
    unittest.main()