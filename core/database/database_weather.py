"""Weather-specific database operations for current, forecast, and historical weather data"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager
from utils.performance_optimizer import monitor_performance

logger = logging.getLogger(__name__)

class WeatherDataOperations:
    """Handles weather-specific database operations"""
    
    def __init__(self, database):
        self.db = database
    
    @monitor_performance("save_current_weather")
    def save_current_weather(self, weather_data: Dict, city: str, state: str = None) -> bool:
        """Save current weather data to database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO current_weather 
                    (city, state, temperature, humidity, weather_main, weather_description, 
                     wind_speed, pressure, visibility, sunrise, sunset, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    city, state,
                    weather_data.get('temperature'),
                    weather_data.get('humidity'),
                    weather_data.get('weather_main'),
                    weather_data.get('weather_description'),
                    weather_data.get('wind_speed'),
                    weather_data.get('pressure'),
                    weather_data.get('visibility'),
                    weather_data.get('sunrise'),
                    weather_data.get('sunset'),
                    datetime.now()
                ))
                conn.commit()
                logger.debug(f"Saved current weather for {city}, {state}")
                return True
        except Exception as e:
            logger.error(f"Error saving current weather: {e}")
            return False
    
    def save_forecast_data(self, forecast_data: List[Dict], city: str, state: str = None) -> bool:
        """Save forecast weather data to database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                for forecast in forecast_data:
                    cursor.execute("""
                        INSERT OR REPLACE INTO forecast_weather 
                        (city, state, forecast_date, temp_min, temp_max, humidity, 
                         weather_main, weather_description, wind_speed, pressure, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        city, state,
                        forecast.get('date'),
                        forecast.get('temp_min'),
                        forecast.get('temp_max'),
                        forecast.get('humidity'),
                        forecast.get('weather_main'),
                        forecast.get('weather_description'),
                        forecast.get('wind_speed'),
                        forecast.get('pressure'),
                        datetime.now()
                    ))
                conn.commit()
                logger.debug(f"Saved forecast data for {city}, {state}")
                return True
        except Exception as e:
            logger.error(f"Error saving forecast data: {e}")
            return False
    
    def save_historical_weather(self, city: str, state: str, data: Dict) -> bool:
        """Save historical weather data to database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                for date, weather in data.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO historical_weather 
                        (city, state, date, temp_min, temp_max, humidity, weather_main, 
                         weather_description, wind_speed, pressure, precipitation, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        city, state, date,
                        weather.get('temp_min'),
                        weather.get('temp_max'),
                        weather.get('humidity'),
                        weather.get('weather_main'),
                        weather.get('weather_description'),
                        weather.get('wind_speed'),
                        weather.get('pressure'),
                        weather.get('precipitation'),
                        datetime.now()
                    ))
                conn.commit()
                logger.debug(f"Saved historical weather for {city}, {state}")
                return True
        except Exception as e:
            logger.error(f"Error saving historical weather: {e}")
            return False
    
    @monitor_performance("get_current_weather")
    def get_current_weather(self, city: str, state: str = None, max_age_hours: int = 1) -> Optional[Dict]:
        """Get current weather data from database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
                cursor.execute("""
                    SELECT * FROM current_weather 
                    WHERE city = ? AND state = ? AND timestamp > ?
                    ORDER BY timestamp DESC LIMIT 1
                """, (city, state, cutoff_time))
                row = cursor.fetchone()
                if row:
                    return dict(zip([col[0] for col in cursor.description], row))
                return None
        except Exception as e:
            logger.error(f"Error getting current weather: {e}")
            return None
    
    def get_forecast_data(self, city: str, state: str = None, max_age_hours: int = 6) -> List[Dict]:
        """Get forecast weather data from database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
                cursor.execute("""
                    SELECT * FROM forecast_weather 
                    WHERE city = ? AND state = ? AND timestamp > ?
                    ORDER BY forecast_date ASC
                """, (city, state, cutoff_time))
                rows = cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting forecast data: {e}")
            return []
    
    def get_historical_weather(self, city: str, state: str, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get historical weather data from database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM historical_weather WHERE city = ? AND state = ?"
                params = [city, state]
                
                if start_date:
                    query += " AND date >= ?"
                    params.append(start_date)
                if end_date:
                    query += " AND date <= ?"
                    params.append(end_date)
                
                query += " ORDER BY date ASC"
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting historical weather: {e}")
            return []
    
    def save_recent_historical_weather(self, city: str, state: str, data: Dict) -> bool:
        """Save recent historical weather data to database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                for date, weather in data.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO recent_historical_weather 
                        (city, state, date, temp_min, temp_max, humidity, weather_main, 
                         weather_description, wind_speed, pressure, precipitation, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        city, state, date,
                        weather.get('temp_min'),
                        weather.get('temp_max'),
                        weather.get('humidity'),
                        weather.get('weather_main'),
                        weather.get('weather_description'),
                        weather.get('wind_speed'),
                        weather.get('pressure'),
                        weather.get('precipitation'),
                        datetime.now()
                    ))
                conn.commit()
                logger.debug(f"Saved recent historical weather for {city}, {state}")
                return True
        except Exception as e:
            logger.error(f"Error saving recent historical weather: {e}")
            return False
    
    def get_recent_historical_weather(self, city: str, state: str, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get recent historical weather data from database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM recent_historical_weather WHERE city = ? AND state = ?"
                params = [city, state]
                
                if start_date:
                    query += " AND date >= ?"
                    params.append(start_date)
                if end_date:
                    query += " AND date <= ?"
                    params.append(end_date)
                
                query += " ORDER BY date ASC"
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(zip([col[0] for col in cursor.description], row)) for row in rows]
        except Exception as e:
            logger.error(f"Error getting recent historical weather: {e}")
            return [] 