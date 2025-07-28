"""
Comprehensive unit tests for weather data models.

Tests cover WeatherData, ForecastData, ComprehensiveWeatherData, and SavedCity
with proper validation and edge case handling.
"""

import unittest
from datetime import datetime
from typing import Dict, Any

from core.weather_models import WeatherData, ForecastData, ComprehensiveWeatherData, SavedCity


class TestWeatherData(unittest.TestCase):
    """Test cases for WeatherData model."""
    
    def test_weather_data_creation(self):
        """Test basic WeatherData creation."""
        weather = WeatherData(
            city="Test City",
            temperature=72.5,
            humidity=65,
            weather_main="Clear",
            weather_description="clear sky",
            timestamp=datetime.now().isoformat(),
            units="imperial"
        )
        
        self.assertEqual(weather.city, "Test City")
        self.assertEqual(weather.temperature, 72.5)
        self.assertEqual(weather.humidity, 65)
        self.assertEqual(weather.weather_main, "Clear")
        self.assertEqual(weather.units, "imperial")
    
    def test_weather_data_optional_fields(self):
        """Test WeatherData with optional fields."""
        weather = WeatherData(
            city="Test City",
            temperature=72.5,
            timestamp=datetime.now().isoformat(),
            units="imperial"
        )
        
        self.assertEqual(weather.city, "Test City")
        self.assertEqual(weather.temperature, 72.5)
        self.assertIsNone(weather.humidity)
        self.assertIsNone(weather.weather_main)
    
    def test_weather_data_validation(self):
        """Test WeatherData validation."""
        # Should raise ValueError for missing city
        with self.assertRaises(ValueError):
            WeatherData(
                city="",
                temperature=72.5,
                timestamp=datetime.now().isoformat(),
                units="imperial"
            )
    
    def test_weather_data_to_dict(self):
        """Test WeatherData to_dict method."""
        timestamp = datetime.now().isoformat()
        weather = WeatherData(
            city="Test City",
            temperature=72.5,
            humidity=65,
            weather_main="Clear",
            weather_description="clear sky",
            timestamp=timestamp,
            units="imperial"
        )
        
        data_dict = weather.to_dict()
        
        self.assertEqual(data_dict["city"], "Test City")
        self.assertEqual(data_dict["temperature"], 72.5)
        self.assertEqual(data_dict["humidity"], 65)
        self.assertEqual(data_dict["weather_main"], "Clear")
        self.assertEqual(data_dict["timestamp"], timestamp)
        self.assertEqual(data_dict["units"], "imperial")
    
    def test_weather_data_from_api_response(self):
        """Test WeatherData creation from API response."""
        api_response = {
            "name": "Test City",
            "main": {
                "temp": 72.5,
                "feels_like": 74.0,
                "humidity": 65,
                "pressure": 1013.25
            },
            "weather": [{
                "main": "Clear",
                "description": "clear sky",
                "icon": "01d"
            }],
            "wind": {
                "speed": 10.5,
                "deg": 180
            },
            "visibility": 10000,
            "sys": {
                "country": "US"
            }
        }
        
        weather = WeatherData.from_api_response(api_response, "imperial")
        
        self.assertEqual(weather.city, "Test City")
        self.assertEqual(weather.temperature, 72.5)
        self.assertEqual(weather.feels_like, 74.0)
        self.assertEqual(weather.humidity, 65)
        self.assertEqual(weather.pressure, 1013.25)
        self.assertEqual(weather.weather_main, "Clear")
        self.assertEqual(weather.weather_description, "clear sky")
        self.assertEqual(weather.weather_icon, "01d")
        self.assertEqual(weather.wind_speed, 10.5)
        self.assertEqual(weather.wind_direction, 180)
        self.assertEqual(weather.visibility, 10000)
        self.assertEqual(weather.country, "US")
        self.assertEqual(weather.units, "imperial")


