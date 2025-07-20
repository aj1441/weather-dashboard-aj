"""
Weather conversion service following Python best practices.

This service provides pure functions for converting weather data (current and forecast) 
between temperature units without mutating the original data.
"""

from typing import List, Dict, Any, Optional
import copy
from .conversion_utils import convert_to_celsius, convert_to_fahrenheit


class WeatherConversionService:
    """
    Service for converting weather data (current and forecast) between temperature units.
    
    Uses pure functions that don't mutate input data, following functional programming
    principles for predictable, testable code.
    """
    
    @staticmethod
    def convert_forecast_data(forecast_data: List[Dict[str, Any]], 
                            from_unit: str, 
                            to_unit: str) -> List[Dict[str, Any]]:
        """
        Convert forecast data from one unit to another.
        
        Args:
            forecast_data: List of forecast day dictionaries
            from_unit: Source unit ('imperial' or 'metric')
            to_unit: Target unit ('imperial' or 'metric')
            
        Returns:
            New list with converted temperatures (original data unchanged)
        """
        if from_unit == to_unit:
            # Return deep copy to maintain immutability contract
            return copy.deepcopy(forecast_data)
        
        if not forecast_data or not isinstance(forecast_data, list):
            return []
        
        # Create new converted data without modifying original
        converted_data = []
        
        for day_data in forecast_data:
            converted_day = copy.deepcopy(day_data)
            
            # Convert temperature fields
            temp_fields = ['temp_min', 'temp_max', 'temp_day', 'temp_night']
            for field in temp_fields:
                if field in converted_day and converted_day[field] is not None:
                    converted_day[field] = WeatherConversionService._convert_temperature(
                        converted_day[field], from_unit, to_unit
                    )
            
            # Update unit label
            converted_day['unit'] = '°C' if to_unit == 'metric' else '°F'
            
            converted_data.append(converted_day)
        
        return converted_data
    
    @staticmethod
    def _convert_temperature(temp: float, from_unit: str, to_unit: str) -> float:
        """
        Convert a single temperature value between units.
        
        Args:
            temp: Temperature value to convert
            from_unit: Source unit ('imperial' or 'metric')
            to_unit: Target unit ('imperial' or 'metric')
            
        Returns:
            Converted temperature value
        """
        if from_unit == to_unit:
            return temp
        
        if from_unit == 'imperial' and to_unit == 'metric':
            return convert_to_celsius(temp)
        elif from_unit == 'metric' and to_unit == 'imperial':
            return convert_to_fahrenheit(temp)
        else:
            raise ValueError(f"Invalid unit conversion: {from_unit} -> {to_unit}")
    
    @staticmethod
    def get_unit_label(unit: str) -> str:
        """
        Get display label for temperature unit.
        
        Args:
            unit: Unit string ('imperial' or 'metric')
            
        Returns:
            Display label ('°F' or '°C')
        """
        return '°C' if unit == 'metric' else '°F'
    
    @staticmethod
    def convert_current_weather_data(weather_data: Dict[str, Any], 
                                   from_unit: str, 
                                   to_unit: str) -> Dict[str, Any]:
        """
        Convert current weather data from one unit to another.
        
        Args:
            weather_data: Current weather data dictionary
            from_unit: Source unit ('imperial' or 'metric')
            to_unit: Target unit ('imperial' or 'metric')
            
        Returns:
            New dictionary with converted temperatures (original data unchanged)
        """
        if from_unit == to_unit:
            return copy.deepcopy(weather_data)
        
        if not weather_data or not isinstance(weather_data, dict):
            return {}
        
        # Create new converted data without modifying original
        converted = copy.deepcopy(weather_data)
        
        # Handle both flat and nested (with 'current') data structures
        # Flat: {'temperature': ..., 'feels_like': ...}
        # Nested: {'current': {...}, 'forecast': [...]}
        if 'current' in converted:
            current = converted['current']
            # Convert nested current weather data
            temp_fields = ['temp', 'feels_like']
            for field in temp_fields:
                if field in current and current[field] is not None:
                    current[field] = WeatherConversionService._convert_temperature(
                        current[field], from_unit, to_unit
                    )
            current['unit'] = WeatherConversionService.get_unit_label(to_unit)
        else:
            # Convert flat structure
            temp_fields = ['temperature', 'feels_like']
            for field in temp_fields:
                if field in converted and converted[field] is not None:
                    converted[field] = WeatherConversionService._convert_temperature(
                        converted[field], from_unit, to_unit
                    )
            converted['unit'] = WeatherConversionService.get_unit_label(to_unit)
        
        # Convert forecast data if present (for comprehensive weather objects)
        if 'forecast' in converted and isinstance(converted['forecast'], list):
            converted['forecast'] = WeatherConversionService.convert_forecast_data(
                converted['forecast'], from_unit, to_unit
            )
        
        return converted


class ForecastCache:
    """
    Simple, immutable forecast cache that maintains original data integrity.
    
    Stores forecast data in its original unit and provides converted copies
    without mutating the original data.
    """
    
    def __init__(self):
        self._original_data: Optional[List[Dict[str, Any]]] = None
        self._original_unit: Optional[str] = None
    
    def store(self, forecast_data: List[Dict[str, Any]], unit: str) -> None:
        """
        Store forecast data in the cache.
        
        Args:
            forecast_data: Forecast data to cache
            unit: Unit of the forecast data ('imperial' or 'metric')
        """
        self._original_data = copy.deepcopy(forecast_data) if forecast_data else None
        self._original_unit = unit
    
    def get_converted(self, target_unit: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get forecast data converted to the target unit.
        
        Args:
            target_unit: Desired unit ('imperial' or 'metric')
            
        Returns:
            Converted forecast data, or None if no data cached
        """
        if not self._original_data or not self._original_unit:
            return None
        
        return WeatherConversionService.convert_forecast_data(
            self._original_data, self._original_unit, target_unit
        )
    
    def has_data(self) -> bool:
        """Check if cache contains data."""
        return self._original_data is not None
    
    def clear(self) -> None:
        """Clear the cache."""
        self._original_data = None
        self._original_unit = None