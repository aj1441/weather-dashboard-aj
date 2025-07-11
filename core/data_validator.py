"""Weather data validation and cleaning utilities"""

import logging
from datetime import datetime
from typing import Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class ValidationRules:
    """Configuration for weather data validation rules"""
    
    # Temperature ranges for different units
    # Celsius ranges
    min_temperature_celsius: float = -60.0
    max_temperature_celsius: float = 60.0
    
    # Fahrenheit ranges  
    min_temperature_fahrenheit: float = -76.0  # -60°C in Fahrenheit
    max_temperature_fahrenheit: float = 140.0  # 60°C in Fahrenheit
    
    # Kelvin ranges
    min_temperature_kelvin: float = 213.15  # -60°C in Kelvin
    max_temperature_kelvin: float = 333.15  # 60°C in Kelvin
    
    # Default unit for validation (imperial = Fahrenheit, metric = Celsius)
    temperature_unit: str = "imperial"
    
    # Humidity range (percentage)
    min_humidity: int = 0
    max_humidity: int = 100
    
    # Pressure range (hPa)
    min_pressure: float = 800.0
    max_pressure: float = 1200.0
    
    # Wind speed range (m/s for metric, mph for imperial)
    max_wind_speed_metric: float = 200.0  # m/s
    max_wind_speed_imperial: float = 450.0  # mph
    
    # Visibility range (meters)
    max_visibility: int = 50000

    # No special initialization needed by default

