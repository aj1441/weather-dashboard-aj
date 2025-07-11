"""OpenMeteo API client module for weather data fallback"""

import requests
import logging
from datetime import datetime
from typing import Dict, Optional

class OpenMeteoClient:
    """Client for the OpenMeteo API service"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # OpenMeteo weather code mappings
        self.weather_codes = {
            0: {'main': 'Clear', 'description': 'Clear sky', 'icon': '01d'},
            1: {'main': 'Partly Cloudy', 'description': 'Partly cloudy', 'icon': '02d'},
            2: {'main': 'Cloudy', 'description': 'Cloudy', 'icon': '03d'},
            3: {'main': 'Overcast', 'description': 'Overcast', 'icon': '04d'},
            45: {'main': 'Foggy', 'description': 'Foggy', 'icon': '50d'},
            48: {'main': 'Foggy', 'description': 'Depositing rime fog', 'icon': '50d'},
            51: {'main': 'Drizzle', 'description': 'Light drizzle', 'icon': '09d'},
            53: {'main': 'Drizzle', 'description': 'Moderate drizzle', 'icon': '09d'},
            55: {'main': 'Drizzle', 'description': 'Heavy drizzle', 'icon': '09d'},
            61: {'main': 'Rain', 'description': 'Light rain', 'icon': '10d'},
            63: {'main': 'Rain', 'description': 'Moderate rain', 'icon': '10d'},
            65: {'main': 'Rain', 'description': 'Heavy rain', 'icon': '10d'},
            71: {'main': 'Snow', 'description': 'Light snow', 'icon': '13d'},
            73: {'main': 'Snow', 'description': 'Moderate snow', 'icon': '13d'},
            75: {'main': 'Snow', 'description': 'Heavy snow', 'icon': '13d'},
            77: {'main': 'Snow', 'description': 'Snow grains', 'icon': '13d'},
            80: {'main': 'Rain', 'description': 'Light rain showers', 'icon': '10d'},
            81: {'main': 'Rain', 'description': 'Moderate rain showers', 'icon': '10d'},
            82: {'main': 'Rain', 'description': 'Heavy rain showers', 'icon': '10d'},
            85: {'main': 'Snow', 'description': 'Light snow showers', 'icon': '13d'},
            86: {'main': 'Snow', 'description': 'Heavy snow showers', 'icon': '13d'},
            95: {'main': 'Thunderstorm', 'description': 'Thunderstorm', 'icon': '11d'},
            96: {'main': 'Thunderstorm', 'description': 'Thunderstorm with hail', 'icon': '11d'},
            99: {'main': 'Thunderstorm', 'description': 'Thunderstorm with heavy hail', 'icon': '11d'}
        }

    def fetch_weather(self, lat: float, lon: float, units: str = "metric") -> Optional[Dict]:
        """
        Fetch current weather data from OpenMeteo API
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            units: Temperature units ('imperial' or 'metric')
            
        Returns:
            Dictionary with weather data or error dictionary
        """
        self.logger.info("Fetching weather data from OpenMeteo API")
        
        # OpenMeteo uses metric by default, fahrenheit needs to be specified
        temperature_unit = "fahrenheit" if units == "imperial" else "celsius"
        
        try:
            # Current Weather API endpoint
            current_url = "https://api.open-meteo.com/v1/forecast"
            params = {
                'latitude': lat,
                'longitude': lon,
                'current': ['temperature_2m', 'relative_humidity_2m', 'apparent_temperature',
                           'weather_code', 'pressure_msl', 'wind_speed_10m', 'wind_direction_10m'],
                'temperature_unit': temperature_unit,
                'wind_speed_unit': 'mph' if units == 'imperial' else 'kmh',
                'timezone': 'auto'
            }
            
            response = requests.get(current_url, params=params, timeout=self.timeout)
            if response.status_code != 200:
                return {"error": f"OpenMeteo API error: {response.status_code}"}
                
            data = response.json()
            
            if 'error' in data:
                return {"error": f"OpenMeteo API error: {data['error']}"}
                
            current = data.get('current', {})
            weather_code = current.get('weather_code')
            weather_info = self.weather_codes.get(weather_code, 
                {'main': 'Unknown', 'description': 'Unknown weather', 'icon': '01d'})
            
            # Format the response to match our expected structure
            weather_data = {
                'temperature': current.get('temperature_2m'),
                'feels_like': current.get('apparent_temperature'),
                'humidity': current.get('relative_humidity_2m'),
                'pressure': current.get('pressure_msl'),
                'weather_main': weather_info['main'],
                'weather_description': weather_info['description'],
                'weather_icon': weather_info['icon'],
                'wind_speed': current.get('wind_speed_10m'),
                'wind_direction': current.get('wind_direction_10m'),
                'visibility': None,  # Not provided by OpenMeteo free API
                'api_source': 'open_meteo'
            }
            
            self.logger.info("Successfully fetched weather data from OpenMeteo")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"OpenMeteo API request failed: {str(e)}")
            return {"error": f"OpenMeteo request failed: {str(e)}"}
        except Exception as e:
            self.logger.error(f"Error processing OpenMeteo data: {str(e)}")
            return {"error": f"Error processing OpenMeteo data: {str(e)}"}

    def fetch_forecast(self, lat: float, lon: float, units: str = "metric", days: int = 7) -> Optional[Dict]:
        """
        Fetch forecast data from OpenMeteo API
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            units: Temperature units ('imperial' or 'metric')
            days: Number of forecast days to fetch
            
        Returns:
            Dictionary with forecast data or error dictionary
        """
        # Implementation of forecast fetching can be added here
        # Similar to fetch_weather but using different OpenMeteo API parameters
        pass
