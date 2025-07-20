"""SQLite database management for weather data storage"""

import sqlite3
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class WeatherDatabase:
    """Handles all database operations for weather data storage"""
    
    def __init__(self, db_path: str = "data/weather.db"):
        """Initialize the database connection"""
        self.db_path = db_path
        self._ensure_database_directory()
        self._initialize_database()
        if not self._verify_tables():
            logger.info("Re-initializing database tables...")
            self._initialize_database()  # Try to create tables again
            if not self._verify_tables():
                raise RuntimeError("Failed to initialize database tables")
        logger.info("Database initialized successfully at %s", self.db_path)
    
    def _ensure_database_directory(self):
        """Create the data directory if it doesn't exist"""
        try:
            directory = os.path.dirname(self.db_path)
            if directory:  # Only create if there's a directory component
                os.makedirs(directory, exist_ok=True)
                # Verify the directory is writable
                if not os.access(directory, os.W_OK):
                    raise PermissionError(f"Database directory {directory} is not writable")
            logger.debug("Database directory verified: %s", directory)
        except Exception as e:
            logger.error("Error ensuring database directory exists: %s", e)
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
                    ('current_weather', 'forecast_weather', 'saved_locations', 'user_preferences', 'historical_weather', 'weather_predictions')
                """)
                existing_tables = {row[0] for row in cursor.fetchall()}
                required_tables = {'current_weather', 'forecast_weather', 'saved_locations', 'user_preferences', 'historical_weather', 'weather_predictions'}
                missing_tables = required_tables - existing_tables
                
                if missing_tables:
                    logger.warning("Missing tables detected: %s", missing_tables)
                    return False
                else:
                    logger.debug("All required database tables verified")
                
                return True
        except Exception as e:
            logger.error("Error verifying tables: %s", e)
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
            
            # Historical weather table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historical_weather (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    state TEXT,
                    date DATE NOT NULL,
                    temperature_max REAL,
                    temperature_min REAL,
                    temperature_mean REAL,
                    precipitation REAL,
                    rain REAL,
                    wind_speed_max REAL,
                    wind_gusts_max REAL,
                    cloud_cover INTEGER,
                    humidity INTEGER,
                    latitude REAL,
                    longitude REAL,
                    sunrise INTEGER,
                    sunset INTEGER,
                    UNIQUE(city, state, date)
                )
            ''')
            
            # Weather predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS weather_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    state TEXT,
                    prediction_date DATE NOT NULL,
                    prediction_day INTEGER NOT NULL,  -- 1, 2, or 3 for day 1-3 forecast
                    predicted_temp_max REAL,
                    predicted_temp_min REAL,
                    predicted_precipitation REAL,
                    predicted_humidity REAL,
                    predicted_wind_speed REAL,
                    predicted_conditions TEXT,
                    model_confidence REAL,
                    data_points_used INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    model_performance TEXT,  -- JSON string of model performance metrics
                    trend_analysis TEXT,     -- JSON string of trend analysis
                    actual_temp_max REAL,    -- Filled in later when actual data is available
                    actual_temp_min REAL,
                    actual_precipitation REAL,
                    actual_humidity REAL,
                    actual_conditions TEXT,
                    accuracy_score REAL,     -- Calculated when actual data is compared
                    is_latest BOOLEAN DEFAULT 1  -- Track which prediction is the most recent for a given date
                )
            ''')
            
            conn.commit()
            
            # Apply database migrations
            self._apply_migrations()
    
    def _apply_migrations(self):
        """Apply database schema migrations for backward compatibility."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Migration 1: Remove UNIQUE constraint and add is_latest column
                cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='weather_predictions'")
                current_schema = cursor.fetchone()
                
                if current_schema and 'UNIQUE(city, state, prediction_date, prediction_day)' in current_schema[0]:
                    logger.info("Applying migration: Removing UNIQUE constraint and adding is_latest column")
                    
                    # Step 1: Create new table without UNIQUE constraint
                    cursor.execute('''
                        CREATE TABLE weather_predictions_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            city TEXT NOT NULL,
                            state TEXT,
                            prediction_date DATE NOT NULL,
                            prediction_day INTEGER NOT NULL,
                            predicted_temp_max REAL,
                            predicted_temp_min REAL,
                            predicted_precipitation REAL,
                            predicted_humidity REAL,
                            predicted_wind_speed REAL,
                            predicted_conditions TEXT,
                            model_confidence REAL,
                            data_points_used INTEGER,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            model_performance TEXT,
                            trend_analysis TEXT,
                            actual_temp_max REAL,
                            actual_temp_min REAL,
                            actual_precipitation REAL,
                            actual_humidity REAL,
                            actual_conditions TEXT,
                            accuracy_score REAL,
                            is_latest BOOLEAN DEFAULT 1
                        )
                    ''')
                    
                    # Step 2: Copy data from old table, marking all as latest
                    cursor.execute('''
                        INSERT INTO weather_predictions_new 
                        SELECT id, city, state, prediction_date, prediction_day,
                               predicted_temp_max, predicted_temp_min, predicted_precipitation,
                               predicted_humidity, predicted_wind_speed, predicted_conditions,
                               model_confidence, data_points_used, created_at,
                               model_performance, trend_analysis,
                               actual_temp_max, actual_temp_min, actual_precipitation,
                               actual_humidity, actual_conditions, accuracy_score,
                               1 as is_latest
                        FROM weather_predictions
                    ''')
                    
                    # Step 3: Drop old table and rename new table
                    cursor.execute('DROP TABLE weather_predictions')
                    cursor.execute('ALTER TABLE weather_predictions_new RENAME TO weather_predictions')
                    
                    conn.commit()
                    logger.info("Migration completed: UNIQUE constraint removed, is_latest column added")
                else:
                    logger.debug("Migration skipped: Table already has correct schema")
                
        except Exception as e:
            logger.error(f"Error applying database migrations: {e}")
    
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
            logger.error("Error saving current weather: %s", e)
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
            logger.error("Error saving forecast data: %s", e)
            return False
    
    def save_historical_weather(self, city: str, state: str, data: Dict) -> bool:
        """
        Save historical weather data to database only if it doesn't already exist
        
        Args:
            city: City name
            state: State code
            data: Dictionary with historical weather data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if data already exists for this city, state, and date
                cursor.execute('''
                    SELECT id FROM historical_weather 
                    WHERE city = ? AND state = ? AND date = ?
                ''', (city, state, data['date']))
                
                existing = cursor.fetchone()
                if existing:
                    logger.debug(f"Historical data already exists for {city}, {state} on {data['date']}")
                    return True  # Return True since data exists (not an error)
                
                # Insert only if data doesn't exist
                cursor.execute('''
                    INSERT INTO historical_weather
                    (city, state, date, temperature_max, temperature_min, temperature_mean,
                     precipitation, rain, wind_speed_max, wind_gusts_max, cloud_cover,
                     humidity, latitude, longitude, sunrise, sunset)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    city,
                    state,
                    data['date'],
                    data['temperature_2m_max'],
                    data['temperature_2m_min'],
                    data['temperature_2m_mean'],
                    data['precipitation_sum'],
                    data['rain_sum'],
                    data['wind_speed_10m_max'],
                    data['wind_gusts_10m_max'],
                    data['cloud_cover_mean'],
                    data['relative_humidity_2m_mean'],
                    data['latitude'],
                    data['longitude'],
                    data['sunrise'],
                    data['sunset']
                ))
                conn.commit()
                logger.debug(f"Saved new historical data for {city}, {state} on {data['date']}")
                return True
        except Exception as e:
            logger.error(f"Error saving historical weather data: {str(e)}")
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
            logger.error("Error retrieving current weather: %s", e)
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
            logger.error("Error retrieving forecast data: %s", e)
            return []
    
    def get_historical_weather(self, city: str, state: str, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Get historical weather data for a city between dates
        
        Args:
            city: City name
            state: State code
            start_date: Start date string (YYYY-MM-DD), optional
            end_date: End date string (YYYY-MM-DD), optional
            
        Returns:
            List of weather data dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if start_date and end_date:
                    # Get data between specific dates
                    cursor.execute('''
                        SELECT *
                        FROM historical_weather
                        WHERE city = ? AND state = ?
                        AND date BETWEEN ? AND ?
                        ORDER BY date ASC
                    ''', (city, state, start_date, end_date))
                else:
                    # Get all historical data for this city/state
                    cursor.execute('''
                        SELECT *
                        FROM historical_weather
                        WHERE city = ? AND state = ?
                        ORDER BY date ASC
                    ''', (city, state))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error retrieving historical weather data: {str(e)}")
            return []
    
    def save_location(
        self,
        city: str,
        state: str = None,
        nickname: str = None,
        latitude: float = None,
        longitude: float = None,
    ) -> bool:
        """Save a location to saved locations"""
        try:
            logger.debug(
                "Attempting to save location: city=%s, state=%s, nickname=%s, lat=%s, lon=%s",
                city,
                state,
                nickname,
                latitude,
                longitude,
            )

            with self.get_connection() as conn:
                cursor = conn.cursor()

                # First check if location already exists
                cursor.execute(
                    """
                        SELECT id FROM saved_locations
                        WHERE city = ? AND state = ?
                    """,
                    (city, state),
                )

                existing = cursor.fetchone()
                if existing:
                    logger.debug("Location already exists with id %s, updating...", existing[0])

                cursor.execute(
                    """
                        INSERT OR REPLACE INTO saved_locations (
                            city, state, nickname, latitude, longitude, last_accessed
                        ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (city, state, nickname, latitude, longitude),
                )

                conn.commit()
                logger.info("Successfully saved location: %s, %s", city, state)
                return True

        except Exception as e:
            logger.error("Error saving location: %s", e)
            logger.debug("Full error details: %s", e.__class__.__name__)
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
            logger.error("Error retrieving saved locations: %s", e)
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
            logger.error("Error removing saved location: %s", e)
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
            logger.error("Error saving user preference: %s", e)
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
            logger.error("Error retrieving user preference: %s", e)
            return default
    
    def save_weather_prediction(self, city: str, state: str, prediction_data: Dict) -> bool:
        """
        Save weather prediction data to database
        
        Args:
            city: City name
            state: State code
            prediction_data: Dictionary containing prediction data from WeatherPredictor
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Extract prediction metadata
                forecast = prediction_data.get('forecast', [])
                confidence = prediction_data.get('confidence', 0.0)
                data_points_used = prediction_data.get('data_points_used', 0)
                model_performance = json.dumps(prediction_data.get('model_performance', {}))
                trend_analysis = json.dumps(prediction_data.get('trend', {}))
                
                # Mark previous predictions as not latest for this city/state/dates
                prediction_dates = [day_pred.get('date') for day_pred in forecast]
                for pred_date in prediction_dates:
                    cursor.execute('''
                        UPDATE weather_predictions 
                        SET is_latest = 0 
                        WHERE city = ? AND state = ? AND prediction_date = ?
                    ''', (city, state, pred_date))
                
                # Save each day's prediction as new entries (preserving all historical predictions)
                for day_pred in forecast:
                    cursor.execute('''
                        INSERT INTO weather_predictions (
                            city, state, prediction_date, prediction_day,
                            predicted_temp_max, predicted_temp_min, predicted_precipitation,
                            predicted_humidity, predicted_wind_speed, predicted_conditions,
                            model_confidence, data_points_used, model_performance, trend_analysis,
                            is_latest
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ''', (
                        city,
                        state,
                        day_pred.get('date'),
                        day_pred.get('day_number'),
                        day_pred.get('temperature_max'),
                        day_pred.get('temperature_min'),
                        day_pred.get('precipitation'),
                        day_pred.get('humidity'),
                        day_pred.get('wind_speed'),
                        day_pred.get('conditions'),
                        confidence,
                        data_points_used,
                        model_performance,
                        trend_analysis
                    ))
                
                conn.commit()
                logger.info(f"Saved {len(forecast)} weather predictions for {city}, {state}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving weather prediction: {str(e)}")
            return False
    
    def get_weather_predictions(self, city: str, state: str, start_date: str = None, end_date: str = None, latest_only: bool = True) -> List[Dict]:
        """
        Get weather predictions for a city between dates
        
        Args:
            city: City name
            state: State code
            start_date: Start date string (YYYY-MM-DD), optional
            end_date: End date string (YYYY-MM-DD), optional
            latest_only: If True, only get the most recent prediction for each date (default: True)
            
        Returns:
            List of prediction dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build WHERE clause
                where_clause = "WHERE city = ? AND state = ?"
                params = [city, state]
                
                if latest_only:
                    where_clause += " AND is_latest = 1"
                
                if start_date and end_date:
                    where_clause += " AND prediction_date BETWEEN ? AND ?"
                    params.extend([start_date, end_date])
                
                query = f'''
                    SELECT * FROM weather_predictions
                    {where_clause}
                    ORDER BY prediction_date ASC, prediction_day ASC
                '''
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error retrieving weather predictions: {str(e)}")
            return []
    
    def get_all_prediction_history(self, city: str, state: str, days_back: int = 365) -> List[Dict]:
        """
        Get ALL historical predictions for ML analysis (not just latest)
        
        Args:
            city: City name
            state: State code  
            days_back: Number of days back to retrieve (default: 365)
            
        Returns:
            List of ALL prediction records for analysis
        """
        try:
            from datetime import datetime, timedelta
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            # Get ALL predictions (not just latest) for ML analysis
            return self.get_weather_predictions(
                city, state,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d'),
                latest_only=False  # Get ALL historical predictions
            )
            
        except Exception as e:
            logger.error(f"Error getting prediction history for ML analysis: {e}")
            return []
    
    def update_prediction_with_actual(self, city: str, state: str, prediction_date: str, 
                                    actual_temp_max: float, actual_temp_min: float,
                                    actual_precipitation: float, actual_humidity: float,
                                    actual_conditions: str) -> bool:
        """
        Update a prediction record with actual weather data and calculate accuracy
        
        Args:
            city: City name
            state: State code
            prediction_date: Date of the prediction (YYYY-MM-DD)
            actual_temp_max: Actual maximum temperature
            actual_temp_min: Actual minimum temperature
            actual_precipitation: Actual precipitation
            actual_humidity: Actual humidity
            actual_conditions: Actual weather conditions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all prediction days for this date
                cursor.execute('''
                    SELECT * FROM weather_predictions
                    WHERE city = ? AND state = ? AND prediction_date = ?
                ''', (city, state, prediction_date))
                
                predictions = cursor.fetchall()
                
                for pred in predictions:
                    # Calculate accuracy score
                    accuracy_score = self._calculate_prediction_accuracy(
                        pred, actual_temp_max, actual_temp_min, 
                        actual_precipitation, actual_humidity, actual_conditions
                    )
                    
                    # Update the record with actual data
                    cursor.execute('''
                        UPDATE weather_predictions
                        SET actual_temp_max = ?, actual_temp_min = ?, 
                            actual_precipitation = ?, actual_humidity = ?,
                            actual_conditions = ?, accuracy_score = ?
                        WHERE id = ?
                    ''', (
                        actual_temp_max, actual_temp_min, actual_precipitation,
                        actual_humidity, actual_conditions, accuracy_score,
                        pred['id']
                    ))
                
                conn.commit()
                logger.info(f"Updated {len(predictions)} predictions with actual data for {city}, {state} on {prediction_date}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating prediction with actual data: {str(e)}")
            return False
    
    def _calculate_prediction_accuracy(self, prediction: Dict, actual_temp_max: float,
                                     actual_temp_min: float, actual_precipitation: float,
                                     actual_humidity: float, actual_conditions: str) -> float:
        """
        Calculate accuracy score for a prediction vs actual data
        
        Returns:
            Accuracy score between 0 and 1
        """
        try:
            scores = []
            
            # Temperature accuracy (weighted heavily)
            if prediction['predicted_temp_max'] is not None and actual_temp_max is not None:
                temp_max_error = abs(prediction['predicted_temp_max'] - actual_temp_max)
                temp_max_score = max(0, 1 - (temp_max_error / 20))  # 20°F tolerance
                scores.append(temp_max_score * 0.3)
            
            if prediction['predicted_temp_min'] is not None and actual_temp_min is not None:
                temp_min_error = abs(prediction['predicted_temp_min'] - actual_temp_min)
                temp_min_score = max(0, 1 - (temp_min_error / 20))  # 20°F tolerance
                scores.append(temp_min_score * 0.3)
            
            # Precipitation accuracy
            if prediction['predicted_precipitation'] is not None and actual_precipitation is not None:
                precip_error = abs(prediction['predicted_precipitation'] - actual_precipitation)
                precip_score = max(0, 1 - (precip_error / 1.0))  # 1 inch tolerance
                scores.append(precip_score * 0.2)
            
            # Humidity accuracy
            if prediction['predicted_humidity'] is not None and actual_humidity is not None:
                humidity_error = abs(prediction['predicted_humidity'] - actual_humidity)
                humidity_score = max(0, 1 - (humidity_error / 30))  # 30% tolerance
                scores.append(humidity_score * 0.1)
            
            # Conditions accuracy (exact match)
            if prediction['predicted_conditions'] and actual_conditions:
                conditions_score = 1.0 if prediction['predicted_conditions'] == actual_conditions else 0.0
                scores.append(conditions_score * 0.1)
            
            # Return average of all scores
            return sum(scores) / len(scores) if scores else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating prediction accuracy: {str(e)}")
            return 0.0
    
    def get_prediction_accuracy_stats(self, city: str = None, state: str = None) -> Dict:
        """
        Get prediction accuracy statistics
        
        Args:
            city: Optional city filter
            state: Optional state filter
            
        Returns:
            Dictionary with accuracy statistics
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Build query with optional filters
                base_query = '''
                    SELECT 
                        AVG(accuracy_score) as avg_accuracy,
                        COUNT(*) as total_predictions,
                        COUNT(CASE WHEN accuracy_score IS NOT NULL THEN 1 END) as verified_predictions,
                        AVG(model_confidence) as avg_confidence,
                        MIN(accuracy_score) as min_accuracy,
                        MAX(accuracy_score) as max_accuracy
                    FROM weather_predictions
                    WHERE accuracy_score IS NOT NULL
                '''
                
                params = []
                if city and state:
                    base_query += " AND city = ? AND state = ?"
                    params.extend([city, state])
                elif city:
                    base_query += " AND city = ?"
                    params.append(city)
                
                cursor.execute(base_query, params)
                stats = dict(cursor.fetchone())
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting prediction accuracy stats: {str(e)}")
            return {}
    
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
                
                # Clean up old historical weather data
                cursor.execute('''
                    DELETE FROM historical_weather 
                    WHERE date < date('now', '-{} days')
                '''.format(days_to_keep))
                
                # Clean up old prediction data (keep longer for accuracy analysis)
                cursor.execute('''
                    DELETE FROM weather_predictions 
                    WHERE datetime(created_at) < datetime('now', '-{} days')
                '''.format(days_to_keep * 3))  # Keep predictions 3x longer
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error("Error cleaning up old data: %s", e)
            return False


# Singleton pattern for database access
_database_instance = None

def get_database() -> WeatherDatabase:
    """Get the singleton database instance"""
    global _database_instance
    if _database_instance is None:
        _database_instance = WeatherDatabase()
    return _database_instance