class TestForecastData(unittest.TestCase):
    """Test cases for ForecastData model."""
    
    def test_forecast_data_creation(self):
        """Test basic ForecastData creation."""
        forecast_date = datetime.now()
        forecast = ForecastData(
            city="Test City",
            forecast_date=forecast_date,
            temp_min=65.0,
            temp_max=80.0,
            humidity=70,
            weather_main="Partly Cloudy",
            weather_description="partly cloudy",
            units="imperial"
        )
        
        self.assertEqual(forecast.city, "Test City")
        self.assertEqual(forecast.forecast_date, forecast_date)
        self.assertEqual(forecast.temp_min, 65.0)
        self.assertEqual(forecast.temp_max, 80.0)
        self.assertEqual(forecast.humidity, 70)
        self.assertEqual(forecast.weather_main, "Partly Cloudy")
        self.assertEqual(forecast.units, "imperial")
    
    def test_forecast_data_optional_fields(self):
        """Test ForecastData with optional fields."""
        forecast_date = datetime.now()
        forecast = ForecastData(
            city="Test City",
            forecast_date=forecast_date,
            units="imperial"
        )
        
        self.assertEqual(forecast.city, "Test City")
        self.assertEqual(forecast.forecast_date, forecast_date)
        self.assertIsNone(forecast.temp_min)
        self.assertIsNone(forecast.temp_max)
        self.assertIsNone(forecast.humidity)
    
    def test_forecast_data_validation(self):
        """Test ForecastData validation."""
        # Should raise ValueError for missing city
        with self.assertRaises(ValueError):
            ForecastData(
                city="",
                forecast_date=datetime.now(),
                units="imperial"
            )
        
        # Should raise ValueError for invalid forecast_date
        with self.assertRaises(ValueError):
            ForecastData(
                city="Test City",
                forecast_date="invalid_date",
                units="imperial"
            )
    
    def test_forecast_data_to_dict(self):
        """Test ForecastData to_dict method."""
        forecast_date = datetime.now()
        forecast = ForecastData(
            city="Test City",
            forecast_date=forecast_date,
            temp_min=65.0,
            temp_max=80.0,
            humidity=70,
            weather_main="Partly Cloudy",
            weather_description="partly cloudy",
            units="imperial"
        )
        
        data_dict = forecast.to_dict()
        
        self.assertEqual(data_dict["city"], "Test City")
        self.assertEqual(data_dict["forecast_date"], forecast_date.isoformat())
        self.assertEqual(data_dict["temp_min"], 65.0)
        self.assertEqual(data_dict["temp_max"], 80.0)
        self.assertEqual(data_dict["humidity"], 70)
        self.assertEqual(data_dict["weather_main"], "Partly Cloudy")
        self.assertEqual(data_dict["units"], "imperial")
    
    def test_forecast_data_from_dict(self):
        """Test ForecastData creation from dictionary."""
        forecast_date = datetime.now()
        data_dict = {
            "city": "Test City",
            "forecast_date": forecast_date.isoformat(),
            "temp_min": 65.0,
            "temp_max": 80.0,
            "humidity": 70,
            "weather_main": "Partly Cloudy",
            "weather_description": "partly cloudy",
            "units": "imperial"
        }
        
        forecast = ForecastData.from_dict(data_dict)
        
        self.assertEqual(forecast.city, "Test City")
        self.assertEqual(forecast.forecast_date, forecast_date)
        self.assertEqual(forecast.temp_min, 65.0)
        self.assertEqual(forecast.temp_max, 80.0)
        self.assertEqual(forecast.humidity, 70)
        self.assertEqual(forecast.weather_main, "Partly Cloudy")
        self.assertEqual(forecast.units, "imperial")


