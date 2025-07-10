"""Enhanced data handler with database integration"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from core.database import get_database

logger = logging.getLogger(__name__)

class DatabaseDataHandler:
    """Enhanced data handler that uses SQLite database for persistence"""
    
    def __init__(self):
        self.db = get_database()
        # Keep JSON fallback for migration/backup
        self.json_file = "data/saved_locations.json"
        self._migrate_json_data()
    
    def _migrate_json_data(self):
        """Migrate existing JSON data to database (one-time operation)"""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r') as f:
                    json_data = json.load(f)
                    
                # Migrate saved cities to database
                for city_data in json_data:
                    self.db.save_location(
                        city=city_data.get('city'),
                        state=city_data.get('state'),
                        nickname=city_data.get('nickname')
                    )
                
                # Backup and remove JSON file after migration
                backup_file = f"{self.json_file}.backup"
                os.rename(self.json_file, backup_file)
                logger.info(
                    "Migrated JSON data to database. Backup saved as %s",
                    backup_file,
                )
                
            except Exception as e:
                logger.warning("Migration warning: %s", e)
    
    def save_weather_data(self, weather_data: Dict, city: str, state: str = None) -> bool:
        """Save current weather data to database"""
        return self.db.save_current_weather(weather_data, city, state)
    
    def save_forecast_data(self, forecast_data: List[Dict], city: str, state: str = None) -> bool:
        """Save forecast data to database"""
        return self.db.save_forecast_data(forecast_data, city, state)
    
    def get_weather_data(self, city: str, state: str = None, max_age_hours: int = 1) -> Optional[Dict]:
        """Get cached weather data if recent enough"""
        return self.db.get_current_weather(city, state, max_age_hours)
    
    def get_forecast_data(self, city: str, state: str = None, max_age_hours: int = 6) -> List[Dict]:
        """Get cached forecast data if recent enough"""
        return self.db.get_forecast_data(city, state, max_age_hours)
    
    def save_city(self, city: str, state: str = None, nickname: str = None) -> bool:
        """Save a city to favorites"""
        return self.db.save_location(city, state, nickname)
    
    def load_saved_cities(self) -> List[Dict]:
        """Load all saved cities from database"""
        locations = self.db.get_saved_locations()
        
        # Convert database format to match existing JSON format for compatibility
        formatted_cities = []
        for location in locations:
            formatted_cities.append({
                'id': location['id'],
                'city': location['city'],
                'state': location['state'],
                'nickname': location.get('nickname'),
                'last_updated': location['last_accessed'],
                'is_favorite': bool(location.get('is_favorite', 0))
            })
        
        return formatted_cities
    
    def remove_saved_city(self, city_index_or_id) -> bool:
        """Remove a saved city by index (legacy) or ID"""
        if isinstance(city_index_or_id, int):
            # If it's a small number, treat as index (legacy compatibility)
            if city_index_or_id < 100:  
                saved_cities = self.load_saved_cities()
                if 0 <= city_index_or_id < len(saved_cities):
                    city_id = saved_cities[city_index_or_id]['id']
                    return self.db.remove_saved_location(city_id)
                return False
            else:
                # Treat as database ID
                return self.db.remove_saved_location(city_index_or_id)
        
        return False
    
    def save_user_theme(self, theme: str) -> bool:
        """Save user theme preference to database"""
        return self.db.save_user_preference('theme', theme)
    
    def load_user_theme(self, default: str = 'vapor') -> str:
        """Load user theme preference from database"""
        return self.db.get_user_preference('theme', default)
    
    def save_user_preference(self, key: str, value: str) -> bool:
        """Save any user preference"""
        return self.db.save_user_preference(key, value)
    
    def get_user_preference(self, key: str, default: str = None) -> Optional[str]:
        """Get any user preference"""
        return self.db.get_user_preference(key, default)
    
    def get_weather_history(self, city: str, state: str = None, days: int = 7) -> List[Dict]:
        """Get historical weather data for analytics"""
        # This could be enhanced to return data for charts/trends
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT DATE(timestamp) as date, 
                           AVG(temperature) as avg_temp,
                           AVG(humidity) as avg_humidity,
                           weather_description
                    FROM current_weather 
                    WHERE city = ? AND state = ?
                    AND DATE(timestamp) >= DATE('now', '-{} days')
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                '''.format(days), (city, state))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error("Error getting weather history: %s", e)
            return []
    
    def cleanup_old_data(self, days: int = 30) -> bool:
        """Clean up old weather data"""
        return self.db.cleanup_old_data(days)
    
    def save_historical_data(self, city: str, state: str, historical_df: pd.DataFrame) -> bool:
        """
        Save historical weather data from DataFrame
        
        Args:
            city: City name
            state: State abbreviation
            historical_df: DataFrame containing historical weather data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = True
            for _, row in historical_df.iterrows():
                if not self.db.save_historical_weather(city, state, row):
                    success = False
            return success
        except Exception as e:
            logger.error(f"Error saving historical data: {str(e)}")
            return False
    
    def get_historical_data(self, city: str, state: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Get historical weather data for a city
        
        Args:
            city: City name
            state: State abbreviation
            start_date: Start date
            end_date: End date
            
        Returns:
            List of historical weather data dictionaries
        """
        try:
            return self.db.get_historical_weather(
                city=city,
                state=state,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            return []
