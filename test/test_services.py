"""
Comprehensive unit tests for the service layer.

Tests cover WeatherService, DataService, ThemeService, and ValidationService
with proper mocking and edge case handling.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from config import Config
from services import WeatherService, DataService, ThemeService, ValidationService
from core.weather.weather_models import WeatherData, ForecastData, ComprehensiveWeatherData, SavedCity


class TestWeatherService(unittest.TestCase):
    """Test cases for WeatherService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock(spec=Config)
        self.config.units = "imperial"
        self.weather_service = WeatherService(self.config)
    
    @patch('services.weather_service.WeatherAPI')
    def test_get_current_weather_success(self, mock_api_class):
        """Test successful current weather retrieval."""
        # Mock API response
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        mock_api.fetch_weather.return_value = {
            "name": "Test City",
            "main": {"temp": 72.5, "humidity": 65},
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "wind": {"speed": 10.5}
        }
        
        # Mock validator
        self.weather_service.validator.validate_weather_data.return_value = True
        
        # Test
        result = self.weather_service.get_current_weather("Test City")
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.city, "Test City")
        self.assertEqual(result.temperature, 72.5)
        mock_api.fetch_weather.assert_called_once_with("Test City")
    
    @patch('services.weather_service.WeatherAPI')
    def test_get_current_weather_api_error(self, mock_api_class):
        """Test current weather retrieval with API error."""
        # Mock API error
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        mock_api.fetch_weather.return_value = {"error": "API Error"}
        
        # Test
        result = self.weather_service.get_current_weather("Test City")
        
        # Assertions
        self.assertIsNone(result)
    
    @patch('services.weather_service.WeatherAPI')
    def test_get_current_weather_validation_failure(self, mock_api_class):
        """Test current weather retrieval with validation failure."""
        # Mock API response
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        mock_api.fetch_weather.return_value = {
            "name": "Test City",
            "main": {"temp": 72.5}
        }
        
        # Mock validator failure
        self.weather_service.validator.validate_weather_data.return_value = False
        
        # Test
        result = self.weather_service.get_current_weather("Test City")
        
        # Assertions
        self.assertIsNone(result)
    
    @patch('services.weather_service.WeatherAPI')
    def test_get_coordinates_success(self, mock_api_class):
        """Test successful coordinate retrieval."""
        # Mock API response
        mock_api = Mock()
        mock_api_class.return_value = mock_api
        mock_api.get_coordinates.return_value = {"lat": 40.7128, "lon": -74.0060}
        
        # Test
        result = self.weather_service.get_coordinates("New York", "NY")
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result["lat"], 40.7128)
        self.assertEqual(result["lon"], -74.0060)
        mock_api.get_coordinates.assert_called_once_with("New York", "NY")
    
    def test_validate_weather_data(self):
        """Test weather data validation."""
        # Mock validator
        self.weather_service.validator.validate_weather_data.return_value = True
        
        # Test
        test_data = {"temp": 72.5, "humidity": 65}
        result = self.weather_service.validate_weather_data(test_data)
        
        # Assertions
        self.assertTrue(result)
        self.weather_service.validator.validate_weather_data.assert_called_once_with(test_data)


