"""Location service for determining user's geographic location and sunrise/sunset times"""

import requests
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict
import json
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LocationInfo:
    """Container for location information"""
    latitude: float
    longitude: float
    city: str
    country: str
    timezone_name: str
    
@dataclass  
class SunTimes:
    """Container for sunrise/sunset information"""
    sunrise: datetime
    sunset: datetime
    is_daytime: bool

class LocationService:
    """Service for getting user location and calculating sunrise/sunset times"""
    
    def __init__(self, cache_file: str = "data/location_cache.json", cache_duration_hours: int = 24):
        self.cache_file = cache_file
        self.cache_duration_hours = cache_duration_hours
        self._ensure_data_directory()
    
    def _ensure_data_directory(self) -> None:
        """Create data directory if it doesn't exist"""
        data_dir = os.path.dirname(self.cache_file)
        if data_dir:
            os.makedirs(data_dir, exist_ok=True)
    
    def get_user_location(self, use_cache: bool = True) -> Optional[LocationInfo]:
        """
        Get user's location via IP geolocation with caching
        
        Args:
            use_cache: Whether to use cached location if available
            
        Returns:
            LocationInfo object or None if failed
        """
        # Try cache first
        if use_cache:
            cached_location = self._load_cached_location()
            if cached_location:
                logger.debug("Using cached location data")
                return cached_location
        
        # Fetch fresh location data
        try:
            # Using ipapi.co as it's free and reliable
            response = requests.get("https://ipapi.co/json/", timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if we got valid data
            if not all(key in data for key in ['latitude', 'longitude', 'city', 'country_name']):
                logger.warning("Incomplete location data received")
                return None
            
            location_info = LocationInfo(
                latitude=float(data['latitude']),
                longitude=float(data['longitude']),
                city=data['city'],
                country=data['country_name'],
                timezone_name=data.get('timezone', 'UTC')
            )
            
            # Cache the result
            self._save_cached_location(location_info)
            
            logger.info(f"Located user in {location_info.city}, {location_info.country}")
            return location_info
            
        except requests.RequestException as e:
            logger.error(f"Failed to get location via IP: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid location data received: {e}")
            return None
    
    def get_sunrise_sunset(self, location: LocationInfo, date: Optional[datetime] = None) -> Optional[SunTimes]:
        """
        Get sunrise and sunset times for a location
        
        Args:
            location: LocationInfo object with coordinates
            date: Date to get times for (defaults to today)
            
        Returns:
            SunTimes object or None if failed
        """
        if date is None:
            date = datetime.now()
        
        try:
            # Using sunrise-sunset.org API (free, no key required)
            url = "https://api.sunrise-sunset.org/json"
            params = {
                'lat': location.latitude,
                'lng': location.longitude,
                'formatted': 0,  # Get ISO format
                'date': date.strftime('%Y-%m-%d')
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.error(f"Sunrise API error: {data}")
                return None
            
            # Parse times
            sunrise_str = data['results']['sunrise']
            sunset_str = data['results']['sunset']
            
            sunrise = datetime.fromisoformat(sunrise_str.replace('Z', '+00:00'))
            sunset = datetime.fromisoformat(sunset_str.replace('Z', '+00:00'))
            
            # Convert to local time (approximate - using system timezone)
            now = datetime.now(timezone.utc)
            local_offset = datetime.now() - datetime.utcnow()
            
            sunrise_local = sunrise + local_offset
            sunset_local = sunset + local_offset
            
            # Determine if it's currently daytime
            now_local = datetime.now()
            is_daytime = sunrise_local.time() <= now_local.time() <= sunset_local.time()
            
            sun_times = SunTimes(
                sunrise=sunrise_local,
                sunset=sunset_local,
                is_daytime=is_daytime
            )
            
            logger.info(f"Sun times for {location.city}: sunrise {sunrise_local.strftime('%H:%M')}, "
                       f"sunset {sunset_local.strftime('%H:%M')}, currently {'day' if is_daytime else 'night'}")
            
            return sun_times
            
        except requests.RequestException as e:
            logger.error(f"Failed to get sunrise/sunset data: {e}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid sunrise/sunset data received: {e}")
            return None
    
    def is_daytime_now(self, location: Optional[LocationInfo] = None) -> Optional[bool]:
        """
        Determine if it's currently daytime at user's location
        
        Args:
            location: LocationInfo object (fetched automatically if None)
            
        Returns:
            True if daytime, False if nighttime, None if unable to determine
        """
        if location is None:
            location = self.get_user_location()
            if location is None:
                return None
        
        sun_times = self.get_sunrise_sunset(location)
        if sun_times is None:
            return None
        
        return sun_times.is_daytime
    
    def _load_cached_location(self) -> Optional[LocationInfo]:
        """Load cached location if valid"""
        if not os.path.exists(self.cache_file):
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            
            # Check if cache is still valid
            cache_time = datetime.fromisoformat(data['cached_at'])
            hours_since_cache = (datetime.now() - cache_time).total_seconds() / 3600
            
            if hours_since_cache > self.cache_duration_hours:
                logger.debug("Location cache expired")
                return None
            
            return LocationInfo(
                latitude=data['latitude'],
                longitude=data['longitude'],
                city=data['city'],
                country=data['country'],
                timezone_name=data['timezone_name']
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Invalid location cache: {e}")
            return None
    
    def _save_cached_location(self, location: LocationInfo) -> None:
        """Save location to cache"""
        try:
            cache_data = {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'city': location.city,
                'country': location.country,
                'timezone_name': location.timezone_name,
                'cached_at': datetime.now().isoformat()
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to cache location: {e}")
