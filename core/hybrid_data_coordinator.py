"""
Hybrid weather data coordinator that combines Open-Meteo bulk historical data 
with OpenWeather recent historical data for optimal prediction accuracy.
"""

import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .open_meteo_historical import OpenMeteoHistorical
from .openweather_history_client import OpenWeatherHistoryClient
from .database import WeatherDatabase

logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    OPEN_METEO_BULK = "open_meteo_bulk"
    OPENWEATHER_RECENT = "openweather_recent"

@dataclass
class HybridDataConfig:
    """Configuration for hybrid data approach"""
    recent_days_threshold: int = 7  # Use OpenWeather for last 7 days
    bulk_cutoff_days: int = 5       # Use Open-Meteo for >5 days old
    cache_expiry_hours: int = 24    # How long to cache data

class HybridWeatherDataCoordinator:
    """
    Coordinates data fetching from multiple sources for optimal prediction accuracy.
    
    Strategy:
    - Open-Meteo: Bulk historical data (>5 days old) - FREE, lots of data
    - OpenWeather: Recent 7-day history - MORE ACCURATE for recent patterns
    """
    
    def __init__(self, database: WeatherDatabase = None, config: HybridDataConfig = None):
        self.db = database or WeatherDatabase()
        self.config = config or HybridDataConfig()
        self.open_meteo_client = OpenMeteoHistorical()
        self.openweather_client = OpenWeatherHistoryClient()
        self.logger = logging.getLogger(__name__)
    
    def fetch_combined_historical_data(self, 
                                     city: str, 
                                     state: str, 
                                     latitude: float, 
                                     longitude: float) -> Tuple[bool, Optional[str]]:
        """
        Fetch and combine historical data from both sources for a single city.
        
        Args:
            city: City name
            state: State abbreviation  
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Tuple of (success status, error message if any)
        """
        try:
            self.logger.info(f"Starting hybrid data fetch for {city}, {state}")
            
            # Step 1: Check what data we already have
            existing_coverage = self._analyze_existing_data_coverage(city, state)
            self.logger.info(f"Existing data coverage: {existing_coverage}")
            
            # Step 2: Fetch bulk historical data (Open-Meteo)
            bulk_success, bulk_error = self._fetch_bulk_historical_data(
                city, state, latitude, longitude, existing_coverage
            )
            
            # Step 3: Fetch recent historical data (OpenWeather)
            recent_success, recent_error = self._fetch_recent_historical_data(
                city, state, latitude, longitude, existing_coverage
            )
            
            # Step 4: Combine and validate the data
            combined_data = self._get_combined_historical_data(city, state)
            
            if combined_data is None or len(combined_data) < 60:
                return False, f"Insufficient combined data: {len(combined_data) if combined_data else 0} days"
            
            self.logger.info(f"Hybrid data fetch completed successfully. Total data points: {len(combined_data)}")
            
            # Determine overall success
            if bulk_success or recent_success:
                errors = []
                if bulk_error:
                    errors.append(f"Bulk data: {bulk_error}")
                if recent_error:
                    errors.append(f"Recent data: {recent_error}")
                
                error_msg = "; ".join(errors) if errors else None
                return True, error_msg
            else:
                return False, f"Both data sources failed. Bulk: {bulk_error}, Recent: {recent_error}"
                
        except Exception as e:
            self.logger.error(f"Error in hybrid data fetch: {e}")
            return False, f"Hybrid fetch error: {str(e)}"
    
    def _analyze_existing_data_coverage(self, city: str, state: str) -> Dict:
        """Analyze what historical data already exists"""
        try:
            # Check bulk historical table
            bulk_data = self.db.get_historical_weather(city, state)
            
            # Check recent historical table  
            recent_data = self.db.get_recent_historical_weather(city, state)
            
            coverage = {
                'bulk_records': len(bulk_data) if bulk_data else 0,
                'recent_records': len(recent_data) if recent_data else 0,
                'bulk_date_range': None,
                'recent_date_range': None,
                'total_records': 0
            }
            
            if bulk_data:
                dates = [datetime.strptime(r['date'], '%Y-%m-%d') for r in bulk_data]
                coverage['bulk_date_range'] = (min(dates), max(dates))
            
            if recent_data:
                dates = [datetime.strptime(r['date'], '%Y-%m-%d') for r in recent_data]
                coverage['recent_date_range'] = (min(dates), max(dates))
            
            coverage['total_records'] = coverage['bulk_records'] + coverage['recent_records']
            
            return coverage
            
        except Exception as e:
            self.logger.error(f"Error analyzing data coverage: {e}")
            return {'bulk_records': 0, 'recent_records': 0, 'total_records': 0}
    
    def _fetch_bulk_historical_data(self, city: str, state: str, 
                                  latitude: float, longitude: float, 
                                  existing_coverage: Dict) -> Tuple[bool, Optional[str]]:
        """Fetch bulk historical data from Open-Meteo"""
        try:
            # Skip if we already have substantial bulk data
            if existing_coverage.get('bulk_records', 0) > 1000:
                self.logger.info("Sufficient bulk historical data already exists, skipping Open-Meteo fetch")
                return True, None
            
            self.logger.info("Fetching bulk historical data from Open-Meteo...")
            
            # Fetch from Open-Meteo (gets data from 2010 to 5 days ago)
            result = self.open_meteo_client.get_historical_data(latitude, longitude)
            # Handle the result format: ((df, error), success)
            if isinstance(result, tuple) and len(result) == 2:
                if isinstance(result[0], tuple):
                    df, error = result[0]
                else:
                    df, error = result
            else:
                df, error = result, None
            
            if error:
                return False, f"Open-Meteo error: {error}"
            
            if df is None or df.empty:
                return False, "No bulk historical data received"
            
            # Clean the data
            cleaned_df = self.open_meteo_client.clean_historical_data(df)
            if cleaned_df is None:
                return False, "Failed to clean bulk historical data"
            
            # Add city/state metadata
            cleaned_df['city'] = city
            cleaned_df['state'] = state
            
            # Save to historical_weather table (checking for duplicates)
            saved_count = 0
            for _, row in cleaned_df.iterrows():
                if self.db.save_historical_weather(city, state, row.to_dict()):
                    saved_count += 1
            
            self.logger.info(f"Saved {saved_count} bulk historical records for {city}, {state}")
            return True, None
            
        except Exception as e:
            self.logger.error(f"Error fetching bulk historical data: {e}")
            return False, f"Bulk fetch error: {str(e)}"
    
    def _fetch_recent_historical_data(self, city: str, state: str,
                                    latitude: float, longitude: float,
                                    existing_coverage: Dict) -> Tuple[bool, Optional[str]]:
        """Fetch recent historical data from OpenWeather"""
        try:
            # Check if we need recent data (last 7 days)
            now = datetime.now()
            cutoff_date = now - timedelta(days=self.config.recent_days_threshold)
            
            # Skip if we already have recent data that's fresh
            recent_range = existing_coverage.get('recent_date_range')
            if recent_range and recent_range[1] > (now - timedelta(days=1)):
                self.logger.info("Recent historical data is already up-to-date, skipping OpenWeather fetch")
                return True, None
            
            self.logger.info("Fetching recent historical data from OpenWeather...")
            
            # Fetch from OpenWeather (last 7 days)
            result = self.openweather_client.get_7day_history(latitude, longitude, city, state)
            # Handle the result format: ((df, error), success)
            if isinstance(result, tuple) and len(result) == 2:
                if isinstance(result[0], tuple):
                    df, error = result[0]
                else:
                    df, error = result
            else:
                df, error = result, None
            
            if error:
                return False, f"OpenWeather error: {error}"
            
            if df is None or df.empty:
                return False, "No recent historical data received"
            
            # Save to recent_historical_weather table (with replace logic)
            saved_count = 0
            for _, row in df.iterrows():
                if self.db.save_recent_historical_weather(city, state, row.to_dict()):
                    saved_count += 1
            
            self.logger.info(f"Saved {saved_count} recent historical records for {city}, {state}")
            return True, None
            
        except Exception as e:
            self.logger.error(f"Error fetching recent historical data: {e}")
            return False, f"Recent fetch error: {str(e)}"
    
    def _get_combined_historical_data(self, city: str, state: str) -> Optional[List[Dict]]:
        """Get combined historical data from both tables, with recent data taking precedence"""
        try:
            # Get bulk historical data (older than 7 days)
            cutoff_date = (datetime.now() - timedelta(days=self.config.recent_days_threshold)).strftime('%Y-%m-%d')
            
            bulk_data = self.db.get_historical_weather(
                city, state, 
                start_date='2010-01-01', 
                end_date=cutoff_date
            )
            
            # Get recent historical data (last 7 days)
            recent_start = (datetime.now() - timedelta(days=self.config.recent_days_threshold)).strftime('%Y-%m-%d')
            recent_end = datetime.now().strftime('%Y-%m-%d')
            
            recent_data = self.db.get_recent_historical_weather(
                city, state,
                start_date=recent_start,
                end_date=recent_end
            )
            
            # Combine the data (recent takes precedence for overlapping dates)
            combined_data = []
            recent_dates = {r['date'] for r in recent_data} if recent_data else set()
            
            # Add bulk data (excluding dates covered by recent data)
            if bulk_data:
                for record in bulk_data:
                    if record['date'] not in recent_dates:
                        combined_data.append(record)
            
            # Add recent data
            if recent_data:
                combined_data.extend(recent_data)
            
            # Sort by date
            combined_data.sort(key=lambda x: x['date'])
            
            self.logger.info(f"Combined data: {len(bulk_data or [])} bulk + {len(recent_data or [])} recent = {len(combined_data)} total records")
            
            return combined_data
            
        except Exception as e:
            self.logger.error(f"Error combining historical data: {e}")
            return None
    
    def has_sufficient_data_for_predictions(self, city: str, state: str) -> bool:
        """Check if we have sufficient combined data for predictions"""
        try:
            combined_data = self._get_combined_historical_data(city, state)
            return combined_data is not None and len(combined_data) >= 60
        except Exception:
            return False