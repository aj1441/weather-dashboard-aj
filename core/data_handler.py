"""Weather data handling module with integrated validation and config support"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from config import Config
from core.data_validator import WeatherDataValidator
from core.state_utils import normalize_state_abbreviation
from core.database import WeatherDatabase

class WeatherDataHandler:
    """Handles all weather data operations with integrated validation and config support"""
    
    def __init__(self, config: Config = None, data_directory: str = "data"):
        # Use config if provided, otherwise fall back to defaults
        self.config = config
        if config:
            self.data_directory = os.path.dirname(config.database_path)
            self.database_path = config.database_path
        else:
            self.data_directory = data_directory
            self.database_path = os.path.join(data_directory, "weather.db")
        
        self.default_filename = "weather_history.json"
        self.saved_cities_filename = "saved_cities.json"
        
        # Initialize validator, logger, and database
        self.validator = WeatherDataValidator()
        self.logger = logging.getLogger(__name__)
        self.db = WeatherDatabase(self.database_path)
        
        self._ensure_data_directory()

    def _ensure_data_directory(self) -> None:
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
    
    def save_weather_data_validated(self, validated_data: Dict, to_database: bool = True, to_json: bool = True) -> bool:
        """
        Save pre-validated weather data to storage
        
        Args:
            validated_data: Already validated and cleaned weather data
            to_database: Whether to save to SQLite database
            to_json: Whether to save to JSON file (for backward compatibility)
            
        Returns:
            True if successful, False otherwise
        """
        success = True
        
        if to_database:
            try:
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    # Ensure timestamp is present
                    timestamp = validated_data.get('timestamp') or datetime.now().isoformat()
                    
                    cursor.execute('''
                        INSERT INTO current_weather (
                            city, state, country, latitude, longitude,
                            temperature, feels_like, humidity, pressure,
                            wind_speed, wind_direction, weather_description,
                            weather_main, weather_icon, visibility, uv_index,
                            timestamp, api_response
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        validated_data.get('city'),
                        validated_data.get('state'),
                        validated_data.get('country', 'US'),
                        validated_data.get('latitude'),
                        validated_data.get('longitude'),
                        validated_data.get('temperature'),
                        validated_data.get('feels_like'),
                        validated_data.get('humidity'),
                        validated_data.get('pressure'),
                        validated_data.get('wind_speed'),
                        validated_data.get('wind_direction'),
                        validated_data.get('weather_description'),
                        validated_data.get('weather_main'),
                        validated_data.get('weather_icon'),
                        validated_data.get('visibility'),
                        validated_data.get('uv_index'),
                        timestamp,
                        json.dumps(validated_data)  # Store full data as JSON
                    ))
                    conn.commit()
                self.logger.info(f"Successfully saved weather data to database for {validated_data.get('city')}")
            except Exception as e:
                self.logger.error(f"Error saving to database: {str(e)}")
                success = False
        
        if to_json:
            success &= self._save_to_json_legacy(validated_data)
        
        return success

    def save_city(self, city_data: Dict) -> bool:
        """Save a city to saved locations"""
        try:
            # Normalize state abbreviation to uppercase
            state = normalize_state_abbreviation(city_data.get('state', ''))
            
            self.logger.info(f"Attempting to save city: {city_data.get('city')}, {state}")
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO saved_locations (
                        city, state, country, latitude, longitude
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    city_data.get('city'),
                    state,  # Use normalized state
                    city_data.get('country', 'US'),
                    city_data.get('latitude'),
                    city_data.get('longitude')
                ))
                conn.commit()
            self.logger.info(f"Successfully saved city {city_data.get('city')} to database")
            return True
        except Exception as e:
            self.logger.error(f"Error saving city to database: {str(e)}")
            return False

    def load_saved_cities(self) -> List[Dict]:
        """Load saved cities from database"""
        try:
            self.logger.info("Loading saved cities from database")
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM saved_locations')
                rows = cursor.fetchall()
                cities = [dict(row) for row in rows]
                self.logger.info(f"Successfully loaded {len(cities)} saved cities")
                return cities
        except Exception as e:
            self.logger.error(f"Error loading saved cities: {str(e)}")
            return []

    def delete_city(self, city: str, state: str = None, country: str = 'US') -> bool:
        """Delete a city from saved locations"""
        try:
            self.logger.info(f"Attempting to delete city: {city}, {state}")
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                if state:
                    cursor.execute('''
                        DELETE FROM saved_locations
                        WHERE city = ? AND state = ? AND country = ?
                    ''', (city, state, country))
                else:
                    cursor.execute('''
                        DELETE FROM saved_locations
                        WHERE city = ? AND state IS NULL AND country = ?
                    ''', (city, country))
                conn.commit()
                self.logger.info(f"Successfully deleted city {city} from database")
                return True
        except Exception as e:
            self.logger.error(f"Error deleting city from database: {str(e)}")
            return False

    def _save_to_json_legacy(self, data: Dict) -> bool:
        """Save to JSON file for backward compatibility"""
        try:
            filepath = os.path.join(self.data_directory, self.default_filename)
            history = []
            
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as file:
                        history = json.load(file)
                except json.JSONDecodeError:
                    self.logger.warning(f"Could not decode existing JSON file: {filepath}")
                    history = []
            
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()
            
            history.append(data)
            
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(history, file, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving to JSON: {str(e)}")
            return False

    def save_forecast_data(self, city: str, state: str, country: str, forecast_data: List[Dict]) -> bool:
        """
        Save forecast data to the database
        
        Args:
            city: City name
            state: State code
            country: Country code
            forecast_data: List of forecast dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not forecast_data:
            self.logger.warning("No forecast data to save")
            return False
            
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # First, delete existing forecast data for this location to avoid duplicates
                cursor.execute('''
                    DELETE FROM forecast_weather 
                    WHERE city = ? AND state = ? AND country = ?
                ''', (city, state, country))
                
                # Insert new forecast data
                for day_forecast in forecast_data:
                    try:
                        # Convert timestamp to date
                        dt = day_forecast.get('dt')
                        if dt:
                            forecast_date = datetime.fromtimestamp(dt).strftime('%Y-%m-%d')
                        else:
                            continue  # Skip if no timestamp
                        
                        cursor.execute('''
                            INSERT OR REPLACE INTO forecast_weather (
                                city, state, country, forecast_date,
                                temperature_min, temperature_max, temperature_day, temperature_night,
                                humidity, pressure, wind_speed,
                                weather_description, weather_main, weather_icon,
                                precipitation_probability, precipitation_amount,
                                created_timestamp, api_response
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            city, state, country, forecast_date,
                            day_forecast.get('temp_min'),
                            day_forecast.get('temp_max'), 
                            day_forecast.get('temp_day'),
                            day_forecast.get('temp_night'),
                            day_forecast.get('humidity'),
                            day_forecast.get('pressure'),
                            day_forecast.get('wind_speed'),
                            day_forecast.get('description'),
                            day_forecast.get('main'),
                            day_forecast.get('icon'),
                            day_forecast.get('pop', 0),  # Precipitation probability
                            day_forecast.get('precipitation_amount', 0),
                            datetime.now().isoformat(),
                            json.dumps(day_forecast)  # Store full forecast data as JSON
                        ))
                    except Exception as e:
                        self.logger.warning(f"Error saving individual forecast day: {str(e)}")
                        continue
                
                conn.commit()
                self.logger.info(f"Successfully saved {len(forecast_data)} forecast days for {city}, {state}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving forecast data to database: {str(e)}")
            return False

    def get_forecast_data(self, city: str, state: str = None, country: str = 'US', days: int = 7) -> List[Dict]:
        """
        Retrieve forecast data from the database
        
        Args:
            city: City name
            state: State code
            country: Country code  
            days: Number of forecast days to retrieve
            
        Returns:
            List of forecast dictionaries
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM forecast_weather 
                    WHERE city = ? AND state = ? AND country = ?
                    ORDER BY forecast_date ASC
                    LIMIT ?
                ''', (city, state, country, days))
                
                results = cursor.fetchall()
                
                forecast_data = []
                for row in results:
                    forecast_item = {
                        'id': row['id'],
                        'forecast_date': row['forecast_date'],
                        'temp_min': row['temperature_min'],
                        'temp_max': row['temperature_max'],
                        'temp_day': row['temperature_day'],
                        'temp_night': row['temperature_night'],
                        'humidity': row['humidity'],
                        'pressure': row['pressure'],
                        'wind_speed': row['wind_speed'],
                        'description': row['weather_description'],
                        'main': row['weather_main'],
                        'icon': row['weather_icon'],
                        'pop': row['precipitation_probability'],
                        'precipitation_amount': row['precipitation_amount'],
                        'created_timestamp': row['created_timestamp']
                    }
                    
                    # Try to parse the stored API response if available
                    if row['api_response']:
                        try:
                            api_data = json.loads(row['api_response'])
                            forecast_item['api_data'] = api_data
                        except json.JSONDecodeError:
                            pass
                    
                    forecast_data.append(forecast_item)
                
                self.logger.info(f"Retrieved {len(forecast_data)} forecast days for {city}, {state}")
                return forecast_data
                
        except Exception as e:
            self.logger.error(f"Error retrieving forecast data from database: {str(e)}")
            return []
    
    def cleanup_old_forecast_data(self, days_to_keep: int = 30) -> bool:
        """
        Clean up old forecast data to prevent database bloat
        
        Args:
            days_to_keep: Number of days of forecast data to keep
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete forecast data older than specified days
                cursor.execute('''
                    DELETE FROM forecast_weather 
                    WHERE created_timestamp < datetime('now', '-{} days')
                '''.format(days_to_keep))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    self.logger.info(f"Cleaned up {deleted_count} old forecast records")
                else:
                    self.logger.debug("No old forecast records to clean up")
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old forecast data: {str(e)}")
            return False


