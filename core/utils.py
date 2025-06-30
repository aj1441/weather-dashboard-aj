"""Utility functions and classes for the weather dashboard"""

from datetime import datetime
import json
import os
from typing import Dict, Optional

class UserSettingsManager:
    """Handles all user settings and preferences"""
    
    def __init__(self, settings_file: str = "data/user_settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            "theme": "vapor",
            "default_location": "",
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "pressure_unit": "hPa"
        }
        self._ensure_data_directory()
    
    def _ensure_data_directory(self) -> None:
        """Create data directory if it doesn't exist"""
        data_dir = os.path.dirname(self.settings_file)
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)
    
    def load_user_theme(self, default: str = "vapor") -> str:
        """
        Load saved theme from file, or use default
        
        Args:
            default: Default theme name if none saved
            
        Returns:
            Theme name string
        """
        settings = self.load_settings()
        return settings.get("theme", default)
    
    def save_user_theme(self, theme_name: str) -> bool:
        """
        Save selected theme to user settings file
        
        Args:
            theme_name: Name of the theme to save
            
        Returns:
            True if successful, False otherwise
        """
        settings = self.load_settings()
        settings["theme"] = theme_name
        return self.save_settings(settings)
    
    def load_settings(self) -> Dict:
        """
        Load all user settings from file
        
        Returns:
            Dictionary of user settings
        """
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        return self.default_settings.copy()
    
    def save_settings(self, settings: Dict) -> bool:
        """
        Save user settings to file
        
        Args:
            settings: Dictionary of settings to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.settings_file, "w") as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save settings: {e}")
            return False

class WeatherFormatter:
    """Handles formatting and display utilities for weather data"""
    
    @staticmethod
    def format_timestamp(timestamp: str) -> str:
        """
        Convert ISO timestamp to readable format
        
        Args:
            timestamp: ISO format timestamp string
            
        Returns:
            Formatted date string
        """
        try:
            return datetime.fromisoformat(timestamp).strftime("%b %d, %Y %I:%M %p")
        except:
            return "N/A"
    
    @staticmethod
    def map_weather_to_emoji(description: str) -> str:
        """
        Map weather descriptions to appropriate emojis
        DEPRECATED: Use IconManager.get_weather_icon() instead
        
        Args:
            description: Weather description string
            
        Returns:
            Emoji character representing the weather
        """
        # Import here to avoid circular imports
        try:
            from .icon_manager import get_weather_icon
            return get_weather_icon(description)
        except ImportError:
            # Fallback to original logic if icon_manager not available
            d = description.lower()
            if "sun" in d or "clear" in d:
                return "☀️"
            elif "partly" in d:
                return "🌤️"
            elif "cloud" in d:
                return "☁️"
            elif "wind" in d:
                return "🌬️"
            elif "rain" in d:
                return "🌧️"
            elif "thunder" in d:
                return "⛈️"
            elif "snow" in d:
                return "❄️"
            else:
                return "🌡️"

# Legacy functions for backward compatibility
def load_user_theme(default="vapor"):
    """Legacy function - wraps the new class-based approach"""
    manager = UserSettingsManager()
    return manager.load_user_theme(default)

def save_user_theme(theme_name):
    """Legacy function - wraps the new class-based approach"""
    manager = UserSettingsManager()
    return manager.save_user_theme(theme_name)

def format_timestamp(timestamp):
    """Legacy function - wraps the new class-based approach"""
    return WeatherFormatter.format_timestamp(timestamp)

def map_weather_to_emoji(description):
    """Legacy function - wraps the new class-based approach"""
    return WeatherFormatter.map_weather_to_emoji(description)
