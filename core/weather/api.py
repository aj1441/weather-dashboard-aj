"""Weather API client module with enhanced error handling and rate limiting"""

import requests
import time
import logging
from datetime import datetime
from functools import wraps
from typing import Dict, Optional, List, Any, Union
from config import Config
from core.weather.data_validator import WeatherDataValidator
from utils.decorators import rate_limit, retry_on_failure, log_execution_time
from utils.performance.performance_optimizer import monitor_performance, cache_api_response, connection_pool
from core.weather.open_meteo_client import OpenMeteoClient
from utils.fallback.fallback_utils import fallback_handler

class WeatherAPI:
    """Enhanced weather API client with rate limiting, retries, and data validation"""
    
    def __init__(self, config: Optional[Config] = None) -> None:
        # Use config object if provided, otherwise fall back to legacy approach
        if config:
            self.api_key = config.api_key
            self.base_url = config.base_url
            self.timeout = config.request_timeout
            self.units = config.units
            self.max_retries = config.max_retries
            self.min_request_interval = config.min_request_interval
        else:
            # Legacy fallback
            from config import API_KEY, BASE_URL, UNITS
            self.api_key = API_KEY
            self.base_url = BASE_URL
            self.timeout = 10
            self.units = UNITS
            self.max_retries = 3
            self.min_request_interval = 1.0
        
        # Use connection pool for better performance
        self.session = connection_pool.get_http_session()
        self.last_request_time = 0
        
        # Initialize data validator with correct temperature unit and logger
        self.validator = WeatherDataValidator(temperature_unit=self.units)
        self.logger = logging.getLogger(__name__)
        
        # Initialize fallback API client
        self.fallback_client = OpenMeteoClient(timeout=self.timeout)
        
        self.logger.info(f"WeatherAPI initialized with base_url={self.base_url}, units={self.units}")
    
    def _respect_rate_limit(self) -> None:
        """Ensure we don't exceed API rate limits"""
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    @monitor_performance("api_request")
    def _make_api_request(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a robust API request with retries and error handling"""
        self._respect_rate_limit()
        
        retry_delays = [1, 2, 4]  # Exponential backoff
        
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"API request attempt {attempt + 1}: {url}")
                self.logger.debug(f"API params: {params}")
                response = self.session.get(url, params=params, timeout=self.timeout)
                
                self.logger.debug(f"API response status: {response.status_code}")
                
                if response.status_code == 200:
                    json_data = response.json()
                    # Handle both dictionary and list responses
                    if isinstance(json_data, dict):
                        self.logger.debug(f"API response keys: {list(json_data.keys())}")
                    elif isinstance(json_data, list):
                        self.logger.debug(f"API response list length: {len(json_data)}")
                    else:
                        self.logger.debug(f"API response type: {type(json_data)}")
                    return json_data
                elif response.status_code == 401:
                    self.logger.error("Invalid API key")
                    return {"error": "API Error: Invalid API key or unauthorized access"}
                elif response.status_code == 404:
                    self.logger.warning("Location not found")
                    return {"error": "City not found"}
                elif response.status_code == 429:
                    self.logger.warning("Rate limited by API. Waiting...")
                    time.sleep(60)  # Wait 1 minute for rate limit reset
                    continue
                else:
                    self.logger.warning(f"API returned status {response.status_code}: {response.text}")
                    return {"error": f"API Error: Server returned status {response.status_code}"}
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    return {"error": "Connection timeout - please check your internet connection"}
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"Connection error (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    return {"error": "Connection error - please check your internet connection"}
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return {"error": f"Network error: {str(e)}"}
            
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries - 1:
                sleep_time = retry_delays[min(attempt, len(retry_delays) - 1)]
                self.logger.debug(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
        
        self.logger.error(f"Failed to fetch data after {self.max_retries} attempts")
        return {"error": "API request failed after multiple attempts - please try again later"}

    def _validate_basic_structure(self, data: Dict[str, Any]) -> bool:
        """Validate that the API response has the expected basic structure"""
        try:
            # Check for required top-level fields
            required_fields = ['name', 'main', 'weather']
            for field in required_fields:
                if field not in data:
                    self.logger.warning(f"Missing required field: {field}")
                    return False
            
            # Check main data structure
            main_data = data.get('main', {})
            if 'temp' not in main_data:
                self.logger.warning("Missing temperature data")
                return False
            
            # Check weather data structure
            weather_data = data.get('weather', [])
            if not weather_data or not isinstance(weather_data, list):
                self.logger.warning("Missing or invalid weather description data")
                return False
            
            if 'description' not in weather_data[0]:
                self.logger.warning("Missing weather description")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating API response structure: {e}")
            return False

    @rate_limit()
    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    @log_execution_time()
    @cache_api_response(ttl=300)  # Cache for 5 minutes
    @monitor_performance("fetch_weather")
    def fetch_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch weather data for a city (WeatherAPI.com format - legacy method)
        
        Args:
            city: Name of the city
            
        Returns:
            Dictionary with weather data or error dictionary
        """
        url = f"https://api.weatherapi.com/v1/current.json?key=demo&q={city}"

        try:
            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 404:
                return {"error": "City not found"}

            data = response.json()
            temp_k = data.get("current", {}).get("temp_k")

            if temp_k is None:
                return {"error": "No weather data"}

            description = data.get("current", {}).get("condition", {}).get("text", "No description")
            temp_c = round(temp_k - 273.15, 1)

            return {
                "city": city,
                "temp_c": temp_c,
                "description": description
            }

        except requests.exceptions.RequestException:
            return {"error": "Network error"}
        except Exception:
            return {"error": "Something went wrong"}

    def get_coordinates(self, city: str, state: str) -> Optional[Dict[str, Any]]:
        """
        Get latitude and longitude for a city using OpenWeatherMap Geocoding API
        
        Args:
            city: Name of the city
            state: State abbreviation
            
        Returns:
            Dictionary with lat, lon, and location info or error dictionary
        """
        geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            'q': f"{city},{state},US",
            'limit': 1,
            'appid': self.api_key
        }
        
        raw_data = self._make_api_request(geocoding_url, params)
        
        if raw_data and "error" not in raw_data:
            if raw_data and len(raw_data) > 0:
                location = raw_data[0]
                return {
                    'lat': location.get('lat'),
                    'lon': location.get('lon'),
                    'name': location.get('name', city),
                    'state': location.get('state', state),
                    'country': location.get('country', 'US')
                }
            else:
                return {"error": "City not found"}
        
        return raw_data

    @fallback_handler
    def fetch_current_weather(self, city: str, state: str, units: Optional[str] = None) -> Optional[Dict[str, Any]]:
        # This is a new or refactored method to centralize current weather fetching
        # (You may need to adapt this to your actual method signature and logic)
        params = {
            'q': f'{city},{state},US',
            'appid': self.api_key,
            'units': units or self.units
        }
        url = f"{self.base_url}"
        data = self._make_api_request(url, params)
        if data and "error" not in data:
            return data
        return {"error": "API request failed"}

    def fetch_comprehensive_weather(self, city: str, state: str, units: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch comprehensive weather data including current conditions and 7-day forecast
        using OpenWeatherMap APIs
        
        Args:
            city: Name of the city
            state: State abbreviation
            units: Temperature units (uses class default if not provided)
            
        Returns:
            Dictionary with current weather and forecast data or error dictionary
        """
        if units is None:
            units = self.units
        
        # First, get coordinates for the location
        coords = self.get_coordinates(city, state)
        if "error" in coords:
            return coords
        
        lat = coords['lat']
        lon = coords['lon']
        
        # Fetch current weather using coordinates
        current_weather_url = "https://api.openweathermap.org/data/2.5/weather"
        current_params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': units
        }
        
        current_data = self._make_api_request(current_weather_url, current_params)
        if "error" in current_data:
            return current_data
        
        # Validate and clean current weather data
        if not self._validate_basic_structure(current_data):
            return {"error": "Invalid current weather response structure"}
        
        cleaned_current = self.validator.validate_and_clean_current_weather(current_data)
        if not cleaned_current:
            return {"error": "Current weather data validation failed"}
        
        # Use Daily Forecast 16 Days API to get 7 days of forecast with POP values
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast/daily"
        
        # Get dedicated forecast API key if available
        import os
        forecast_api_key = os.getenv('7DAY_FORECAST_API_KEY', self.api_key)
        forecast_params = {
            'lat': lat,
            'lon': lon,
            'appid': forecast_api_key,
            'units': units,
            'cnt': 8  # Get 8 days to ensure we have 7 after excluding today
        }
        
        forecast_data = self._make_api_request(forecast_url, forecast_params)
        
        if forecast_data and "error" not in forecast_data:
            # Process daily forecast data from 16-day API
            daily_forecast = self._process_16day_daily_forecast(forecast_data)
            self.logger.info(f"Successfully fetched 16-day daily forecast with {len(daily_forecast)} days")
        else:
            # If daily forecast fails, try 5-day forecast as fallback
            self.logger.warning("16-day daily forecast unavailable, trying 5-day forecast as fallback")
            fallback_url = "https://api.openweathermap.org/data/2.5/forecast"
            fallback_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': units,
                'cnt': 40  # Get 40 3-hour forecasts (5 days * 8 forecasts per day)
            }
            
            fallback_data = self._make_api_request(fallback_url, fallback_params)
            if fallback_data and "error" not in fallback_data:
                daily_forecast = self._process_5day_forecast_to_daily(fallback_data)
                self.logger.info(f"Using 5-day forecast fallback with {len(daily_forecast)} days")
                
                # If we still don't have enough days, create placeholder forecasts
                if len(daily_forecast) < 7:
                    daily_forecast = self._extend_forecast_with_placeholders(daily_forecast, 7)
                    self.logger.info(f"Extended forecast to {len(daily_forecast)} days with placeholders")
            else:
                daily_forecast = []
                self.logger.warning("Both 16-day daily and 5-day forecasts unavailable")
        
        # Create comprehensive weather data structure
        comprehensive_data = {
            'current': {
                'temp': cleaned_current.get('temperature'),
                'feels_like': cleaned_current.get('feels_like'),
                'description': cleaned_current.get('weather_description'),
                'main': cleaned_current.get('weather_main'),
                'icon': cleaned_current.get('weather_icon'),
                'humidity': cleaned_current.get('humidity'),
                'pressure': cleaned_current.get('pressure'),
                'wind_speed': cleaned_current.get('wind_speed'),
                'wind_deg': cleaned_current.get('wind_direction'),
                'visibility': cleaned_current.get('visibility'),
                'uv_index': cleaned_current.get('uv_index'),
                'clouds': cleaned_current.get('cloudiness'),
                'dt': cleaned_current.get('api_timestamp'),
                'sunrise': cleaned_current.get('sunrise'),
                'sunset': cleaned_current.get('sunset')
            },
            'forecast': daily_forecast,
            'location': {
                'name': cleaned_current.get('city', city),
                'state': state,
                'country': cleaned_current.get('country', 'US'),
                'lat': lat,
                'lon': lon
            },
            'api_source': 'openweathermap_coords_based'
        }
        
        self.logger.info(f"Successfully fetched comprehensive weather data with {len(daily_forecast)} forecast days")
        return comprehensive_data

    def _process_16day_daily_forecast(self, forecast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process 16-day daily forecast data from OpenWeatherMap, excluding today to show 7 days starting tomorrow
        
        Args:
            forecast_data: Raw daily forecast data from API
            
        Returns:
            List of daily forecast summaries (7 days starting from tomorrow)
        """
        try:
            forecast_list = forecast_data.get('list', [])
            daily_forecast = []
            today_date = datetime.now().strftime('%Y-%m-%d')
            
            for item in forecast_list:
                # Get the date for this forecast item
                dt = item.get('dt')
                if dt:
                    forecast_date = datetime.fromtimestamp(dt).strftime('%Y-%m-%d')
                    
                    # Skip today's forecast
                    if forecast_date == today_date:
                        continue
                
                # Extract temperature data
                temp_data = item.get('temp', {})
                feels_like_data = item.get('feels_like', {})
                weather_data = item.get('weather', [{}])[0]
                
                daily_item = {
                    'dt': item.get('dt'),
                    'temp_min': round(temp_data.get('min', 0), 1) if temp_data.get('min') is not None else 0,
                    'temp_max': round(temp_data.get('max', 0), 1) if temp_data.get('max') is not None else 0,
                    'temp_day': round(temp_data.get('day', 0), 1) if temp_data.get('day') is not None else 0,
                    'temp_night': round(temp_data.get('night', 0), 1) if temp_data.get('night') is not None else 0,
                    'description': weather_data.get('description', '').title(),
                    'main': weather_data.get('main', ''),
                    'icon': weather_data.get('icon', ''),
                    'humidity': item.get('humidity'),
                    'pressure': item.get('pressure'),
                    'wind_speed': item.get('speed'),  # Wind speed field name in daily API
                    'wind_deg': item.get('deg'),      # Wind direction field name in daily API  
                    'clouds': item.get('clouds'),
                    'pop': item.get('pop', 0),        # Probability of precipitation (0-1 scale) - this is the key field!
                    'uv_index': None,                 # Not available in this API
                    'sunrise': item.get('sunrise'),
                    'sunset': item.get('sunset')
                }
                
                # Validate the forecast item
                validated_item = self.validator._validate_daily_forecast_day(daily_item)
                if validated_item:
                    daily_forecast.append(validated_item)
                else:
                    self.logger.warning(f"Forecast item validation failed for dt={item.get('dt')}")
                
                # Stop when we have 7 days (excluding today)
                if len(daily_forecast) >= 7:
                    break
            
            return daily_forecast
            
        except Exception as e:
            self.logger.error(f"Error processing 16-day daily forecast: {e}")
            return []

    def _process_daily_forecast(self, forecast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process 30-day climate forecast data, excluding today to show 7 days starting tomorrow
        
        Args:
            forecast_data: Raw climate forecast data from API
            
        Returns:
            List of daily forecast summaries (7 days starting from tomorrow)
        """
        try:
            forecast_list = forecast_data.get('list', [])
            daily_forecast = []
            today_date = datetime.now().strftime('%Y-%m-%d')
            
            for item in forecast_list:
                # Get the date for this forecast item
                dt = item.get('dt')
                if dt:
                    forecast_date = datetime.fromtimestamp(dt).strftime('%Y-%m-%d')
                    
                    # Skip today's forecast
                    if forecast_date == today_date:
                        continue
                
                # Extract temperature data
                temp_data = item.get('temp', {})
                feels_like_data = item.get('feels_like', {})
                weather_data = item.get('weather', [{}])[0]
                
                daily_item = {
                    'dt': item.get('dt'),
                    'temp_min': round(temp_data.get('min', 0), 1),
                    'temp_max': round(temp_data.get('max', 0), 1),
                    'temp_day': round(temp_data.get('day', 0), 1),
                    'temp_night': round(temp_data.get('night', 0), 1),
                    'description': weather_data.get('description', '').title(),
                    'main': weather_data.get('main', ''),
                    'icon': weather_data.get('icon', ''),
                    'humidity': item.get('humidity'),
                    'pressure': item.get('pressure'),
                    'wind_speed': item.get('speed'),  # Note: 'speed' not 'wind_speed' in climate API
                    'wind_deg': item.get('deg'),
                    'clouds': item.get('clouds'),
                    'pop': item.get('pop', 0),  # Probability of precipitation (0-1 scale)
                    'uv_index': None,  # Not available in this API
                    'sunrise': item.get('sunrise'),
                    'sunset': item.get('sunset')
                }
                daily_forecast.append(daily_item)
            
            return daily_forecast[:7]  # Return 7 days starting from tomorrow
            
        except Exception as e:
            self.logger.error(f"Error processing climate forecast: {e}")
            return []

    def _process_5day_forecast_to_daily(self, forecast_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process 5-day/3-hour forecast into daily summaries, excluding today to show 7 days starting tomorrow
        
        Args:
            forecast_data: Raw 5-day forecast data from API
            
        Returns:
            List of daily forecast summaries (up to 7 days starting from tomorrow)
        """
        try:
            forecast_list = forecast_data.get('list', [])
            daily_summaries = {}
            today_date = datetime.now().strftime('%Y-%m-%d')
            
            for item in forecast_list:
                # Get date (YYYY-MM-DD) from timestamp
                dt = item.get('dt')
                if dt:
                    date_str = datetime.fromtimestamp(dt).strftime('%Y-%m-%d')
                    
                    # Skip today's forecast
                    if date_str == today_date:
                        continue
                    
                    # Initialize day if not seen before
                    if date_str not in daily_summaries:
                        daily_summaries[date_str] = {
                            'dt': dt,
                            'temps': [],
                            'conditions': [],
                            'humidity': [],
                            'pressure': [],
                            'wind_speed': [],
                            'clouds': [],
                            'pop': 0,  # Max precipitation probability
                            'icons': []
                        }
                    
                    # Collect data for this day
                    main = item.get('main', {})
                    weather = item.get('weather', [{}])[0]
                    wind = item.get('wind', {})
                    clouds = item.get('clouds', {})
                    
                    daily_summaries[date_str]['temps'].append(main.get('temp', 0))
                    daily_summaries[date_str]['conditions'].append(weather.get('description', ''))
                    daily_summaries[date_str]['humidity'].append(main.get('humidity', 0))
                    daily_summaries[date_str]['pressure'].append(main.get('pressure', 0))
                    daily_summaries[date_str]['wind_speed'].append(wind.get('speed', 0))
                    daily_summaries[date_str]['clouds'].append(clouds.get('all', 0))
                    daily_summaries[date_str]['icons'].append(weather.get('icon', ''))
                    
                    # Track max precipitation probability
                    pop = item.get('pop', 0)
                    if pop > daily_summaries[date_str]['pop']:
                        daily_summaries[date_str]['pop'] = pop
            
            # Convert to daily forecast format
            daily_forecast = []
            for date_str, data in sorted(daily_summaries.items()):
                temps = data['temps']
                if temps:
                    # Most common condition and icon
                    most_common_condition = max(set(data['conditions']), key=data['conditions'].count)
                    most_common_icon = max(set(data['icons']), key=data['icons'].count)
                    
                    daily_item = {
                        'dt': data['dt'],
                        'temp_min': round(min(temps), 1),
                        'temp_max': round(max(temps), 1),
                        'temp_day': round(sum(temps) / len(temps), 1),
                        'temp_night': round(min(temps), 1),  # Approximation
                        'description': most_common_condition.title(),
                        'main': most_common_condition.split()[0].title(),
                        'icon': most_common_icon,
                        'humidity': round(sum(data['humidity']) / len(data['humidity'])) if data['humidity'] else None,
                        'pressure': round(sum(data['pressure']) / len(data['pressure'])) if data['pressure'] else None,
                        'wind_speed': round(sum(data['wind_speed']) / len(data['wind_speed']), 1) if data['wind_speed'] else None,
                        'wind_deg': None,  # Not available in this aggregation
                        'clouds': round(sum(data['clouds']) / len(data['clouds'])) if data['clouds'] else None,
                        'pop': data['pop'],
                        'uv_index': None,  # Not available in free API
                        'sunrise': None,
                        'sunset': None
                    }
                    daily_forecast.append(daily_item)
            
            # Return all available days (typically 4-5 days from 5-day forecast after excluding today)
            return daily_forecast
            
        except Exception as e:
            self.logger.error(f"Error processing 5-day forecast: {e}")
            return []

    def _extend_forecast_with_placeholders(self, existing_forecast: List[Dict[str, Any]], target_days: int) -> List[Dict[str, Any]]:
        """
        Extend forecast with intelligent predictions when API doesn't provide enough days
        
        Args:
            existing_forecast: List of existing forecast data
            target_days: Target number of days needed
            
        Returns:
            Extended forecast list with intelligent predictions
        """
        try:
            if len(existing_forecast) >= target_days:
                return existing_forecast[:target_days]
            
            extended_forecast = existing_forecast.copy()
            
            # Create intelligent forecasts for missing days
            days_needed = target_days - len(existing_forecast)
            
            if existing_forecast:
                # Use pattern from existing data to create reasonable forecasts
                last_day = existing_forecast[-1]
                
                # Calculate average conditions from existing forecast
                avg_temp_min = sum(day.get('temp_min', 70) for day in existing_forecast) / len(existing_forecast)
                avg_temp_max = sum(day.get('temp_max', 80) for day in existing_forecast) / len(existing_forecast)
                avg_humidity = sum(day.get('humidity', 50) for day in existing_forecast if day.get('humidity')) / len(existing_forecast)
                avg_pressure = sum(day.get('pressure', 1013) for day in existing_forecast if day.get('pressure')) / len(existing_forecast)
                
                # Get most common weather condition
                conditions = [day.get('main', 'Clear') for day in existing_forecast]
                most_common_condition = max(set(conditions), key=conditions.count)
                
                # Get most common icon
                icons = [day.get('icon', '01d') for day in existing_forecast]
                most_common_icon = max(set(icons), key=icons.count)
                
                for i in range(days_needed):
                    # Calculate the timestamp for this future day
                    days_ahead = len(extended_forecast) + 1
                    future_timestamp = int(datetime.now().timestamp() + (days_ahead * 24 * 60 * 60))
                    
                    # Add some variation to make it more realistic
                    temp_variation = (-2 + (i * 0.5)) if i < 4 else 0  # Small temperature trend
                    
                    placeholder_item = {
                        'dt': future_timestamp,
                        'temp_min': round(avg_temp_min + temp_variation, 1),
                        'temp_max': round(avg_temp_max + temp_variation, 1),
                        'temp_day': round((avg_temp_min + avg_temp_max) / 2 + temp_variation, 1),
                        'temp_night': round(avg_temp_min + temp_variation, 1),
                        'description': f'Predicted {most_common_condition}',
                        'main': most_common_condition,
                        'icon': most_common_icon,
                        'humidity': round(avg_humidity),
                        'pressure': round(avg_pressure),
                        'wind_speed': last_day.get('wind_speed', 5),
                        'wind_deg': last_day.get('wind_deg', 0),
                        'clouds': last_day.get('clouds', 20),
                        'pop': 0.1,  # Low probability for predicted days
                        'uv_index': None,
                        'sunrise': None,
                        'sunset': None
                    }
                    
                    extended_forecast.append(placeholder_item)
            else:
                # Create basic placeholders when no existing forecast data
                for i in range(days_needed):
                    future_timestamp = int(datetime.now().timestamp() + ((i + 1) * 24 * 60 * 60))
                    
                    placeholder_item = {
                        'dt': future_timestamp,
                        'temp_min': 70,
                        'temp_max': 80,
                        'temp_day': 75,
                        'temp_night': 65,
                        'description': 'Forecast Unavailable',
                        'main': 'Unknown',
                        'icon': '01d',
                        'humidity': 50,
                        'pressure': 1013,
                        'wind_speed': 5,
                        'wind_deg': 0,
                        'clouds': 20,
                        'pop': 0,
                        'uv_index': None,
                        'sunrise': None,
                        'sunset': None
                    }
                    
                    extended_forecast.append(placeholder_item)
            
            return extended_forecast
            
        except Exception as e:
            self.logger.error(f"Error extending forecast with placeholders: {e}")
            return existing_forecast

    @rate_limit()
    @retry_on_failure()
    @log_execution_time()
   

    @staticmethod
    def _convert_temperature(temp: float, from_unit: str, to_unit: str) -> float:
        """Convert temperature between units
        
        Args:
            temp: Temperature value to convert
            from_unit: Current unit ('imperial', 'metric')
            to_unit: Target unit ('imperial', 'metric')
            
        Returns:
            Converted temperature value
        """
        if from_unit == to_unit or temp is None:
            return temp
            
        if from_unit == 'imperial' and to_unit == 'metric':
            return round((temp - 32) * 5/9, 1)  # F to C
        elif from_unit == 'metric' and to_unit == 'imperial':
            return round((temp * 9/5) + 32, 1)  # C to F
        return temp


