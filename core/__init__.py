# core/__init__.py
# """Core functionality for Weather Dashboard"""

# Make imports conditional to avoid dependency issues
try:
    from .weather.api import WeatherAPI
except ImportError:
    WeatherAPI = None

try:
    from .database.data_handler import WeatherDataHandler
except ImportError:
    WeatherDataHandler = None

try:
    from .location.location_service import LocationService
except ImportError:
    LocationService = None

try:
    from .weather.historical_coordinator import HistoricalDataCoordinator
except ImportError:
    HistoricalDataCoordinator = None

__all__ = []

# Snoops example of how to use the core components
# __all__ = ['WeatherAPI', 'StorageManager', 'DataProcessor']