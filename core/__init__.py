# core/__init__.py
# """Core functionality for Weather Dashboard"""

from .api import WeatherAPI
# from .storage import StorageManager
from .data_handler import WeatherDataHandler
from .utils import UserSettingsManager

__all__ = ['WeatherAPI', 'WeatherDataHandler', 'UserSettingsManager']

# Snoops example of how to use the core components
# __all__ = ['WeatherAPI', 'StorageManager', 'DataProcessor']