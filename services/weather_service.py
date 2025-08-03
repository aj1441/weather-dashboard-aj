"""
Weather service for handling weather-related business logic.

This service encapsulates weather API operations, data processing,
and provides a clean interface for weather-related functionality.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import Config
from core.weather.api import WeatherAPI
from core.weather.weather_models import WeatherData, ForecastData, ComprehensiveWeatherData
from core.weather.data_validator import WeatherDataValidator


class WeatherService:
    """
    Service for weather-related operations and business logic.
    
    This service provides a clean interface for weather API operations,
    data processing, and validation. It encapsulates the complexity
    of weather data retrieval and ensures consistent error handling.
    
    Attributes:
        config: Application configuration object
        logger: Logger instance for this service
        api: Weather API client instance
        validator: Weather data validator instance
    """
    
    def __init__(self, config: Config) -> None:
        """
        Initialize the weather service with configuration.
        
        Args:
            config: Application configuration containing API settings,
                   timeout values, and other operational parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api = WeatherAPI(config)
        self.validator = WeatherDataValidator(temperature_unit=config.units)
    
    def get_current_weather(self, city: str, state: Optional[str] = None, units: Optional[str] = None) -> Optional[WeatherData]:
        """
        Get current weather for a location.
        
        This method fetches current weather data from the weather API,
        validates the response, and returns a structured WeatherData object.
        It handles API errors gracefully and provides detailed logging.
        
        Args:
            city: City name to get weather for (required)
            state: State abbreviation for disambiguation (optional)
            units: Temperature units ('imperial', 'metric', 'kelvin').
                   Uses config default if not provided
            
        Returns:
            WeatherData object with current weather information, or None if
            the request failed due to API errors, validation failures, or
            network issues
            
        Raises:
            No exceptions are raised - all errors are logged and None is returned
            
        Example:
            >>> service = WeatherService(config)
            >>> weather = service.get_current_weather("New York", "NY")
            >>> if weather:
            ...     print(f"Temperature: {weather.temperature}°F")
        """
        try:
            if units is None:
                units = self.config.units
            
            # Get weather data from API
            weather_data = self.api.fetch_weather(city)
            if not weather_data or "error" in weather_data:
                self.logger.error(f"Failed to fetch weather for {city}: {weather_data}")
                return None
            
            # Convert to WeatherData model
            weather = WeatherData.from_api_response(weather_data, units)
            
            # Validate the data
            if not self.validator.validate_weather_data(weather.to_dict()):
                self.logger.warning(f"Weather data validation failed for {city}")
                return None
            
            self.logger.info(f"Successfully retrieved weather for {city}")
            return weather
            
        except Exception as e:
            self.logger.error(f"Error getting current weather for {city}: {e}")
            return None
    
    def get_comprehensive_weather(self, city: str, state: Optional[str] = None, units: Optional[str] = None) -> Optional[ComprehensiveWeatherData]:
        """
        Get comprehensive weather data including current conditions and forecast.
        
        This method fetches both current weather and forecast data from the API,
        processes the response into structured data models, and validates the
        results. It provides a complete weather picture for a location.
        
        Args:
            city: City name to get weather for (required)
            state: State abbreviation for disambiguation (optional)
            units: Temperature units ('imperial', 'metric', 'kelvin').
                   Uses config default if not provided
            
        Returns:
            ComprehensiveWeatherData object containing current weather and
            forecast information, or None if the request failed
            
        Raises:
            No exceptions are raised - all errors are logged and None is returned
            
        Example:
            >>> service = WeatherService(config)
            >>> weather = service.get_comprehensive_weather("Los Angeles", "CA")
            >>> if weather:
            ...     print(f"Current: {weather.current.temperature}°F")
            ...     print(f"Forecast days: {len(weather.forecast)}")
        """
        try:
            if units is None:
                units = self.config.units
            
            # Get comprehensive data from API
            comprehensive_data = self.api.fetch_comprehensive_weather(city, state, units)
            if not comprehensive_data or "error" in comprehensive_data:
                self.logger.error(f"Failed to fetch comprehensive weather for {city}: {comprehensive_data}")
                return None
            
            # Extract current weather
            current_data = comprehensive_data.get('current', {})
            location_data = comprehensive_data.get('location', {})
            
            # Create WeatherData object
            current_weather = WeatherData(
                city=location_data.get('name', city),
                state=location_data.get('state', state),
                country=location_data.get('country', 'US'),
                latitude=location_data.get('lat'),
                longitude=location_data.get('lon'),
                temperature=current_data.get('temp'),
                feels_like=current_data.get('feels_like'),
                humidity=current_data.get('humidity'),
                pressure=current_data.get('pressure'),
                weather_main=current_data.get('main'),
                weather_description=current_data.get('description'),
                weather_icon=current_data.get('icon'),
                wind_speed=current_data.get('wind_speed'),
                wind_direction=current_data.get('wind_deg'),
                visibility=current_data.get('visibility'),
                uv_index=current_data.get('uv_index'),
                timestamp=datetime.now().isoformat(),
                api_source='openweathermap',
                units=units
            )
            
            # Process forecast data
            forecast_list = []
            for day_data in comprehensive_data.get('forecast', []):
                forecast = ForecastData(
                    city=location_data.get('name', city),
                    state=location_data.get('state', state),
                    country=location_data.get('country', 'US'),
                    forecast_date=datetime.fromisoformat(day_data.get('dt', datetime.now().isoformat())),
                    temp_min=day_data.get('temp_min'),
                    temp_max=day_data.get('temp_max'),
                    temp_day=day_data.get('temp_day'),
                    temp_night=day_data.get('temp_night'),
                    humidity=day_data.get('humidity'),
                    pressure=day_data.get('pressure'),
                    wind_speed=day_data.get('wind_speed'),
                    weather_main=day_data.get('main'),
                    weather_description=day_data.get('description'),
                    weather_icon=day_data.get('icon'),
                    precipitation_probability=day_data.get('pop'),
                    precipitation_amount=day_data.get('precipitation_amount'),
                    created_timestamp=datetime.now(),
                    api_data=day_data,
                    units=units
                )
                forecast_list.append(forecast)
            
            # Create comprehensive weather data
            comprehensive_weather = ComprehensiveWeatherData(
                current=current_weather,
                forecast=forecast_list,
                location=location_data,
                api_source=comprehensive_data.get('api_source', 'unknown')
            )
            
            self.logger.info(f"Successfully retrieved comprehensive weather for {city}")
            return comprehensive_weather
            
        except Exception as e:
            self.logger.error(f"Error getting comprehensive weather for {city}: {e}")
            return None
    
    def get_coordinates(self, city: str, state: Optional[str] = None) -> Optional[Dict[str, float]]:
        """
        Get coordinates for a city.
        
        Args:
            city: City name
            state: State abbreviation (optional)
            
        Returns:
            Dictionary with 'lat' and 'lon' keys or None if failed
        """
        try:
            coords = self.api.get_coordinates(city, state)
            if "error" in coords:
                self.logger.error(f"Failed to get coordinates for {city}: {coords}")
                return None
            
            return coords
            
        except Exception as e:
            self.logger.error(f"Error getting coordinates for {city}: {e}")
            return None
    
    def validate_weather_data(self, weather_data: Dict[str, Any]) -> bool:
        """
        Validate weather data using the validator.
        
        Args:
            weather_data: Weather data dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        return self.validator.validate_weather_data(weather_data)
    
    def clean_weather_data(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Clean and validate raw weather data.
        
        Args:
            raw_data: Raw weather data from API
            
        Returns:
            Cleaned weather data or None if validation fails
        """
        return self.validator.validate_and_clean_current_weather(raw_data) 