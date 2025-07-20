# core/__init__.py
# """Core functionality for Weather Dashboard"""

from .api import WeatherAPI
# from .storage import StorageManager
from .data_handler import WeatherDataHandler
from .icon_manager import IconManager
from .historical_coordinator import HistoricalDataCoordinator
from .location_service import LocationService
__all__ = []

# Snoops example of how to use the core components
# __all__ = ['WeatherAPI', 'StorageManager', 'DataProcessor']