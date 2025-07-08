"""Location and sunrise/sunset services for automatic theme switching"""

import requests
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
import time

class LocationService:
    """Service to get user location and sunrise/sunset times"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.last_location_fetch = 0
        self.cached_location = None
        self.cache_duration = 3600  # Cache for 1 hour
    
    def get_user_location_from_ip(self) -> Optional[Dict]:
        """
        Get user's approximate location from IP address
        
        Returns:
            Dict with location info (lat, lon, city, country) or None if failed
        """
        # Check cache first
        if (self.cached_location and 
            time.time() - self.last_location_fetch < self.cache_duration):
            self.logger.debug("Using cached location data")
            return self.cached_location
        
        try:
            # Using ipapi.co for IP geolocation (free, no API key needed)
            response = self.session.get(
                "https://ipapi.co/json/", 
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                location_info = {
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'country': data.get('country_name'),
                    'timezone': data.get('timezone')
                }
                
                # Validate we got the essential data
                if location_info['latitude'] and location_info['longitude']:
                    self.cached_location = location_info
                    self.last_location_fetch = time.time()
                    self.logger.info(f"Located user in {location_info['city']}, {location_info['region']}")
                    return location_info
                else:
                    self.logger.warning("IP location service returned incomplete data")
                    
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Failed to get location from IP: {e}")
        except Exception as e:
            self.logger.error(f"Error processing IP location: {e}")
        
        return None
    
    def get_sunrise_sunset(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get sunrise and sunset times for given coordinates
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Dict with sunrise/sunset times or None if failed
        """
        try:
            # Using sunrise-sunset.org API (free, no API key needed)
            response = self.session.get(
                "https://api.sunrise-sunset.org/json",
                params={
                    'lat': latitude,
                    'lng': longitude,
                    'formatted': 0  # Get ISO format times
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK':
                    results = data['results']
                    
                    # Parse ISO format times
                    sunrise_utc = datetime.fromisoformat(results['sunrise'].replace('Z', '+00:00'))
                    sunset_utc = datetime.fromisoformat(results['sunset'].replace('Z', '+00:00'))
                    
                    return {
                        'sunrise_utc': sunrise_utc,
                        'sunset_utc': sunset_utc,
                        'sunrise_local': sunrise_utc.astimezone(),
                        'sunset_local': sunset_utc.astimezone(),
                        'day_length': results.get('day_length')
                    }
                else:
                    self.logger.warning(f"Sunrise API returned status: {data.get('status')}")
                    
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Failed to get sunrise/sunset data: {e}")
        except Exception as e:
            self.logger.error(f"Error processing sunrise/sunset data: {e}")
        
        return None

class AutoThemeManager:
    """Manages automatic theme switching based on day/night cycle"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.location_service = LocationService()
        self.current_location = None
        self.current_sun_times = None
    
    def should_use_dark_theme(self, latitude: float = None, longitude: float = None) -> bool:
        """
        Determine if dark theme should be used based on current time and location
        
        Args:
            latitude: Optional specific latitude (uses IP location if not provided)
            longitude: Optional specific longitude (uses IP location if not provided)
            
        Returns:
            True if dark theme should be used, False for light theme
        """
        try:
            # Use provided coordinates or get from IP
            if latitude is not None and longitude is not None:
                coords = {'latitude': latitude, 'longitude': longitude}
            else:
                coords = self.location_service.get_user_location_from_ip()
                if not coords:
                    self.logger.warning("Could not determine location, defaulting to dark theme")
                    return True  # Default to dark if location unknown
            
            # Get sunrise/sunset times
            sun_times = self.location_service.get_sunrise_sunset(
                coords['latitude'], 
                coords['longitude']
            )
            
            if not sun_times:
                self.logger.warning("Could not get sunrise/sunset times, defaulting to dark theme")
                return True  # Default to dark if sun times unknown
            
            # Check if current time is between sunrise and sunset
            now = datetime.now().astimezone()
            sunrise = sun_times['sunrise_local']
            sunset = sun_times['sunset_local']
            
            is_daytime = sunrise <= now <= sunset
            
            self.logger.info(f"Current time: {now.strftime('%H:%M')}")
            self.logger.info(f"Sunrise: {sunrise.strftime('%H:%M')}, Sunset: {sunset.strftime('%H:%M')}")
            self.logger.info(f"Is daytime: {is_daytime}")
            
            # Store for potential future use
            self.current_location = coords
            self.current_sun_times = sun_times
            
            return not is_daytime  # Dark theme when it's NOT daytime
            
        except Exception as e:
            self.logger.error(f"Error determining day/night status: {e}")
            return True  # Default to dark theme on error
    
    def get_recommended_theme(self, latitude: float = None, longitude: float = None) -> str:
        """
        Get the recommended theme name based on day/night cycle
        
        Args:
            latitude: Optional specific latitude
            longitude: Optional specific longitude
            
        Returns:
            Theme name ("aj_lightly" for light, "aj_darkly" for dark)
        """
        use_dark = self.should_use_dark_theme(latitude, longitude)
        return "aj_darkly" if use_dark else "aj_lightly"
    
    def get_location_info(self) -> Optional[Dict]:
        """Get the current location information"""
        return self.current_location
    
    def get_sun_times(self) -> Optional[Dict]:
        """Get the current sunrise/sunset times"""
        return self.current_sun_times

# Utility functions for easy integration
def get_auto_theme(latitude: float = None, longitude: float = None) -> str:
    """
    Get the recommended theme based on day/night cycle
    
    Args:
        latitude: Optional specific latitude
        longitude: Optional specific longitude
        
    Returns:
        Theme name ("aj_lightly" for light, "aj_darkly" for dark)
    """
    manager = AutoThemeManager()
    return manager.get_recommended_theme(latitude, longitude)

def is_daytime(latitude: float = None, longitude: float = None) -> bool:
    """
    Check if it's currently daytime at the given location
    
    Args:
        latitude: Optional specific latitude
        longitude: Optional specific longitude
        
    Returns:
        True if daytime, False if nighttime
    """
    manager = AutoThemeManager()
    return not manager.should_use_dark_theme(latitude, longitude)
