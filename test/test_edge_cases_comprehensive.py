#!/usr/bin/env python3
"""
Comprehensive edge case tests for the Weather Dashboard application.

This test file focuses on boundary conditions, error states, and unusual
input scenarios that might not be covered in regular unit tests.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from datetime import datetime, timedelta
import json

from config import Config
from core.weather.weather_models import WeatherData, ForecastData
from services.weather_service import WeatherService
from core.weather.api import WeatherAPI


class TestBoundaryConditions(unittest.TestCase):
    """Test boundary conditions and extreme values."""
    
    def test_temperature_extremes(self):
        """Test handling of extreme temperature values."""
        # Test extremely high temperature
        weather_hot = WeatherData(
            city="Death Valley",
            temperature=134.0,  # Record high temperature
            timestamp=datetime.now().isoformat(),
            units="fahrenheit"
        )
        self.assertEqual(weather_hot.temperature, 134.0)
        
        # Test extremely low temperature
        weather_cold = WeatherData(
            city="Antarctica",
            temperature=-128.6,  # Record low temperature
            timestamp=datetime.now().isoformat(),
            units="fahrenheit"
        )
        self.assertEqual(weather_cold.temperature, -128.6)
        
        # Test absolute zero (edge case)
        weather_absolute_zero = WeatherData(
            city="Laboratory",
            temperature=-459.67,  # Absolute zero in Fahrenheit
            timestamp=datetime.now().isoformat(),
            units="fahrenheit"
        )
        self.assertEqual(weather_absolute_zero.temperature, -459.67)
    
    def test_humidity_boundaries(self):
        """Test humidity boundary values."""
        # Test 0% humidity
        weather_dry = WeatherData(
            city="Desert",
            temperature=100.0,
            humidity=0,
            timestamp=datetime.now().isoformat(),
            units="imperial"
        )
        self.assertEqual(weather_dry.humidity, 0)
        
        # Test 100% humidity
        weather_saturated = WeatherData(
            city="Rainforest",
            temperature=80.0,
            humidity=100,
            timestamp=datetime.now().isoformat(),
            units="imperial"
        )
        self.assertEqual(weather_saturated.humidity, 100)
        
        # Test invalid humidity values should raise error
        with self.assertRaises(ValueError):
            WeatherData(
                city="Invalid",
                temperature=70.0,
                humidity=101,  # Invalid: > 100%
                timestamp=datetime.now().isoformat(),
                units="imperial"
            )
        
        with self.assertRaises(ValueError):
            WeatherData(
                city="Invalid",
                temperature=70.0,
                humidity=-1,  # Invalid: < 0%
                timestamp=datetime.now().isoformat(),
                units="imperial"
            )
    
    def test_pressure_extremes(self):
        """Test atmospheric pressure extreme values."""
        # Test record low pressure (typhoon)
        weather_low_pressure = WeatherData(
            city="Typhoon Center",
            temperature=80.0,
            pressure=25.69,  # Record low pressure in inHg
            timestamp=datetime.now().isoformat(),
            units="imperial"
        )
        self.assertEqual(weather_low_pressure.pressure, 25.69)
        
        # Test high pressure
        weather_high_pressure = WeatherData(
            city="High Pressure System",
            temperature=70.0,
            pressure=32.01,  # Very high pressure in inHg
            timestamp=datetime.now().isoformat(),
            units="imperial"
        )
        self.assertEqual(weather_high_pressure.pressure, 32.01)


class TestErrorConditions(unittest.TestCase):
    """Test error conditions and recovery scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock(spec=Config)
        self.config.api_key = "test_key"
        self.config.base_url = "https://api.test.com"
        self.config.request_timeout = 5
        self.config.max_retries = 3
        self.config.min_request_interval = 0.1
        self.config.units = "imperial"
    
    @patch('requests.Session.get')
    def test_network_timeout_recovery(self, mock_get):
        """Test recovery from network timeout."""
        import requests
        
        # First call times out, second succeeds
        mock_get.side_effect = [
            requests.exceptions.Timeout("Request timed out"),
            Mock(status_code=200, json=lambda: {"name": "Test City", "main": {"temp": 70}})
        ]
        
        api = WeatherAPI(self.config)
        result = api.fetch_weather("Test City")
        
        # Should eventually succeed after retry
        self.assertEqual(mock_get.call_count, 2)
        self.assertNotIn("error", result)
    
    @patch('requests.Session.get')
    def test_rate_limit_handling(self, mock_get):
        """Test proper handling of rate limiting."""
        # Simulate rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"message": "Too many requests"}
        mock_get.return_value = mock_response
        
        api = WeatherAPI(self.config)
        result = api.fetch_weather("Test City")
        
        # Should return error for rate limiting
        self.assertIn("error", result)
        self.assertIn("rate", result["error"].lower())
    
    def test_malformed_json_response(self):
        """Test handling of malformed JSON responses."""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_response.text = "Not valid JSON"
            mock_get.return_value = mock_response
            
            api = WeatherAPI(self.config)
            result = api.fetch_weather("Test City")
            
            self.assertIn("error", result)
    
    def test_empty_city_name(self):
        """Test handling of empty or whitespace-only city names."""
        api = WeatherAPI(self.config)
        
        # Test empty string
        result_empty = api.fetch_weather("")
        self.assertIn("error", result_empty)
        
        # Test whitespace only
        result_whitespace = api.fetch_weather("   ")
        self.assertIn("error", result_whitespace)
        
        # Test None
        result_none = api.fetch_weather(None)
        self.assertIn("error", result_none)
    
    def test_unicode_city_names(self):
        """Test handling of unicode city names."""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "name": "Москва",  # Moscow in Cyrillic
                "main": {"temp": -5, "humidity": 80}
            }
            mock_get.return_value = mock_response
            
            api = WeatherAPI(self.config)
            result = api.fetch_weather("Москва")
            
            self.assertNotIn("error", result)
            self.assertEqual(result["city"], "Москва")