class TestComprehensiveWeatherData(unittest.TestCase):
    """Test cases for ComprehensiveWeatherData model."""
    
    def test_comprehensive_weather_data_creation(self):
        """Test basic ComprehensiveWeatherData creation."""
        current_weather = WeatherData(
            city="Test City",
            temperature=72.5,
            timestamp=datetime.now().isoformat(),
            units="imperial"
        )
        
        forecast_date = datetime.now()
        forecast = ForecastData(
            city="Test City",
            forecast_date=forecast_date,
            temp_min=65.0,
            temp_max=80.0,
            units="imperial"
        )
        
        comprehensive = ComprehensiveWeatherData(
            current=current_weather,
            forecast=[forecast],
            location={"name": "Test City", "lat": 40.7128, "lon": -74.0060},
            api_source="openweathermap"
        )
        
        self.assertEqual(comprehensive.current, current_weather)
        self.assertEqual(len(comprehensive.forecast), 1)
        self.assertEqual(comprehensive.forecast[0], forecast)
        self.assertEqual(comprehensive.location["name"], "Test City")
        self.assertEqual(comprehensive.api_source, "openweathermap")
    
    def test_comprehensive_weather_data_to_dict(self):
        """Test ComprehensiveWeatherData to_dict method."""
        current_weather = WeatherData(
            city="Test City",
            temperature=72.5,
            timestamp=datetime.now().isoformat(),
            units="imperial"
        )
        
        forecast_date = datetime.now()
        forecast = ForecastData(
            city="Test City",
            forecast_date=forecast_date,
            temp_min=65.0,
            temp_max=80.0,
            units="imperial"
        )
        
        comprehensive = ComprehensiveWeatherData(
            current=current_weather,
            forecast=[forecast],
            location={"name": "Test City", "lat": 40.7128, "lon": -74.0060},
            api_source="openweathermap"
        )
        
        data_dict = comprehensive.to_dict()
        
        self.assertIn("current", data_dict)
        self.assertIn("forecast", data_dict)
        self.assertIn("location", data_dict)
        self.assertEqual(data_dict["api_source"], "openweathermap")
        self.assertEqual(len(data_dict["forecast"]), 1)


class TestSavedCity(unittest.TestCase):
    """Test cases for SavedCity model."""
    
    def test_saved_city_creation(self):
        """Test basic SavedCity creation."""
        saved_city = SavedCity(
            city="Test City",
            state="CA",
            nickname="Test Nickname"
        )
        
        self.assertEqual(saved_city.city, "Test City")
        self.assertEqual(saved_city.state, "CA")
        self.assertEqual(saved_city.nickname, "Test Nickname")
    
    def test_saved_city_optional_fields(self):
        """Test SavedCity with optional fields."""
        saved_city = SavedCity(
            city="Test City"
        )
        
        self.assertEqual(saved_city.city, "Test City")
        self.assertIsNone(saved_city.state)
        self.assertIsNone(saved_city.nickname)
    
    def test_saved_city_validation(self):
        """Test SavedCity validation."""
        # Should raise ValueError for missing city
        with self.assertRaises(ValueError):
            SavedCity(city="")
    
    def test_saved_city_to_dict(self):
        """Test SavedCity to_dict method."""
        saved_city = SavedCity(
            city="Test City",
            state="CA",
            nickname="Test Nickname"
        )
        
        data_dict = saved_city.to_dict()
        
        self.assertEqual(data_dict["city"], "Test City")
        self.assertEqual(data_dict["state"], "CA")
        self.assertEqual(data_dict["nickname"], "Test Nickname")
    
    def test_saved_city_from_dict(self):
        """Test SavedCity creation from dictionary."""
        data_dict = {
            "city": "Test City",
            "state": "CA",
            "nickname": "Test Nickname"
        }
        
        saved_city = SavedCity.from_dict(data_dict)
        
        self.assertEqual(saved_city.city, "Test City")
        self.assertEqual(saved_city.state, "CA")
        self.assertEqual(saved_city.nickname, "Test Nickname")
    
    def test_saved_city_display_name(self):
        """Test SavedCity display name logic."""
        # With nickname
        saved_city = SavedCity(
            city="Test City",
            state="CA",
            nickname="Test Nickname"
        )
        self.assertEqual(saved_city.display_name, "Test Nickname")
        
        # Without nickname, with state
        saved_city = SavedCity(
            city="Test City",
            state="CA"
        )
        self.assertEqual(saved_city.display_name, "Test City, CA")
        
        # Without nickname, without state
        saved_city = SavedCity(
            city="Test City"
        )
        self.assertEqual(saved_city.display_name, "Test City")


if __name__ == '__main__':
    unittest.main() 