"""Coordinator for historical weather data operations"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from .open_meteo_historical import OpenMeteoHistorical
from .db_data_handler import DatabaseDataHandler

logger = logging.getLogger(__name__)

class HistoricalDataCoordinator:
    """Coordinates fetching, validating, and storing historical weather data"""
    
    def __init__(self):
        self.api_client = OpenMeteoHistorical()
        self.data_handler = DatabaseDataHandler()
        
    def fetch_and_store_historical_data(
        self,
        city: str,
        state: str,
        latitude: float,
        longitude: float,
        days_back: int = 30
    ) -> Tuple[bool, Optional[str]]:
        """
        Fetch historical data for a location and store it
        
        Args:
            city: City name
            state: State abbreviation
            latitude: Location latitude
            longitude: Location longitude
            days_back: Number of days of historical data to fetch
            
        Returns:
            Tuple of (success status, error message if any)
        """
        try:
            # Fetch data from API (start_date and end_date are handled internally)
            historical_df, error = self.api_client.get_historical_data(
                latitude=latitude,
                longitude=longitude
            )
            
            if error:
                return False, error
                
            if historical_df is None:
                return False, "No data received from API"
            
            # Clean and validate the data
            cleaned_df = self.api_client.clean_historical_data(historical_df)
            if cleaned_df is None:
                return False, "Failed to clean historical data"
            
            # Store in database
            if not self.data_handler.save_historical_data(city, state, cleaned_df):
                return False, "Failed to save historical data to database"
            
            return True, None
            
        except Exception as e:
            error_msg = f"Error processing historical data: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
            
    def get_historical_data(
        self,
        city: str,
        state: str,
        days_back: int = 30
    ) -> Tuple[List[Dict], Optional[str]]:
        """
        Retrieve historical data for a city
        
        Args:
            city: City name
            state: State abbreviation
            days_back: Number of days of historical data to retrieve
            
        Returns:
            Tuple of (list of historical data records, error message if any)
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            data = self.data_handler.get_historical_data(
                city=city,
                state=state,
                start_date=start_date,
                end_date=end_date
            )
            
            if not data:
                return [], "No historical data found"
                
            return data, None
            
        except Exception as e:
            error_msg = f"Error retrieving historical data: {str(e)}"
            logger.error(error_msg)
            return [], error_msg
