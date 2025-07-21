"""JSON synchronization manager for real-time backup of database data"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class JSONSyncManager:
    """Handles real-time synchronization of database data to JSON files"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.saved_cities_path = self.data_dir / "saved_cities.json"
        self.user_settings_path = self.data_dir / "user_settings.json"
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Data directory ensured at {self.data_dir}")
        except Exception as e:
            logger.error(f"Error creating data directory: {e}")
            raise
    
    def _read_json_file(self, file_path: Path, default_value):
        """Safely read a JSON file with fallback to default value"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.info(f"JSON file not found, using default: {file_path}")
                return default_value
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {e}")
            return default_value
    
    def _write_json_file(self, file_path: Path, data):
        """Safely write data to a JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"JSON file updated: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing JSON file {file_path}: {e}")
            return False
    
    def sync_saved_locations_to_json(self, locations_data: List[Dict]) -> bool:
        """Sync saved locations from database to JSON file"""
        try:
            # Convert database format to JSON format
            json_locations = []
            for location in locations_data:
                json_location = {
                    "city": location.get('city', ''),
                    "state": location.get('state', '').lower() if location.get('state') else '',
                    "country": location.get('country', 'US'),
                    "lat": location.get('latitude', 0.0),
                    "lon": location.get('longitude', 0.0),
                    "last_updated": location.get('last_accessed', datetime.now().isoformat())
                }
                
                # Add nickname if it exists
                if location.get('nickname'):
                    json_location["nickname"] = location.get('nickname')
                
                json_locations.append(json_location)
            
            # Write to JSON file
            success = self._write_json_file(self.saved_cities_path, json_locations)
            
            if success:
                logger.info(f"Synced {len(json_locations)} locations to {self.saved_cities_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error syncing locations to JSON: {e}")
            return False
    
    def sync_user_preferences_to_json(self, preferences_data: Dict) -> bool:
        """Sync user preferences from database to JSON file"""
        try:
            # Read current JSON file to preserve any existing settings
            current_settings = self._read_json_file(self.user_settings_path, {})
            
            # Update with database preferences (database takes precedence)
            for key, pref_data in preferences_data.items():
                if isinstance(pref_data, dict) and 'value' in pref_data:
                    current_settings[key] = pref_data['value']
                else:
                    current_settings[key] = pref_data
            
            # Write updated settings to JSON file
            success = self._write_json_file(self.user_settings_path, current_settings)
            
            if success:
                logger.info(f"Synced {len(preferences_data)} preferences to {self.user_settings_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error syncing preferences to JSON: {e}")
            return False
    
    def get_saved_locations_from_json(self) -> List[Dict]:
        """Get saved locations from JSON file (fallback when database is unavailable)"""
        try:
            locations = self._read_json_file(self.saved_cities_path, [])
            logger.info(f"Retrieved {len(locations)} locations from JSON fallback")
            return locations
        except Exception as e:
            logger.error(f"Error reading locations from JSON: {e}")
            return []
    
    def get_user_preferences_from_json(self) -> Dict:
        """Get user preferences from JSON file (fallback when database is unavailable)"""
        try:
            default_settings = {
                "theme": "aj_lightly",
                "light_theme": "aj_lightly", 
                "dark_theme": "aj_darkly",
                "default_location": "",
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
                "pressure_unit": "hPa"
            }
            
            preferences = self._read_json_file(self.user_settings_path, default_settings)
            logger.info(f"Retrieved {len(preferences)} preferences from JSON fallback")
            return preferences
        except Exception as e:
            logger.error(f"Error reading preferences from JSON: {e}")
            return {}
    
    def get_user_preference_from_json(self, key: str, default=None):
        """Get a specific user preference from JSON file"""
        try:
            preferences = self.get_user_preferences_from_json()
            return preferences.get(key, default)
        except Exception as e:
            logger.error(f"Error getting preference '{key}' from JSON: {e}")
            return default
    
    def add_location_to_json(self, city: str, state: str, country: str = "US", 
                           latitude: float = None, longitude: float = None, nickname: str = None) -> bool:
        """Add a single location to JSON file (for direct JSON updates)"""
        try:
            # Read current locations
            current_locations = self.get_saved_locations_from_json()
            
            # Check if location already exists
            for location in current_locations:
                if (location.get('city', '').lower() == city.lower() and 
                    location.get('state', '').lower() == (state or '').lower()):
                    # Update existing location
                    location.update({
                        "lat": latitude or location.get('lat', 0.0),
                        "lon": longitude or location.get('lon', 0.0),
                        "last_updated": datetime.now().isoformat()
                    })
                    if nickname:
                        location["nickname"] = nickname
                    break
            else:
                # Add new location
                new_location = {
                    "city": city,
                    "state": state.lower() if state else '',
                    "country": country,
                    "lat": latitude or 0.0,
                    "lon": longitude or 0.0,
                    "last_updated": datetime.now().isoformat()
                }
                if nickname:
                    new_location["nickname"] = nickname
                current_locations.append(new_location)
            
            # Write back to file
            return self._write_json_file(self.saved_cities_path, current_locations)
            
        except Exception as e:
            logger.error(f"Error adding location to JSON: {e}")
            return False
    
    def set_user_preference_in_json(self, key: str, value: str) -> bool:
        """Set a specific user preference in JSON file (for direct JSON updates)"""
        try:
            # Read current preferences
            current_preferences = self.get_user_preferences_from_json()
            
            # Update the preference
            current_preferences[key] = value
            
            # Write back to file
            return self._write_json_file(self.user_settings_path, current_preferences)
            
        except Exception as e:
            logger.error(f"Error setting preference '{key}' in JSON: {e}")
            return False
    
    def get_sync_status(self) -> Dict:
        """Get status of JSON sync files"""
        try:
            status = {
                'saved_cities': {
                    'exists': self.saved_cities_path.exists(),
                    'size': self.saved_cities_path.stat().st_size if self.saved_cities_path.exists() else 0,
                    'last_modified': datetime.fromtimestamp(self.saved_cities_path.stat().st_mtime).isoformat() if self.saved_cities_path.exists() else None,
                    'record_count': len(self.get_saved_locations_from_json()) if self.saved_cities_path.exists() else 0
                },
                'user_settings': {
                    'exists': self.user_settings_path.exists(),
                    'size': self.user_settings_path.stat().st_size if self.user_settings_path.exists() else 0,
                    'last_modified': datetime.fromtimestamp(self.user_settings_path.stat().st_mtime).isoformat() if self.user_settings_path.exists() else None,
                    'setting_count': len(self.get_user_preferences_from_json()) if self.user_settings_path.exists() else 0
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting sync status: {e}")
            return {'error': str(e)}


# Singleton pattern for JSON sync manager
_json_sync_manager_instance = None

def get_json_sync_manager() -> JSONSyncManager:
    """Get the singleton JSON sync manager instance"""
    global _json_sync_manager_instance
    if _json_sync_manager_instance is None:
        _json_sync_manager_instance = JSONSyncManager()
    return _json_sync_manager_instance