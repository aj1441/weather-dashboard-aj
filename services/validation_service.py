"""
Validation service for handling data validation operations.

This service encapsulates validation logic and provides a clean
interface for data validation functionality.
"""

import logging
from typing import Dict, Optional, Any

from config import Config
from core.data_validator import WeatherDataValidator, ValidationRules


class ValidationService:
    """Service for data validation operations."""
    
    def __init__(self, config: Config):
        """Initialize the validation service with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.validator = WeatherDataValidator(temperature_unit=config.units)
    
    def validate_weather_data(self, weather_data: Dict[str, Any]) -> bool:
        """
        Validate weather data.
        
        Args:
            weather_data: Weather data dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            is_valid = self.validator.validate_weather_data(weather_data)
            
            if is_valid:
                self.logger.debug("Weather data validation passed")
            else:
                self.logger.warning("Weather data validation failed")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Error validating weather data: {e}")
            return False
    
    def clean_weather_data(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Clean and validate raw weather data.
        
        Args:
            raw_data: Raw weather data from API
            
        Returns:
            Cleaned weather data or None if validation fails
        """
        try:
            cleaned_data = self.validator.validate_and_clean_current_weather(raw_data)
            
            if cleaned_data:
                self.logger.debug("Weather data cleaned successfully")
            else:
                self.logger.warning("Weather data cleaning failed")
            
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"Error cleaning weather data: {e}")
            return None
    
    def validate_city_name(self, city: str) -> bool:
        """
        Validate city name.
        
        Args:
            city: City name to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not city or not isinstance(city, str):
            return False
        
        # Remove whitespace and check length
        city_clean = city.strip()
        if len(city_clean) < 1 or len(city_clean) > 100:
            return False
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        import re
        if not re.match(r"^[a-zA-Z\s\-']+$", city_clean):
            return False
        
        return True
    
    def validate_state_code(self, state: str) -> bool:
        """
        Validate state code.
        
        Args:
            state: State code to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not state:
            return True  # State is optional
        
        if not isinstance(state, str):
            return False
        
        # Remove whitespace and convert to uppercase
        state_clean = state.strip().upper()
        
        # Check length
        if len(state_clean) != 2:
            return False
        
        # Check for valid characters (letters only)
        if not state_clean.isalpha():
            return False
        
        return True
    
    def validate_temperature(self, temperature: float, units: str = "imperial") -> bool:
        """
        Validate temperature value.
        
        Args:
            temperature: Temperature value to validate
            units: Temperature units ('imperial', 'metric', 'kelvin')
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(temperature, (int, float)):
            return False
        
        # Check for NaN or infinity
        if temperature != temperature or temperature == float('inf') or temperature == float('-inf'):
            return False
        
        # Check reasonable ranges based on units
        if units == "imperial":
            return -100 <= temperature <= 150
        elif units == "metric":
            return -73 <= temperature <= 66
        elif units == "kelvin":
            return 173 <= temperature <= 339
        else:
            return False
    
    def validate_humidity(self, humidity: int) -> bool:
        """
        Validate humidity value.
        
        Args:
            humidity: Humidity percentage to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(humidity, int):
            return False
        
        return 0 <= humidity <= 100
    
    def validate_pressure(self, pressure: float) -> bool:
        """
        Validate pressure value.
        
        Args:
            pressure: Pressure in hPa to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(pressure, (int, float)):
            return False
        
        # Check for NaN or infinity
        if pressure != pressure or pressure == float('inf') or pressure == float('-inf'):
            return False
        
        return 800 <= pressure <= 1200
    
    def validate_wind_speed(self, wind_speed: float, units: str = "imperial") -> bool:
        """
        Validate wind speed value.
        
        Args:
            wind_speed: Wind speed to validate
            units: Speed units ('imperial' for mph, 'metric' for m/s)
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(wind_speed, (int, float)):
            return False
        
        # Check for NaN or infinity
        if wind_speed != wind_speed or wind_speed == float('inf') or wind_speed == float('-inf'):
            return False
        
        # Check for negative values
        if wind_speed < 0:
            return False
        
        # Check reasonable ranges based on units
        if units == "imperial":
            return wind_speed <= 450  # mph
        else:
            return wind_speed <= 200  # m/s
    
    def get_validation_rules(self) -> ValidationRules:
        """
        Get current validation rules.
        
        Returns:
            ValidationRules object
        """
        return self.validator.rules
    
    def update_validation_rules(self, rules: ValidationRules) -> None:
        """
        Update validation rules.
        
        Args:
            rules: New validation rules
        """
        self.validator.rules = rules
        self.logger.info("Validation rules updated") 