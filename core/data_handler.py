"""Weather data handling module"""

import json
from datetime import datetime
import os
from typing import Dict, List, Optional

class WeatherDataHandler:
    """Handles all weather data operations including saving and loading"""
    
    def __init__(self, data_directory: str = "data"):
        self.data_directory = data_directory
        self.default_filename = "weather_history.json"
        self.saved_cities_filename = "saved_cities.json"
        self._ensure_data_directory()
    
    def _ensure_data_directory(self) -> None:
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
    
    def save_weather_data(self, data: Dict, filename: str = None) -> bool:
        """
        Append weather data to a local JSON file
        
        Args:
            data: Weather data dictionary from API
            filename: Optional custom filename (uses default if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        if filename is None:
            filename = os.path.join(self.data_directory, self.default_filename)
        elif not filename.startswith(self.data_directory):
            filename = os.path.join(self.data_directory, filename)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "city": data.get("name"),
            "temperature": data.get("main", {}).get("temp"),
            "description": data.get("weather", [{}])[0].get("description")
        }

        try:
            history = self.load_weather_history(filename)
            history.append(entry)

            with open(filename, "w") as file:
                json.dump(history, file, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_weather_history(self, filename: str = None) -> List[Dict]:
        """
        Load weather history from JSON file
        
        Args:
            filename: Optional custom filename (uses default if not provided)
            
        Returns:
            List of weather data entries
        """
        if filename is None:
            filename = os.path.join(self.data_directory, self.default_filename)
        elif not filename.startswith(self.data_directory):
            filename = os.path.join(self.data_directory, filename)
            
        try:
            if os.path.exists(filename):
                with open(filename, "r") as file:
                    return json.load(file)
            return []
        except Exception as e:
            print(f"Error loading data: {e}")
            return []
    
    def get_recent_weather(self, limit: int = 10) -> List[Dict]:
        """
        Get the most recent weather entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent weather data entries
        """
        history = self.load_weather_history()
        return history[-limit:] if history else []
    
    def save_city(self, weather_data: Dict, state: str = "") -> bool:
        """
        Save a city to the saved cities list
        
        Args:
            weather_data: Weather data dictionary from API
            state: State abbreviation (optional)
            
        Returns:
            True if successful, False otherwise
        """
        city_entry = {
            "city": weather_data.get("name"),
            "state": state,
            "country": weather_data.get("sys", {}).get("country", "US"),
            "lat": weather_data.get("coord", {}).get("lat"),
            "lon": weather_data.get("coord", {}).get("lon"),
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            saved_cities = self.load_saved_cities()
            
            # Check if city already exists (avoid duplicates)
            city_name = city_entry["city"]
            existing_city = next((city for city in saved_cities if city["city"] == city_name), None)
            
            if existing_city:
                # Update existing city's last_updated time
                existing_city["last_updated"] = city_entry["last_updated"]
            else:
                # Add new city
                saved_cities.append(city_entry)
            
            filename = os.path.join(self.data_directory, self.saved_cities_filename)
            with open(filename, "w") as file:
                json.dump(saved_cities, file, indent=2)
            return True
        except Exception as e:
            print(f"Error saving city: {e}")
            return False
    
    def load_saved_cities(self) -> List[Dict]:
        """
        Load saved cities from JSON file
        
        Returns:
            List of saved city entries
        """
        filename = os.path.join(self.data_directory, self.saved_cities_filename)
        try:
            if os.path.exists(filename):
                with open(filename, "r") as file:
                    return json.load(file)
            return []
        except Exception as e:
            print(f"Error loading saved cities: {e}")
            return []
    
    def remove_saved_city(self, index: int) -> bool:
        """
        Remove a city from saved cities by index
        
        Args:
            index: Index of city to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            saved_cities = self.load_saved_cities()
            if 0 <= index < len(saved_cities):
                saved_cities.pop(index)
                filename = os.path.join(self.data_directory, self.saved_cities_filename)
                with open(filename, "w") as file:
                    json.dump(saved_cities, file, indent=2)
                return True
            return False
        except Exception as e:
            print(f"Error removing saved city: {e}")
            return False

# Legacy function for backward compatibility
def save_weather_data(data, filename="data/weather_history.json"):
    """Legacy function - wraps the new class-based approach"""
    handler = WeatherDataHandler()
    return handler.save_weather_data(data, filename)
