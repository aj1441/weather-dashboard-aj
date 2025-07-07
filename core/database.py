"""SQLite database management for weather data storage"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager

class WeatherDatabase:
    """Handles all database operations for weather data storage"""
    
    def __init__(self, db_path: str = "data/weather.db"):
        """Initialize the database connection"""
        self.db_path = db_path
        self._ensure_database_directory()
        self._initialize_database()
        if not self._verify_tables():
            print("Re-initializing database tables...")
            self._initialize_database()  # Try to create tables again
            if not self._verify_tables():
                raise RuntimeError("Failed to initialize database tables")
        print(f"Database initialized successfully at {self.db_path}")
    
    def _ensure_database_directory(self):
        """Create the data directory if it doesn't exist"""
        try:
            directory = os.path.dirname(self.db_path)
            if directory:  # Only create if there's a directory component
                os.makedirs(directory, exist_ok=True)
                # Verify the directory is writable
                if not os.access(directory, os.W_OK):
                    raise PermissionError(f"Database directory {directory} is not writable")
            print(f"Database directory verified: {directory}")
        except Exception as e:
            print(f"Error ensuring database directory exists: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    def _verify_tables(self):
        """Verify that all required tables exist"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN 
                    ('current_weather', 'forecast_weather', 'saved_locations', 'user_preferences')
                """)
                existing_tables = {row[0] for row in cursor.fetchall()}
                required_tables = {'current_weather', 'forecast_weather', 'saved_locations', 'user_preferences'}
                missing_tables = required_tables - existing_tables
                
                if missing_tables:
                    print(f"Missing tables detected: {missing_tables}")
                    return False
                else:
                    print("All required database tables verified")
                
                return True
        except Exception as e:
            print(f"Error verifying tables: {e}")
            return False

    def _initialize_database(self):
        """Create database tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Current weather table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS current_weather (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    state TEXT,
                    country TEXT DEFAULT 'US',
                    latitude REAL,
                    longitude REAL,
                    temperature REAL,
                    feels_like REAL,
                    humidity INTEGER,
                    pressure REAL,
                    wind_speed REAL,
                    wind_direction INTEGER,
                    weather_description TEXT,
                    weather_main TEXT,
                    weather_icon TEXT,
                    visibility INTEGER,
                    uv_index REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    api_response TEXT,  -- Store full API response as JSON
                    UNIQUE(city, state, timestamp)
                )
            ''')
            
            # Forecast data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS forecast_weather (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    state TEXT,
                    country TEXT DEFAULT 'US',
                    forecast_date DATE,
                    temperature_min REAL,
                    temperature_max REAL,
                    temperature_day REAL,
                    temperature_night REAL,
                    humidity INTEGER,
                    pressure REAL,
                    wind_speed REAL,
                    weather_description TEXT,
                    weather_main TEXT,
                    weather_icon TEXT,
                    precipitation_probability REAL,
                    precipitation_amount REAL,
                    created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    api_response TEXT,
                    UNIQUE(city, state, forecast_date)
                )
            ''')
            
            # Saved locations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    state TEXT,
                    country TEXT DEFAULT 'US',
                    latitude REAL,
                    longitude REAL,
                    nickname TEXT,  -- User-defined name
                    is_favorite BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(city, state, country)
                )
            ''')
            
            # User preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_key TEXT UNIQUE NOT NULL,
                    preference_value TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def save_current_weather(self, weather_data: Dict, city: str, state: str = None) -> bool:
        """Save current weather data to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Extract data from API response
                main_data = weather_data.get('main', {})
                weather_info = weather_data.get('weather', [{}])[0]
                wind_data = weather_data.get('wind', {})
                coord_data = weather_data.get('coord', {})
                
                cursor.execute('''
                    INSERT OR REPLACE INTO current_weather (
                        city, state, latitude, longitude, temperature, feels_like,
                        humidity, pressure, wind_speed, wind_direction,
                        weather_description, weather_main, weather_icon,
                        visibility, api_response
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    city,
                    state,
                    coord_data.get('lat'),
                    coord_data.get('lon'),
                    main_data.get('temp'),
                    main_data.get('feels_like'),
                    main_data.get('humidity'),
                    main_data.get('pressure'),
                    wind_data.get('speed'),
                    wind_data.get('deg'),
                    weather_info.get('description'),
                    weather_info.get('main'),
                    weather_info.get('icon'),
                    weather_data.get('visibility'),
                    json.dumps(weather_data)
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving current weather: {e}")
            return False
    
    def save_forecast_data(self, forecast_data: List[Dict], city: str, state: str = None) -> bool:
        """Save 7-day forecast data to database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                for day_forecast in forecast_data:
                    # Extract forecast data
                    temp_data = day_forecast.get('temp', {})
                    weather_info = day_forecast.get('weather', [{}])[0]
                    
                    # Convert timestamp to date
                    forecast_date = datetime.fromtimestamp(day_forecast.get('dt')).date()
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO forecast_weather (
                            city, state, forecast_date, temperature_min, temperature_max,
                            temperature_day, temperature_night, humidity, pressure,
                            wind_speed, weather_description, weather_main, weather_icon,
                            precipitation_probability, api_response
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        city,
                        state,
                        forecast_date,
                        temp_data.get('min'),
                        temp_data.get('max'),
                        temp_data.get('day'),
                        temp_data.get('night'),
                        day_forecast.get('humidity'),
                        day_forecast.get('pressure'),
                        day_forecast.get('wind_speed'),
                        weather_info.get('description'),
                        weather_info.get('main'),
                        weather_info.get('icon'),
                        day_forecast.get('pop'),  # Probability of precipitation
                        json.dumps(day_forecast)
                    ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving forecast data: {e}")
            return False
    
    def get_current_weather(self, city: str, state: str = None, max_age_hours: int = 1) -> Optional[Dict]:
        """Retrieve current weather data from database if recent enough"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT * FROM current_weather 
                    WHERE city = ? AND state = ?
                    AND datetime(timestamp) > datetime('now', '-{} hours')
                    ORDER BY timestamp DESC LIMIT 1
                '''.format(max_age_hours)
                
                cursor.execute(query, (city, state))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            print(f"Error retrieving current weather: {e}")
            return None
    
    def get_forecast_data(self, city: str, state: str = None, max_age_hours: int = 6) -> List[Dict]:
        """Retrieve forecast data from database if recent enough"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT * FROM forecast_weather 
                    WHERE city = ? AND state = ?
                    AND datetime(created_timestamp) > datetime('now', '-{} hours')
                    ORDER BY forecast_date ASC
                '''.format(max_age_hours)
                
                cursor.execute(query, (city, state))
                rows = cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"Error retrieving forecast data: {e}")
            return []
    
    def save_location(self, city: str, state: str = None, nickname: str = None, 
                        latitude: float = None, longitude: float = None) -> bool:
            """Save a location to saved locations"""
            try:
                print(f"Attempting to save location: city={city}, state={state}, nickname={nickname}, "
                    f"lat={latitude}, lon={longitude}")
                
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # First check if location already exists
                    cursor.execute('''
                        SELECT id FROM saved_locations 
                        WHERE city = ? AND state = ?
                    ''', (city, state))
                    
                    existing = cursor.fetchone()
                    if existing:
                        print(f"Location already exists with id {existing[0]}, updating...")
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO saved_locations (
                            city, state, nickname, latitude, longitude, last_accessed
                        ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (city, state, nickname, latitude, longitude))
                    
                    conn.commit()
                    print(f"Successfully saved location: {city}, {state}")
                    return True
                    
            except Exception as e:
                print(f"Error saving location: {e}")
                print(f"Full error details: ", e.__class__.__name__)
                return False
    
    def get_saved_locations(self) -> List[Dict]:
        """Get all saved locations"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM saved_locations 
                    ORDER BY is_favorite DESC, last_accessed DESC
                ''')
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"Error retrieving saved locations: {e}")
            return []
    
    def remove_saved_location(self, location_id: int) -> bool:
        """Remove a saved location by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM saved_locations WHERE id = ?', (location_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error removing saved location: {e}")
            return False
    
    def save_user_preference(self, key: str, value: str) -> bool:
        """Save a user preference"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_preferences (preference_key, preference_value)
                    VALUES (?, ?)
                ''', (key, value))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error saving user preference: {e}")
            return False
    
    def get_user_preference(self, key: str, default: str = None) -> Optional[str]:
        """Get a user preference value"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT preference_value FROM user_preferences WHERE preference_key = ?', (key,))
                row = cursor.fetchone()
                return row[0] if row else default
                
        except Exception as e:
            print(f"Error retrieving user preference: {e}")
            return default
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """Clean up old weather data to prevent database bloat"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Clean up old current weather data
                cursor.execute('''
                    DELETE FROM current_weather 
                    WHERE datetime(timestamp) < datetime('now', '-{} days')
                '''.format(days_to_keep))
                
                # Clean up old forecast data
                cursor.execute('''
                    DELETE FROM forecast_weather 
                    WHERE datetime(created_timestamp) < datetime('now', '-{} days')
                '''.format(days_to_keep))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
            return False


# Singleton pattern for database access
_database_instance = None

def get_database() -> WeatherDatabase:
    """Get the singleton database instance"""
    global _database_instance
    if _database_instance is None:
        _database_instance = WeatherDatabase()
    return _database_instance
