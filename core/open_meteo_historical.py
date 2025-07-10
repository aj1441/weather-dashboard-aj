"""Historical weather data client using Open-Meteo Archive API"""

import logging
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class OpenMeteoHistorical:
    """Client for fetching historical weather data from Open-Meteo Archive API"""
    
    def __init__(self):
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)  # Cache for 1 hour
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=retry_session)
        self.api_url = "https://archive-api.open-meteo.com/v1/archive"
    
    def get_historical_data(
        self,
        latitude: float,
        longitude: float,
        timezone: str = "America/Los_Angeles"
    ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Fetch historical weather data for a location.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            timezone: Timezone string (default: America/Los_Angeles)
            
        Returns:
            Tuple of (DataFrame with weather data, error message if any)
        """
        try:
            # Fixed start date and calculate end date (6 days before current date)
            end_date = datetime.now() - timedelta(days=6)
            
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": "2010-01-01",
                "end_date": end_date.strftime("%Y-%m-%d"),
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "sunrise",
                    "sunset",
                    "precipitation_sum",
                    "rain_sum",
                    "temperature_2m_mean",
                    "wind_speed_10m_max",
                    "wind_gusts_10m_max",
                    "cloud_cover_mean",
                    "relative_humidity_2m_mean"
                ],
                "timezone": timezone,
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch"
            }
            
            responses = self.client.weather_api(self.api_url, params=params)
            
            if not responses:
                return None, "No data received from API"
                
            # Process first location response
            response = responses[0]
            
            # Process daily data
            daily = response.Daily()
            daily_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left"
                )
            }
            
            # Map all variables to the dataframe
            variables = [
                "temperature_2m_max",
                "temperature_2m_min",
                "sunrise",
                "sunset",
                "precipitation_sum",
                "rain_sum",
                "temperature_2m_mean",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "cloud_cover_mean",
                "relative_humidity_2m_mean"
            ]
            
            for idx, var in enumerate(variables):
                daily_data[var] = daily.Variables(idx).ValuesAsNumpy()
            
            df = pd.DataFrame(data=daily_data)
            
            # Add metadata
            df['latitude'] = response.Latitude()
            df['longitude'] = response.Longitude()
            df['elevation'] = response.Elevation()
            df['timezone'] = response.Timezone()
            
            return df, None
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            return None, f"Failed to fetch historical data: {str(e)}"
    
    def clean_historical_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate historical weather data
        
        Args:
            df: Raw DataFrame from the API
            
        Returns:
            Cleaned DataFrame ready for database insertion
        """
        if df is None:
            return None
            
        try:
            # Convert temperatures to proper format
            temp_columns = [
                'temperature_2m_max',
                'temperature_2m_min',
                'temperature_2m_mean'
            ]
            for col in temp_columns:
                df[col] = df[col].round(1)
            
            # Convert wind speeds
            wind_columns = ['wind_speed_10m_max', 'wind_gusts_10m_max']
            for col in wind_columns:
                df[col] = df[col].round(1)
            
            # Convert precipitation to 2 decimal places
            precip_columns = ['precipitation_sum', 'rain_sum']
            for col in precip_columns:
                df[col] = df[col].round(2)
            
            # Convert cloud cover and humidity to integers
            df['cloud_cover_mean'] = df['cloud_cover_mean'].round().astype(int)
            df['relative_humidity_2m_mean'] = df['relative_humidity_2m_mean'].round().astype(int)
            
            # Convert dates to string format in YYYY-MM-DD format for SQLite compatibility
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning historical data: {str(e)}")
            return None
