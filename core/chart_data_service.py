"""Chart data service for historical weather visualization"""

import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from .historical_coordinator import HistoricalDataCoordinator
from .database import get_database

logger = logging.getLogger(__name__)

class ChartDataService:
    """Service for preparing historical weather data for chart visualization"""
    
    def __init__(self):
        self.historical_coordinator = HistoricalDataCoordinator()
        self.db = get_database()
        
    def get_chart_data(
        self, 
        city1_info: Dict, 
        city2_info: Optional[Dict] = None, 
        days_back: int = 7,
        use_recent_data: bool = False
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Get processed data ready for chart display
        
        Args:
            city1_info: Dict with city, state, display_name keys
            city2_info: Optional second city for comparison
            days_back: Number of days to retrieve
            use_recent_data: If True, use recent_historical_weather table instead
            
        Returns:
            Tuple of (chart_data_dict, error_message)
        """
        try:
            if use_recent_data:
                # Get recent historical data from OpenWeatherMap History API table
                city1_data = self._get_recent_historical_data(
                    city1_info['city'], 
                    city1_info['state'], 
                    days_back
                )
                
                if not city1_data:
                    return None, f"No recent historical data available for {city1_info['display_name']}"
                
                # Get data for city2 if provided
                city2_data = []
                if city2_info:
                    city2_data = self._get_recent_historical_data(
                        city2_info['city'], 
                        city2_info['state'], 
                        days_back
                    )
                    if not city2_data:
                        return None, f"No recent historical data available for {city2_info['display_name']}"
            else:
                # Use existing historical coordinator (original long-term data)
                city1_data, error1 = self.historical_coordinator.get_historical_data(
                    city1_info['city'], 
                    city1_info['state'], 
                    days_back
                )
                
                if error1:
                    return None, f"Error fetching data for {city1_info['display_name']}: {error1}"
                
                # Get data for city2 if provided
                city2_data = []
                if city2_info:
                    city2_data, error2 = self.historical_coordinator.get_historical_data(
                        city2_info['city'], 
                        city2_info['state'], 
                        days_back
                    )
                    if error2:
                        return None, f"Error fetching data for {city2_info['display_name']}: {error2}"
            
            # Process data for charts
            chart_data = self._prepare_chart_data(
                city1_data, city1_info, 
                city2_data, city2_info
            )
            
            return chart_data, None
            
        except Exception as e:
            error_msg = f"Error preparing chart data: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def _prepare_chart_data(
        self, 
        city1_data: List[Dict], 
        city1_info: Dict,
        city2_data: List[Dict], 
        city2_info: Optional[Dict]
    ) -> Dict:
        """Process raw data into chart-ready format"""
        try:
            # Convert to DataFrames for easier processing
            df1 = pd.DataFrame(city1_data) if city1_data else pd.DataFrame()
            df2 = pd.DataFrame(city2_data) if city2_data else pd.DataFrame()
            
            # Ensure we have data
            if df1.empty:
                return {
                    'city1': {'data': [], 'info': city1_info, 'processed': {}},
                    'city2': None,
                    'chart_ready': False
                }
            
            # Sort by date
            df1 = df1.sort_values('date') if 'date' in df1.columns else df1
            if not df2.empty:
                df2 = df2.sort_values('date') if 'date' in df2.columns else df2
            
            # Prepare processed data for each chart type
            city1_processed = self._process_city_data(df1)
            city2_processed = self._process_city_data(df2) if not df2.empty else {}
            
            return {
                'city1': {
                    'data': city1_data, 
                    'info': city1_info,
                    'processed': city1_processed
                },
                'city2': {
                    'data': city2_data, 
                    'info': city2_info,
                    'processed': city2_processed
                } if city2_info and not df2.empty else None,
                'chart_ready': True
            }
            
        except Exception as e:
            logger.error(f"Error processing chart data: {e}")
            return {
                'city1': {'data': city1_data, 'info': city1_info, 'processed': {}},
                'city2': None,
                'chart_ready': False,
                'error': str(e)
            }
    
    def _process_city_data(self, df: pd.DataFrame) -> Dict:
        """Extract chart-specific data from DataFrame"""
        if df.empty:
            return {}
            
        try:
            # Temperature data
            temp_data = {
                'dates': df['date'].tolist() if 'date' in df.columns else [],
                'max_temps': df['temperature_max'].fillna(0).tolist() if 'temperature_max' in df.columns else [],
                'min_temps': df['temperature_min'].fillna(0).tolist() if 'temperature_min' in df.columns else [],
                'mean_temps': df['temperature_mean'].fillna(0).tolist() if 'temperature_mean' in df.columns else []
            }
            
            # Precipitation data
            precip_data = {
                'dates': df['date'].tolist() if 'date' in df.columns else [],
                'precipitation': df['precipitation'].fillna(0).tolist() if 'precipitation' in df.columns else [],
                'rain': df['rain'].fillna(0).tolist() if 'rain' in df.columns else []
            }
            
            # Humidity data
            humidity_data = {
                'dates': df['date'].tolist() if 'date' in df.columns else [],
                'humidity': df['humidity'].fillna(0).tolist() if 'humidity' in df.columns else []
            }
            
            # Weather type data
            weather_data = self._categorize_weather_types(df)
            
            return {
                'temperature': temp_data,
                'precipitation': precip_data,
                'humidity': humidity_data,
                'weather_types': weather_data
            }
            
        except Exception as e:
            logger.error(f"Error processing city data: {e}")
            return {}
    
    def _categorize_weather_types(self, df: pd.DataFrame) -> Dict:
        """Categorize weather types based on data"""
        categories = ['Clear', 'Cloudy', 'Rainy', 'Stormy', 'Snowy', 'Foggy']
        counts = {cat: 0 for cat in categories}
        
        try:
            for _, row in df.iterrows():
                cloud_cover = row.get('cloud_cover', 0) or 0
                precipitation = row.get('precipitation', 0) or 0
                rain = row.get('rain', 0) or 0
                
                # Categorization logic
                if precipitation > 5 or rain > 5:
                    if precipitation > 15:  # Heavy rain could indicate storms
                        counts['Stormy'] += 1
                    else:
                        counts['Rainy'] += 1
                elif cloud_cover > 80:
                    counts['Cloudy'] += 1
                elif cloud_cover < 20:
                    counts['Clear'] += 1
                else:
                    counts['Cloudy'] += 1
            
            # Convert to percentages
            total = len(df) if len(df) > 0 else 1
            percentages = {cat: (count / total) * 100 for cat, count in counts.items()}
            
            return {
                'categories': categories,
                'counts': counts,
                'percentages': percentages
            }
            
        except Exception as e:
            logger.error(f"Error categorizing weather types: {e}")
            return {
                'categories': categories,
                'counts': counts,
                'percentages': {cat: 0 for cat in categories}
            }
    
    def _get_recent_historical_data(self, city: str, state: str, days_back: int) -> List[Dict]:
        """
        Get recent historical data from the recent_historical_weather table
        
        Args:
            city: City name
            state: State code
            days_back: Number of days back to retrieve
            
        Returns:
            List of weather data dictionaries
        """
        try:
            from datetime import datetime, timedelta
            
            # Calculate date range
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)
            
            # Get recent historical data
            data = self.db.get_recent_historical_weather(
                city, 
                state, 
                start_date.strftime('%Y-%m-%d'), 
                end_date.strftime('%Y-%m-%d')
            )
            
            logger.info(f"Retrieved {len(data)} recent historical records for {city}, {state}")
            return data
            
        except Exception as e:
            logger.error(f"Error retrieving recent historical data: {e}")
            return []