"""
Data service for handling data persistence and retrieval operations.

This service encapsulates database operations and provides a clean
interface for data storage and retrieval.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from config import Config
from core.data_handler import WeatherDataHandler
from core.weather_models import WeatherData, ForecastData, SavedCity


class DataService:
    """
    Service for data persistence and retrieval operations.
    
    This service provides a clean interface for all data storage and
    retrieval operations, including weather data, saved cities, and
    historical information. It encapsulates database operations and
    provides consistent error handling.
    
    Attributes:
        config: Application configuration object
        logger: Logger instance for this service
        data_handler: Weather data handler instance for database operations
    """
    
    def __init__(self, config: Config) -> None:
        """
        Initialize the data service with configuration.
        
        Args:
            config: Application configuration containing database settings
                   and other operational parameters
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.data_handler = WeatherDataHandler(config)
    
    def save_weather_data(self, weather_data: WeatherData) -> bool:
        """
        Save weather data to storage.
        
        This method converts a WeatherData object to dictionary format
        and saves it to the database using the data handler. It provides
        detailed logging for success and failure cases.
        
        Args:
            weather_data: WeatherData object containing current weather
                         information to be saved
            
        Returns:
            True if the data was successfully saved, False if the operation
            failed due to database errors or validation issues
            
        Raises:
            No exceptions are raised - all errors are logged and False is returned
            
        Example:
            >>> service = DataService(config)
            >>> weather = WeatherData(city="New York", temperature=72.5)
            >>> success = service.save_weather_data(weather)
            >>> if success:
            ...     print("Weather data saved successfully")
        """
        try:
            # Convert to dictionary format for storage
            data_dict = weather_data.to_dict()
            
            # Save using data handler
            success = self.data_handler.save_weather_data_validated(data_dict)
            
            if success:
                self.logger.info(f"Successfully saved weather data for {weather_data.city}")
            else:
                self.logger.error(f"Failed to save weather data for {weather_data.city}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving weather data: {e}")
            return False
    
    def save_forecast_data(self, city: str, state: Optional[str], forecast_data: List[ForecastData]) -> bool:
        """
        Save forecast data to storage.
        
        Args:
            city: City name
            state: State abbreviation (optional)
            forecast_data: List of ForecastData objects
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert forecast data to dictionary format
            forecast_dicts = []
            for forecast in forecast_data:
                forecast_dict = forecast.to_dict()
                # Convert datetime to timestamp for storage
                if forecast_dict.get('forecast_date'):
                    forecast_dict['dt'] = forecast.forecast_date.timestamp()
                forecast_dicts.append(forecast_dict)
            
            # Save using data handler
            success = self.data_handler.save_forecast_data(city, state, forecast_dicts)
            
            if success:
                self.logger.info(f"Successfully saved forecast data for {city}")
            else:
                self.logger.error(f"Failed to save forecast data for {city}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving forecast data: {e}")
            return False
    
    def save_city(self, city: str, state: Optional[str] = None, nickname: Optional[str] = None) -> bool:
        """
        Save a city to favorites.
        
        Args:
            city: City name
            state: State abbreviation (optional)
            nickname: Custom nickname for the city (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create SavedCity object
            saved_city = SavedCity(
                city=city,
                state=state,
                nickname=nickname
            )
            
            # Convert to dictionary for storage
            city_data = saved_city.to_dict()
            
            # Save using data handler
            success = self.data_handler.save_city(city_data)
            
            if success:
                self.logger.info(f"Successfully saved city: {city}")
            else:
                self.logger.error(f"Failed to save city: {city}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving city: {e}")
            return False
    
    def get_saved_cities(self) -> List[SavedCity]:
        """
        Get list of saved cities.
        
        Returns:
            List of SavedCity objects
        """
        try:
            # Get saved cities from data handler
            cities_data = self.data_handler.load_saved_cities()
            
            # Convert to SavedCity objects
            saved_cities = []
            for city_data in cities_data:
                try:
                    saved_city = SavedCity.from_dict(city_data)
                    saved_cities.append(saved_city)
                except Exception as e:
                    self.logger.warning(f"Error parsing saved city data: {e}")
                    continue
            
            self.logger.info(f"Retrieved {len(saved_cities)} saved cities")
            return saved_cities
            
        except Exception as e:
            self.logger.error(f"Error getting saved cities: {e}")
            return []
    
    def delete_city(self, city: str, state: Optional[str] = None) -> bool:
        """
        Delete a saved city.
        
        Args:
            city: City name
            state: State abbreviation (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.data_handler.delete_city(city, state)
            
            if success:
                self.logger.info(f"Successfully deleted city: {city}")
            else:
                self.logger.error(f"Failed to delete city: {city}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error deleting city: {e}")
            return False
    
    def get_weather_history(self, city: str, state: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get weather history for a city.
        
        Args:
            city: City name
            state: State abbreviation (optional)
            days: Number of days to retrieve
            
        Returns:
            List of weather history records
        """
        try:
            history = self.data_handler.get_forecast_data(city, state, days)
            self.logger.info(f"Retrieved {len(history)} weather history records for {city}")
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting weather history: {e}")
            return []
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """
        Clean up old weather data.
        
        Args:
            days_to_keep: Number of days of data to keep
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.data_handler.cleanup_old_forecast_data(days_to_keep)
            
            if success:
                self.logger.info(f"Successfully cleaned up old weather data (keeping {days_to_keep} days)")
            else:
                self.logger.error("Failed to clean up old weather data")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
            return False 