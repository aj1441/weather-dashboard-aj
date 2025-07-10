"""Unit tests for the WeatherAPI class"""

import unittest
from unittest.mock import patch, Mock, MagicMock, call
import json
import requests
import time
import os

from core.api import WeatherAPI
from config import Config


def load_mock_data(filename):
    """Helper to load mock data from JSON files"""
    filepath = os.path.join(os.path.dirname(__file__), "mock_data", filename)
    with open(filepath, "r") as f:
        return json.load(f)


class TestWeatherAPI(unittest.TestCase):
    """Test suite for the WeatherAPI class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.config = Config(
            api_key="test_api_key",
            base_url="https://api.openweathermap.org/data/2.5/weather",
            units="imperial",
            request_timeout=5,
            max_retries=3,
            min_request_interval=0.5  # For testing rate limiting
        )
        self.api = WeatherAPI(self.config)

    @patch("requests.Session.get")
    def test_fetch_weather_success(self, mock_get):
        """Test fetch_weather returns correctly formatted data on success"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = load_mock_data("weather_success.json")
        mock_get.return_value = mock_response

        # Act
        result = self.api.fetch_weather("New York")

        # Assert
        self.assertEqual(result["city"], "New York")
        self.assertEqual(result["temperature"], 75.2)
        self.assertEqual(result["description"], "clear sky")
        self.assertEqual(result["icon"], "01d")
        mock_get.assert_called_once()

    @patch("requests.Session.get")
    def test_fetch_weather_api_error(self, mock_get):
        """Test fetch_weather handles API errors correctly"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = load_mock_data("weather_api_error.json")
        mock_get.return_value = mock_response

        # Act
        result = self.api.fetch_weather("New York")

        # Assert
        self.assertIn("error", result)
        self.assertEqual(result["error"], "API Error: Invalid API key")

    @patch("requests.Session.get")
    def test_fetch_weather_network_error(self, mock_get):
        """Test fetch_weather handles network errors correctly"""
        # Arrange
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        # Act
        result = self.api.fetch_weather("New York")

        # Assert
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Network Error: Connection error")

    @patch("requests.Session.get")
    def test_get_coordinates_success(self, mock_get):
        """Test get_coordinates returns correct coordinates on success"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = load_mock_data("coordinates_success.json")
        mock_get.return_value = mock_response

        # Act
        result = self.api.get_coordinates("Denver", "CO")

        # Assert
        self.assertEqual(result["lat"], 39.7392)
        self.assertEqual(result["lon"], -104.9903)
        self.assertEqual(result["city"], "Denver")
        self.assertEqual(result["state"], "Colorado")

    @patch("requests.Session.get")
    def test_get_forecast_success(self, mock_get):
        """Test get_forecast returns correctly formatted forecast data"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = load_mock_data("forecast_response.json")
        mock_get.return_value = mock_response

        # Act
        result = self.api.get_forecast(39.7392, -104.9903)

        # Assert
        self.assertEqual(result["city"], "Denver")
        self.assertEqual(len(result["forecast"]), 2)
        self.assertEqual(result["forecast"][0]["temperature"], 75.2)
        self.assertEqual(result["forecast"][1]["description"], "few clouds")

    # New tests for edge cases
    @patch("requests.Session.get")
    def test_city_not_found(self, mock_get):
        """Test handling of non-existent city"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = load_mock_data("city_not_found.json")
        mock_get.return_value = mock_response

        # Act
        result = self.api.fetch_weather("NonExistentCity")

        # Assert
        self.assertIn("error", result)
        self.assertEqual(result["error"], "API Error: city not found")

    @patch("requests.Session.get")
    def test_malformed_response(self, mock_get):
        """Test handling of malformed API response"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = load_mock_data("malformed_response.json")
        mock_get.return_value = mock_response

        # Act
        result = self.api.fetch_weather("Malformed")

        # Assert
        self.assertIn("error", result)
        self.assertTrue("Data validation error" in result["error"])

    # Tests for rate limiting
    @patch("time.sleep")
    @patch("requests.Session.get")
    def test_rate_limiting(self, mock_get, mock_sleep):
        """Test rate limiting between API calls"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = load_mock_data("weather_success.json")
        mock_get.return_value = mock_response

        # Act - Make multiple calls in succession
        self.api.fetch_weather("City1")
        self.api.fetch_weather("City2")
        self.api.fetch_weather("City3")

        # Assert - Should have slept between calls for rate limiting
        self.assertEqual(mock_sleep.call_count, 2)  # Called after first and second requests
        self.assertEqual(mock_sleep.call_args_list[0][0][0], 0.5)  # Slept for 0.5 seconds

    # Tests for retry functionality
    @patch("time.sleep")
    @patch("requests.Session.get")
    def test_retry_on_failure(self, mock_get, mock_sleep):
        """Test retry mechanism on temporary failures"""
        # Arrange - First 2 calls fail, third succeeds
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = load_mock_data("weather_success.json")
        
        mock_response_rate_limit = Mock()
        mock_response_rate_limit.status_code = 429
        mock_response_rate_limit.json.return_value = load_mock_data("rate_limit_exceeded.json")
        
        # First two calls return 429 (rate limit), third succeeds
        mock_get.side_effect = [mock_response_rate_limit, mock_response_rate_limit, mock_response_success]

        # Act
        result = self.api.fetch_weather("RetryCity")

        # Assert
        self.assertEqual(mock_get.call_count, 3)  # Called 3 times
        self.assertEqual(mock_sleep.call_count, 2)  # Slept between retries
        self.assertEqual(result["city"], "New York")  # Eventually succeeded
        
    @patch("requests.Session.get")
    def test_max_retries_exceeded(self, mock_get):
        """Test behavior when max retries are exceeded"""
        # Arrange - All calls fail with rate limit error
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = load_mock_data("rate_limit_exceeded.json")
        mock_get.return_value = mock_response

        # Act
        result = self.api.fetch_weather("MaxRetriesCity")

        # Assert
        self.assertEqual(mock_get.call_count, self.config.max_retries)  # Called max_retries times
        self.assertIn("error", result)
        self.assertTrue("Rate limit exceeded" in result["error"])

    @patch("requests.Session.get")
    def test_empty_response(self, mock_get):
        """Test handling of empty API response"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        # Act
        result = self.api.fetch_weather("EmptyResponseCity")

        # Assert
        self.assertIn("error", result)
        self.assertTrue("Invalid data format" in result["error"] or 
                        "Data validation error" in result["error"])

if __name__ == "__main__":
    unittest.main()