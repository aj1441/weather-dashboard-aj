# core/__init__.py
# """Core functionality for Weather Dashboard"""

from .weather.api import WeatherAPI
from .database.data_handler import WeatherDataHandler
from .location.location_service import LocationService
from .weather.historical_coordinator import HistoricalDataCoordinator
__all__ = []

# Snoops example of how to use the core components
# __all__ = ['WeatherAPI', 'StorageManager', 'DataProcessor']