class TestDataConsistency(unittest.TestCase):
    """Test data consistency and integrity."""
    
    def test_timestamp_formats(self):
        """Test various timestamp format handling."""
        # ISO format
        weather1 = WeatherData(
            city="Test",
            temperature=70.0,
            timestamp="2023-12-01T12:00:00Z",
            units="imperial"
        )
        self.assertEqual(weather1.timestamp, "2023-12-01T12:00:00Z")
        
        # Unix timestamp (should be converted)
        timestamp_unix = 1701432000  # 2023-12-01 12:00:00 UTC
        weather2 = WeatherData(
            city="Test",
            temperature=70.0,
            timestamp=str(timestamp_unix),
            units="imperial"
        )
        self.assertIsNotNone(weather2.timestamp)
    
    def test_unit_consistency(self):
        """Test that units are handled consistently."""
        # Test imperial units
        weather_imperial = WeatherData(
            city="US City",
            temperature=70.0,  # Fahrenheit
            wind_speed=10.0,   # mph
            units="imperial"
        )
        self.assertEqual(weather_imperial.units, "imperial")
        
        # Test metric units
        weather_metric = WeatherData(
            city="EU City",
            temperature=21.0,  # Celsius
            wind_speed=16.0,   # km/h
            units="metric"
        )
        self.assertEqual(weather_metric.units, "metric")
    
    def test_missing_optional_fields(self):
        """Test behavior with various combinations of missing optional fields."""
        # Minimal valid data
        minimal_weather = WeatherData(
            city="Minimal City",
            temperature=70.0,
            timestamp=datetime.now().isoformat(),
            units="imperial"
        )
        
        # Should have defaults or None for missing fields
        self.assertIsNone(minimal_weather.humidity)
        self.assertIsNone(minimal_weather.pressure)
        self.assertIsNone(minimal_weather.wind_speed)
        self.assertIsNone(minimal_weather.weather_description)


class TestConcurrencyAndRacing(unittest.TestCase):
    """Test concurrent access and racing conditions."""
    
    def test_rapid_api_calls(self):
        """Test rapid successive API calls don't cause issues."""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "name": "Test City",
                "main": {"temp": 70, "humidity": 50}
            }
            mock_get.return_value = mock_response
            
            api = WeatherAPI(self.config)
            
            # Make rapid successive calls
            results = []
            for i in range(5):
                result = api.fetch_weather(f"City{i}")
                results.append(result)
            
            # All should succeed without interference
            for result in results:
                self.assertNotIn("error", result)
    
    def test_database_concurrent_access(self):
        """Test concurrent database access scenarios."""
        # This would require more complex setup with threading
        # For now, just test that basic operations don't interfere
        from core.database.data_handler import WeatherDataHandler
        
        with tempfile.TemporaryDirectory() as temp_dir:
            handler1 = WeatherDataHandler(data_directory=temp_dir)
            handler2 = WeatherDataHandler(data_directory=temp_dir)
            
            # Both handlers should be able to access the same database
            cities1 = handler1.load_saved_cities()
            cities2 = handler2.load_saved_cities()
            
            # Should return same results (empty lists for new database)
            self.assertEqual(cities1, cities2)


if __name__ == '__main__':
    unittest.main()