class TestDataService(unittest.TestCase):
    """Test cases for DataService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock(spec=Config)
        self.data_service = DataService(self.config)
    
    @patch('services.data_service.WeatherDataHandler')
    def test_save_weather_data_success(self, mock_handler_class):
        """Test successful weather data saving."""
        # Mock data handler
        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.save_weather_data_validated.return_value = True
        
        # Create test weather data
        weather_data = WeatherData(
            city="Test City",
            temperature=72.5,
            humidity=65,
            weather_main="Clear",
            weather_description="clear sky",
            timestamp=datetime.now().isoformat(),
            units="imperial"
        )
        
        # Test
        result = self.data_service.save_weather_data(weather_data)
        
        # Assertions
        self.assertTrue(result)
        mock_handler.save_weather_data_validated.assert_called_once()
    
    @patch('services.data_service.WeatherDataHandler')
    def test_save_weather_data_failure(self, mock_handler_class):
        """Test weather data saving failure."""
        # Mock data handler failure
        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.save_weather_data_validated.return_value = False
        
        # Create test weather data
        weather_data = WeatherData(
            city="Test City",
            temperature=72.5,
            timestamp=datetime.now().isoformat(),
            units="imperial"
        )
        
        # Test
        result = self.data_service.save_weather_data(weather_data)
        
        # Assertions
        self.assertFalse(result)
    
    @patch('services.data_service.WeatherDataHandler')
    def test_save_city_success(self, mock_handler_class):
        """Test successful city saving."""
        # Mock data handler
        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.save_city.return_value = True
        
        # Test
        result = self.data_service.save_city("Test City", "CA", "Test Nickname")
        
        # Assertions
        self.assertTrue(result)
        mock_handler.save_city.assert_called_once()
    
    @patch('services.data_service.WeatherDataHandler')
    def test_get_saved_cities_success(self, mock_handler_class):
        """Test successful saved cities retrieval."""
        # Mock data handler response
        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.load_saved_cities.return_value = [
            {"city": "Test City", "state": "CA", "nickname": "Test"}
        ]
        
        # Test
        result = self.data_service.get_saved_cities()
        
        # Assertions
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].city, "Test City")
        self.assertEqual(result[0].state, "CA")
    
    @patch('services.data_service.WeatherDataHandler')
    def test_delete_city_success(self, mock_handler_class):
        """Test successful city deletion."""
        # Mock data handler
        mock_handler = Mock()
        mock_handler_class.return_value = mock_handler
        mock_handler.delete_city.return_value = True
        
        # Test
        result = self.data_service.delete_city("Test City", "CA")
        
        # Assertions
        self.assertTrue(result)
        mock_handler.delete_city.assert_called_once_with("Test City", "CA")


class TestThemeService(unittest.TestCase):
    """Test cases for ThemeService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock(spec=Config)
        self.theme_service = ThemeService(self.config)
    
    @patch('services.theme_service.create_theme_manager')
    def test_apply_theme_success(self, mock_create_manager):
        """Test successful theme application."""
        # Mock theme manager
        mock_manager = Mock()
        mock_create_manager.return_value = mock_manager
        self.theme_service.theme_manager = mock_manager
        
        # Test
        result = self.theme_service.apply_theme("dark_theme")
        
        # Assertions
        self.assertTrue(result)
        mock_manager.apply_theme.assert_called_once_with("dark_theme")
    
    @patch('services.theme_service.create_theme_manager')
    def test_apply_theme_failure(self, mock_create_manager):
        """Test theme application failure."""
        # Mock theme manager with exception
        mock_manager = Mock()
        mock_create_manager.return_value = mock_manager
        mock_manager.apply_theme.side_effect = Exception("Theme error")
        self.theme_service.theme_manager = mock_manager
        
        # Test
        result = self.theme_service.apply_theme("invalid_theme")
        
        # Assertions
        self.assertFalse(result)
    
    @patch('services.theme_service.create_theme_manager')
    def test_toggle_auto_mode(self, mock_create_manager):
        """Test auto mode toggle."""
        # Mock theme manager
        mock_manager = Mock()
        mock_create_manager.return_value = mock_manager
        mock_manager.is_auto_enabled.side_effect = [False, True]
        self.theme_service.theme_manager = mock_manager
        
        # Test
        result = self.theme_service.toggle_auto_mode()
        
        # Assertions
        self.assertTrue(result)
        mock_manager.toggle_auto_mode.assert_called_once()
    
    @patch('services.theme_service.create_theme_manager')
    def test_get_current_theme(self, mock_create_manager):
        """Test current theme retrieval."""
        # Mock theme manager
        mock_manager = Mock()
        mock_create_manager.return_value = mock_manager
        mock_manager.get_current_theme.return_value = "dark_theme"
        self.theme_service.theme_manager = mock_manager
        
        # Test
        result = self.theme_service.get_current_theme()
        
        # Assertions
        self.assertEqual(result, "dark_theme")


