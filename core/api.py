"""Weather API client module"""

import requests
from typing import Dict, Optional
from config import API_KEY, UNITS, BASE_URL

class WeatherAPI:
    """Handles all weather API communications"""
    
    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.base_url = BASE_URL
        self.timeout = 10
        self.units = UNITS
    
    def fetch_weather_data(self, city: str, state: str, units: str = None) -> Optional[Dict]:
        """
        Fetch weather data for a city and state (OpenWeatherMap API)
        
        Args:
            city: Name of the city
            state: State abbreviation
            units: Temperature units (uses class default if not provided)
            
        Returns:
            Dictionary with weather data or error dictionary
        """
        if units is None:
            units = self.units
            
        try:
            url = f"{self.base_url}?q={city},{state},US&appid={self.api_key}&units={units}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
    
    def fetch_weather(self, city: str) -> Optional[Dict]:
        """
        Fetch weather data for a city (WeatherAPI.com format)
        
        Args:
            city: Name of the city
            
        Returns:
            Dictionary with weather data or error dictionary
        """
        url = f"https://api.weatherapi.com/v1/current.json?key=demo&q={city}"

        try:
            response = requests.get(url)

            # check if city is not found
            if response.status_code == 404:
                return {"error": "City not found"}

            data = response.json()
            temp_k = data.get("current", {}).get("temp_k")

            if temp_k is None:
                return {"error": "No weather data"}

            description = data.get("current", {}).get("condition", {}).get("text", "No description")
            temp_c = round(temp_k - 273.15, 1)

            return {
                "city": city,
                "temp_c": temp_c,
                "description": description
            }

        except requests.exceptions.RequestException:
            return {"error": "Network error"}
        except Exception:
            return {"error": "Something went wrong"}

# Legacy function for backward compatibility
def fetch_weather_data(city, state, units=UNITS):
    """Legacy function - wraps the new class-based approach"""
    api = WeatherAPI()
    return api.fetch_weather_data(city, state, units)

# Legacy function for backward compatibility  
def fetch_weather(city):
    """Legacy function - wraps the new class-based approach"""
    api = WeatherAPI()
    return api.fetch_weather(city)
