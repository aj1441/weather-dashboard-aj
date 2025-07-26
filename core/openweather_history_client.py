"""OpenWeatherMap History API client for recent historical weather data"""

import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import Config

logger = logging.getLogger(__name__)

class OpenWeatherHistoryClient:
    """Client for fetching recent historical weather data from OpenWeatherMap History API"""
    
    def __init__(self, config: Config = None):
        if config is None:
            config = Config.from_environment()
        
        self.api_key = config.api_key
        self.base_url = config.seven_day_history_url
        self.timeout = config.request_timeout
        
    def get_7day_history(
        self, 
        latitude: float, 
        longitude: float, 
        city: str = None, 
        state: str = None
    ) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Fetch 7 days of recent historical weather data
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            city: City name for metadata
            state: State name for metadata
            
        Returns:
            Tuple of (DataFrame with weather data, error message if any)
        """
        try:
            # Calculate time range (last 7 days)
            end_time = datetime.now()
            start_time = end_time - timedelta(days=7)
            
            # Convert to Unix timestamps
            start_unix = int(start_time.timestamp())
            end_unix = int(end_time.timestamp())
            
            params = {
                "lat": latitude,
                "lon": longitude,
                "type": "hour",
                "start": start_unix,
                "end": end_unix,
                "units": "imperial",  # Fahrenheit, mph
                "appid": self.api_key
            }
            
            logger.info(f"Fetching 7-day history for {city}, {state} from {start_time.date()} to {end_time.date()}")
            
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("cod") != "200":
                return None, f"API Error: {data.get('message', 'Unknown error')}"
            
            # Process hourly data into daily aggregates
            df = self._process_hourly_to_daily(data, city, state, latitude, longitude)
            
            return df, None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching OpenWeather history: {e}")
            return None, f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Error fetching OpenWeather history: {e}")
            return None, f"Failed to fetch historical data: {str(e)}"
    
    def _process_hourly_to_daily(
        self, 
        data: Dict, 
        city: str, 
        state: str, 
        latitude: float, 
        longitude: float
    ) -> pd.DataFrame:
        """Convert hourly data to daily aggregates matching the database schema"""
        
        hourly_data = data.get("list", [])
        if not hourly_data:
            return pd.DataFrame()
        
        # Group by date
        daily_groups = {}
        
        for hour_data in hourly_data:
            # Convert Unix timestamp to date
            dt = datetime.fromtimestamp(hour_data["dt"])
            date_str = dt.strftime("%Y-%m-%d")
            
            if date_str not in daily_groups:
                daily_groups[date_str] = []
            
            daily_groups[date_str].append(hour_data)
        
        # Aggregate daily data
        daily_records = []
        
        for date_str, hours in daily_groups.items():
            # Extract all temperature values for the day
            temps = [h["main"]["temp"] for h in hours if "main" in h and "temp" in h["main"]]
            humidity_vals = [h["main"]["humidity"] for h in hours if "main" in h and "humidity" in h["main"]]
            wind_speeds = [h["wind"]["speed"] for h in hours if "wind" in h and "speed" in h["wind"]]
            wind_gusts = [h["wind"].get("gust", 0) for h in hours if "wind" in h]
            cloud_cover_vals = [h["clouds"]["all"] for h in hours if "clouds" in h and "all" in h["clouds"]]
            
            # Calculate precipitation (rain + snow)
            precip_vals = []
            rain_vals = []
            
            for h in hours:
                rain = h.get("rain", {}).get("1h", 0) or 0
                snow = h.get("snow", {}).get("1h", 0) or 0
                precip_vals.append(rain + snow)
                rain_vals.append(rain)
            
            # Aggregate values
            record = {
                "city": city,
                "state": state,
                "date": date_str,
                "temperature_max": max(temps) if temps else None,
                "temperature_min": min(temps) if temps else None,
                "temperature_mean": sum(temps) / len(temps) if temps else None,
                "precipitation": sum(precip_vals) if precip_vals else 0,
                "rain": sum(rain_vals) if rain_vals else 0,
                "wind_speed_max": max(wind_speeds) if wind_speeds else None,
                "wind_gusts_max": max(wind_gusts) if wind_gusts else None,
                "cloud_cover": int(sum(cloud_cover_vals) / len(cloud_cover_vals)) if cloud_cover_vals else None,
                "humidity": int(sum(humidity_vals) / len(humidity_vals)) if humidity_vals else None,
                "latitude": latitude,
                "longitude": longitude,
                "sunrise": None,  # Not available in hourly history API
                "sunset": None    # Not available in hourly history API
            }
            
            daily_records.append(record)
        
        # Create DataFrame and sort by date
        df = pd.DataFrame(daily_records)
        if not df.empty:
            df = df.sort_values("date")
        
        return df
    
    def save_to_database(self, df: pd.DataFrame, database) -> Tuple[int, Optional[str]]:
        """
        Save recent historical data to the database using WeatherDatabase methods
        
        Args:
            df: DataFrame with recent historical weather data
            database: WeatherDatabase instance
            
        Returns:
            Tuple of (records_inserted, error_message)
        """
        if df.empty:
            return 0, "No data to save"
        
        try:
            records_inserted = 0
            
            for _, row in df.iterrows():
                success = database.save_recent_historical_weather(
                    row['city'], 
                    row['state'], 
                    row.to_dict()
                )
                if success:
                    records_inserted += 1
                else:
                    logger.warning(f"Failed to save record for {row['city']}, {row['state']} on {row['date']}")
            
            logger.info(f"Inserted {records_inserted} recent historical weather records")
            return records_inserted, None
            
        except Exception as e:
            logger.error(f"Error saving recent historical data: {e}")
            return 0, f"Error saving data: {str(e)}"