class TestValidationService(unittest.TestCase):
    """Test cases for ValidationService."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock(spec=Config)
        self.config.units = "imperial"
        self.validation_service = ValidationService(self.config)
    
    def test_validate_city_name_valid(self):
        """Test valid city name validation."""
        valid_cities = ["New York", "Los Angeles", "San Francisco", "Miami"]
        
        for city in valid_cities:
            with self.subTest(city=city):
                result = self.validation_service.validate_city_name(city)
                self.assertTrue(result, f"City '{city}' should be valid")
    
    def test_validate_city_name_invalid(self):
        """Test invalid city name validation."""
        invalid_cities = ["", "   ", "A" * 101, "New York123", "City@Name"]
        
        for city in invalid_cities:
            with self.subTest(city=city):
                result = self.validation_service.validate_city_name(city)
                self.assertFalse(result, f"City '{city}' should be invalid")
    
    def test_validate_state_code_valid(self):
        """Test valid state code validation."""
        valid_states = ["CA", "NY", "TX", "FL", "WA"]
        
        for state in valid_states:
            with self.subTest(state=state):
                result = self.validation_service.validate_state_code(state)
                self.assertTrue(result, f"State '{state}' should be valid")
    
    def test_validate_state_code_invalid(self):
        """Test invalid state code validation."""
        invalid_states = ["C", "CAL", "C1", "C@", "12"]
        
        for state in invalid_states:
            with self.subTest(state=state):
                result = self.validation_service.validate_state_code(state)
                self.assertFalse(result, f"State '{state}' should be invalid")
    
    def test_validate_temperature_valid(self):
        """Test valid temperature validation."""
        valid_temps = [32, 72.5, -10, 100, 0]
        
        for temp in valid_temps:
            with self.subTest(temp=temp):
                result = self.validation_service.validate_temperature(temp, "imperial")
                self.assertTrue(result, f"Temperature {temp} should be valid")
    
    def test_validate_temperature_invalid(self):
        """Test invalid temperature validation."""
        invalid_temps = [float('inf'), float('-inf'), float('nan'), -200, 200]
        
        for temp in invalid_temps:
            with self.subTest(temp=temp):
                result = self.validation_service.validate_temperature(temp, "imperial")
                self.assertFalse(result, f"Temperature {temp} should be invalid")
    
    def test_validate_humidity_valid(self):
        """Test valid humidity validation."""
        valid_humidity = [0, 50, 100]
        
        for humidity in valid_humidity:
            with self.subTest(humidity=humidity):
                result = self.validation_service.validate_humidity(humidity)
                self.assertTrue(result, f"Humidity {humidity} should be valid")
    
    def test_validate_humidity_invalid(self):
        """Test invalid humidity validation."""
        invalid_humidity = [-1, 101, 50.5, "50"]
        
        for humidity in invalid_humidity:
            with self.subTest(humidity=humidity):
                result = self.validation_service.validate_humidity(humidity)
                self.assertFalse(result, f"Humidity {humidity} should be invalid")
    
    def test_validate_pressure_valid(self):
        """Test valid pressure validation."""
        valid_pressure = [800, 1013.25, 1200]
        
        for pressure in valid_pressure:
            with self.subTest(pressure=pressure):
                result = self.validation_service.validate_pressure(pressure)
                self.assertTrue(result, f"Pressure {pressure} should be valid")
    
    def test_validate_pressure_invalid(self):
        """Test invalid pressure validation."""
        invalid_pressure = [799, 1201, float('inf'), float('nan')]
        
        for pressure in invalid_pressure:
            with self.subTest(pressure=pressure):
                result = self.validation_service.validate_pressure(pressure)
                self.assertFalse(result, f"Pressure {pressure} should be invalid")
    
    def test_validate_wind_speed_valid(self):
        """Test valid wind speed validation."""
        valid_wind_speeds = [0, 10.5, 100, 450]
        
        for wind_speed in valid_wind_speeds:
            with self.subTest(wind_speed=wind_speed):
                result = self.validation_service.validate_wind_speed(wind_speed, "imperial")
                self.assertTrue(result, f"Wind speed {wind_speed} should be valid")
    
    def test_validate_wind_speed_invalid(self):
        """Test invalid wind speed validation."""
        invalid_wind_speeds = [-1, 451, float('inf'), float('nan')]
        
        for wind_speed in invalid_wind_speeds:
            with self.subTest(wind_speed=wind_speed):
                result = self.validation_service.validate_wind_speed(wind_speed, "imperial")
                self.assertFalse(result, f"Wind speed {wind_speed} should be invalid")


if __name__ == '__main__':
    unittest.main() 