class WeatherDataValidator:
    """Validates and cleans weather data from API responses"""
    
    def __init__(self, rules: ValidationRules = None, temperature_unit: str = "imperial"):
        self.rules = rules or ValidationRules()
        self.temperature_unit = temperature_unit
        self.logger = logging.getLogger(__name__)
    
    def validate_and_clean_current_weather(self, raw_data: Dict) -> Optional[Dict]:
        """
        Validate and clean current weather data from OpenWeatherMap API
        
        Args:
            raw_data: Raw JSON response from weather API
            
        Returns:
            Cleaned and validated weather data, or None if validation fails
        """
        try:
            # Extract required fields with error handling
            main_data = raw_data.get('main', {})
            weather_data = raw_data.get('weather', [{}])[0]
            wind_data = raw_data.get('wind', {})
            clouds_data = raw_data.get('clouds', {})
            sys_data = raw_data.get('sys', {})
            coord_data = raw_data.get('coord', {})
            
            # Build cleaned data structure
            cleaned_data = {
                # Metadata
                'timestamp': datetime.now().isoformat(),
                'api_timestamp': self._convert_unix_timestamp(raw_data.get('dt')),
                
                # Location data
                'city': self._clean_string(raw_data.get('name')),
                'country': self._clean_string(sys_data.get('country')),
                'latitude': self._clean_float(coord_data.get('lat')),
                'longitude': self._clean_float(coord_data.get('lon')),
                
                # Temperature data
                'temperature': self._clean_float(main_data.get('temp')),
                'feels_like': self._clean_float(main_data.get('feels_like')),
                'temp_min': self._clean_float(main_data.get('temp_min')),
                'temp_max': self._clean_float(main_data.get('temp_max')),
                
                # Atmospheric data
                'humidity': self._clean_int(main_data.get('humidity')),
                'pressure': self._clean_float(main_data.get('pressure')),
                'sea_level': self._clean_float(main_data.get('sea_level')),
                'ground_level': self._clean_float(main_data.get('grnd_level')),
                
                # Weather description
                'weather_main': self._clean_string(weather_data.get('main')),
                'weather_description': self._clean_string(weather_data.get('description')),
                'weather_icon': self._clean_string(weather_data.get('icon')),
                
                # Wind data
                'wind_speed': self._clean_float(wind_data.get('speed')),
                'wind_direction': self._clean_int(wind_data.get('deg')),
                'wind_gust': self._clean_float(wind_data.get('gust')),
                
                # Other data
                'cloudiness': self._clean_int(clouds_data.get('all')),
                'visibility': self._clean_int(raw_data.get('visibility', 10000)),
                'uv_index': self._clean_float(raw_data.get('uvi')),
                
                # Timestamps
                'sunrise': self._convert_unix_timestamp(sys_data.get('sunrise')),
                'sunset': self._convert_unix_timestamp(sys_data.get('sunset')),
            }
            
            # Validate the cleaned data
            if self._validate_weather_data(cleaned_data):
                return cleaned_data
            else:
                self.logger.warning("Weather data failed validation")
                return None
                
        except Exception as e:
            self.logger.error(f"Error cleaning weather data: {e}")
            return None
    
    def _clean_string(self, value: Any) -> Optional[str]:
        """Clean and validate string values"""
        if value is None:
            return None
        return str(value).strip() if str(value).strip() else None
    
    def _clean_float(self, value: Any) -> Optional[float]:
        """Clean and validate float values"""
        if value is None:
            return None
        try:
            result = float(value)
            return result if not (result != result) else None  # Check for NaN
        except (ValueError, TypeError):
            return None
    
    def _clean_int(self, value: Any) -> Optional[int]:
        """Clean and validate integer values"""
        if value is None:
            return None
        try:
            return int(float(value))  # Handle string numbers
        except (ValueError, TypeError):
            return None
    
    def _convert_unix_timestamp(self, timestamp: Any) -> Optional[str]:
        """Convert Unix timestamp to ISO format"""
        if timestamp is None:
            return None
        try:
            return datetime.fromtimestamp(int(timestamp)).isoformat()
        except (ValueError, TypeError, OSError):
            return None
    
    def _validate_weather_data(self, data: Dict) -> bool:
        """Validate cleaned weather data against reasonable ranges"""
        
        # Check required fields
        required_fields = ['city', 'temperature', 'weather_description']
        for field in required_fields:
            if not data.get(field):
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate temperature with correct units
        temp = data.get('temperature')
        if temp is not None:
            if self.temperature_unit == "imperial":
                min_temp = self.rules.min_temperature_fahrenheit
                max_temp = self.rules.max_temperature_fahrenheit
                temp_unit = "°F"
            elif self.temperature_unit == "metric":
                min_temp = self.rules.min_temperature_celsius
                max_temp = self.rules.max_temperature_celsius
                temp_unit = "°C"
            else:  # kelvin
                min_temp = self.rules.min_temperature_kelvin
                max_temp = self.rules.max_temperature_kelvin
                temp_unit = "K"
            
            if not (min_temp <= temp <= max_temp):
                self.logger.warning(f"Temperature out of range: {temp}{temp_unit} (expected {min_temp}-{max_temp})")
                return False
        
        # Validate humidity
        humidity = data.get('humidity')
        if humidity is not None:
            if not (self.rules.min_humidity <= humidity <= self.rules.max_humidity):
                self.logger.warning(f"Humidity out of range: {humidity}%")
                return False
        
        # Validate pressure
        pressure = data.get('pressure')
        if pressure is not None:
            if not (self.rules.min_pressure <= pressure <= self.rules.max_pressure):
                self.logger.warning(f"Pressure out of range: {pressure} hPa")
                return False
        
        # Validate wind speed with correct units
        wind_speed = data.get('wind_speed')
        if wind_speed is not None:
            if self.temperature_unit == "imperial":
                max_wind = self.rules.max_wind_speed_imperial
                wind_unit = "mph"
            else:  # metric
                max_wind = self.rules.max_wind_speed_metric
                wind_unit = "m/s"
            
            if wind_speed > max_wind:
                self.logger.warning(f"Wind speed out of range: {wind_speed} {wind_unit}")
                return False
        
        return True
    
    def validate_forecast_data(self, raw_forecast_list: list) -> list:
        """
        Validate and clean forecast data (for future 7-day forecast feature)
        
        Args:
            raw_forecast_list: List of forecast periods from API
            
        Returns:
            List of cleaned forecast data
        """
        cleaned_forecasts = []
        
        for forecast_item in raw_forecast_list:
            try:
                cleaned_item = {
                    'date': self._convert_unix_timestamp(forecast_item.get('dt')),
                    'temperature_day': self._clean_float(forecast_item.get('temp', {}).get('day')),
                    'temperature_night': self._clean_float(forecast_item.get('temp', {}).get('night')),
                    'temperature_min': self._clean_float(forecast_item.get('temp', {}).get('min')),
                    'temperature_max': self._clean_float(forecast_item.get('temp', {}).get('max')),
                    'humidity': self._clean_int(forecast_item.get('humidity')),
                    'pressure': self._clean_float(forecast_item.get('pressure')),
                    'weather_main': self._clean_string(forecast_item.get('weather', [{}])[0].get('main')),
                    'weather_description': self._clean_string(forecast_item.get('weather', [{}])[0].get('description')),
                    'precipitation_probability': self._clean_float(forecast_item.get('pop')),
                    'wind_speed': self._clean_float(forecast_item.get('wind_speed')),
                    'cloudiness': self._clean_int(forecast_item.get('clouds')),
                    'uv_index': self._clean_float(forecast_item.get('uvi')),
                }
                
                # Basic validation for forecast data
                if cleaned_item['date'] and cleaned_item['weather_description']:
                    cleaned_forecasts.append(cleaned_item)
                    
            except Exception as e:
                self.logger.warning(f"Skipping invalid forecast item: {e}")
                continue
        
        return cleaned_forecasts
    
    def validate_and_clean_one_call_weather(self, data: Dict) -> Optional[Dict]:
        """
        Validate and clean One Call API weather data (current + forecast)
        
        Args:
            data: Raw weather data from OpenWeatherMap One Call API
            
        Returns:
            Cleaned and validated weather data with current and forecast, or None if invalid
        """
        try:
            if not isinstance(data, dict):
                self.logger.warning("Weather data is not a dictionary")
                return None
            
            # Validate current weather data
            current_data = data.get('current')
            if not current_data:
                self.logger.warning("Missing current weather data in One Call response")
                return None
            
            # Extract and validate current weather
            current_cleaned = self._extract_and_validate_current_from_one_call(current_data)
            if not current_cleaned:
                return None
            
            # Extract and validate daily forecast
            daily_data = data.get('daily', [])
            forecast_cleaned = self._extract_and_validate_daily_forecast(daily_data)
            
            # Get timezone info
            timezone_offset = data.get('timezone_offset', 0)
            timezone = data.get('timezone', 'UTC')
            
            # Combine all data
            result = {
                'current': current_cleaned,
                'forecast': forecast_cleaned,
                'timezone': timezone,
                'timezone_offset': timezone_offset,
                'api_source': 'openweathermap_one_call'
            }
            
            self.logger.info(f"Successfully validated One Call weather data with {len(forecast_cleaned)} forecast days")
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating One Call weather data: {e}")
            return None
    
    def _extract_and_validate_current_from_one_call(self, current_data: Dict) -> Optional[Dict]:
        """Extract and validate current weather from One Call API format"""
        try:
            # Temperature data
            temp = current_data.get('temp')
            feels_like = current_data.get('feels_like')
            
            if not self._is_valid_temperature(temp):
                self.logger.warning(f"Invalid current temperature: {temp}")
                return None
            
            # Weather description
            weather_list = current_data.get('weather', [])
            if not weather_list:
                self.logger.warning("Missing weather description in current data")
                return None
            
            weather_info = weather_list[0]
            description = weather_info.get('description', '').title()
            main_weather = weather_info.get('main', '')
            icon = weather_info.get('icon', '')
            
            # Additional current weather data
            humidity = current_data.get('humidity')
            pressure = current_data.get('pressure')
            wind_speed = current_data.get('wind_speed')
            wind_deg = current_data.get('wind_deg')
            visibility = current_data.get('visibility')
            uv_index = current_data.get('uvi')
            clouds = current_data.get('clouds')
            
            # Validate key metrics
            if not self._is_valid_humidity(humidity):
                humidity = None
            if not self._is_valid_pressure(pressure):
                pressure = None
            if not self._is_valid_wind_speed(wind_speed):
                wind_speed = None
            
            return {
                'temp': round(temp, 1),
                'feels_like': round(feels_like, 1) if feels_like is not None else None,
                'description': description,
                'main': main_weather,
                'icon': icon,
                'humidity': humidity,
                'pressure': pressure,
                'wind_speed': wind_speed,
                'wind_deg': wind_deg,
                'visibility': visibility,
                'uv_index': uv_index,
                'clouds': clouds,
                'dt': current_data.get('dt'),
                'sunrise': current_data.get('sunrise'),
                'sunset': current_data.get('sunset')
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting current weather from One Call data: {e}")
            return None
    
    def _extract_and_validate_daily_forecast(self, daily_data: list) -> list:
        """Extract and validate daily forecast from One Call API format"""
        try:
            forecast_list = []
            
            for day_data in daily_data[:7]:  # Limit to 7 days
                day_forecast = self._validate_daily_forecast_day(day_data)
                if day_forecast:
                    forecast_list.append(day_forecast)
            
            return forecast_list
            
        except Exception as e:
            self.logger.error(f"Error extracting daily forecast: {e}")
            return []
    
    def _validate_daily_forecast_day(self, day_data: Dict) -> Optional[Dict]:
        """Validate a single day of forecast data"""
        try:
            # Temperature data
            temp_data = day_data.get('temp', {})
            temp_min = temp_data.get('min')
            temp_max = temp_data.get('max')
            temp_day = temp_data.get('day')
            temp_night = temp_data.get('night')
            
            if not self._is_valid_temperature(temp_min) or not self._is_valid_temperature(temp_max):
                self.logger.warning(f"Invalid forecast temperatures: min={temp_min}, max={temp_max}")
                return None
            
            # Weather description
            weather_list = day_data.get('weather', [])
            if not weather_list:
                return None
            
            weather_info = weather_list[0]
            description = weather_info.get('description', '').title()
            main_weather = weather_info.get('main', '')
            icon = weather_info.get('icon', '')
            
            # Additional forecast data
            humidity = day_data.get('humidity')
            pressure = day_data.get('pressure')
            wind_speed = day_data.get('wind_speed')
            wind_deg = day_data.get('wind_deg')
            clouds = day_data.get('clouds')
            pop = day_data.get('pop')  # Probability of precipitation
            uv_index = day_data.get('uvi')
            
            return {
                'dt': day_data.get('dt'),
                'temp_min': round(temp_min, 1),
                'temp_max': round(temp_max, 1),
                'temp_day': round(temp_day, 1) if temp_day is not None else None,
                'temp_night': round(temp_night, 1) if temp_night is not None else None,
                'description': description,
                'main': main_weather,
                'icon': icon,
                'humidity': humidity if self._is_valid_humidity(humidity) else None,
                'pressure': pressure if self._is_valid_pressure(pressure) else None,
                'wind_speed': wind_speed if self._is_valid_wind_speed(wind_speed) else None,
                'wind_deg': wind_deg,
                'clouds': clouds,
                'pop': pop,  # Probability of precipitation (0-1)
                'uv_index': uv_index,
                'sunrise': day_data.get('sunrise'),
                'sunset': day_data.get('sunset')
            }
            
        except Exception as e:
            self.logger.error(f"Error validating daily forecast day: {e}")
            return None

    def _is_valid_temperature(self, temp: Any) -> bool:
        """Check if temperature is within valid range"""
        if temp is None:
            return False
        try:
            temp_float = float(temp)
            if self.temperature_unit == "imperial":
                return self.rules.min_temperature_fahrenheit <= temp_float <= self.rules.max_temperature_fahrenheit
            elif self.temperature_unit == "metric":
                return self.rules.min_temperature_celsius <= temp_float <= self.rules.max_temperature_celsius
            else:  # kelvin
                return self.rules.min_temperature_kelvin <= temp_float <= self.rules.max_temperature_kelvin
        except (ValueError, TypeError):
            return False
    
    def _is_valid_humidity(self, humidity: Any) -> bool:
        """Check if humidity is within valid range"""
        if humidity is None:
            return False
        try:
            humidity_int = int(humidity)
            return self.rules.min_humidity <= humidity_int <= self.rules.max_humidity
        except (ValueError, TypeError):
            return False
    
    def _is_valid_pressure(self, pressure: Any) -> bool:
        """Check if pressure is within valid range"""
        if pressure is None:
            return False
        try:
            pressure_float = float(pressure)
            return self.rules.min_pressure <= pressure_float <= self.rules.max_pressure
        except (ValueError, TypeError):
            return False
    
    def _is_valid_wind_speed(self, wind_speed: Any) -> bool:
        """Check if wind speed is within valid range"""
        if wind_speed is None:
            return False
        try:
            wind_float = float(wind_speed)
            if self.temperature_unit == "imperial":
                return 0 <= wind_float <= self.rules.max_wind_speed_imperial
            else:  # metric
                return 0 <= wind_float <= self.rules.max_wind_speed_metric
        except (ValueError, TypeError):
            return False
    
    def validate_weather_data(self, data: Dict) -> bool:
        """
        Validate weather data against configured rules
        
        Args:
            data: Weather data dictionary to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = ['city', 'temperature', 'weather_description']
            for field in required_fields:
                if not data.get(field):
                    self.logger.error(f"Missing required field: {field}")
                    return False

            # Validate temperature
            temp = data.get('temperature')
            if temp is not None:
                if self.temperature_unit == "imperial":
                    if not (self.rules.min_temperature_fahrenheit <= temp <= self.rules.max_temperature_fahrenheit):
                        self.logger.error(f"Temperature out of range: {temp}°F")
                        return False
                else:  # metric
                    if not (self.rules.min_temperature_celsius <= temp <= self.rules.max_temperature_celsius):
                        self.logger.error(f"Temperature out of range: {temp}°C")
                        return False

            # Validate humidity if present
            humidity = data.get('humidity')
            if humidity is not None:
                if not (self.rules.min_humidity <= humidity <= self.rules.max_humidity):
                    self.logger.error(f"Humidity out of range: {humidity}%")
                    return False

            # Validate pressure if present
            pressure = data.get('pressure')
            if pressure is not None:
                if not (self.rules.min_pressure <= pressure <= self.rules.max_pressure):
                    self.logger.error(f"Pressure out of range: {pressure} hPa")
                    return False

            # Validate wind speed if present
            wind_speed = data.get('wind_speed')
            if wind_speed is not None:
                max_speed = (self.rules.max_wind_speed_imperial 
                           if self.temperature_unit == "imperial" 
                           else self.rules.max_wind_speed_metric)
                if not (0 <= wind_speed <= max_speed):
                    self.logger.error(f"Wind speed out of range: {wind_speed}")
                    return False

            # All validations passed
            return True

        except Exception as e:
            self.logger.error(f"Error validating weather data: {str(e)}")
            return False
    
    # Internal validation methods are handled within the main validation methods
    
    # Default initialization is sufficient

