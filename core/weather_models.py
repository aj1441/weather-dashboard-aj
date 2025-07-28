"""
Weather data models using dataclasses for type safety and consistency.

This module provides standardized data structures for weather information
throughout the application, ensuring type safety and consistent data handling.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class WeatherData:
    """Standardized weather data structure for current weather conditions."""
    
    # Location information
    city: str
    state: Optional[str] = None
    country: str = "US"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Temperature data
    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    
    # Atmospheric data
    humidity: Optional[int] = None
    pressure: Optional[float] = None
    sea_level: Optional[float] = None
    ground_level: Optional[float] = None
    
    # Weather description
    weather_main: Optional[str] = None
    weather_description: Optional[str] = None
    weather_icon: Optional[str] = None
    
    # Wind data
    wind_speed: Optional[float] = None
    wind_direction: Optional[int] = None
    wind_gust: Optional[float] = None
    
    # Other data
    cloudiness: Optional[int] = None
    visibility: Optional[int] = None
    uv_index: Optional[float] = None
    
    # Timestamps
    timestamp: Optional[str] = None
    api_timestamp: Optional[str] = None
    sunrise: Optional[str] = None
    sunset: Optional[str] = None
    
    # Metadata
    api_source: str = "unknown"
    units: str = "imperial"
    
    def __post_init__(self):
        """Validate data after initialization."""
        if not self.city:
            raise ValueError("City name is required")
        
        # Validate temperature ranges
        if self.temperature is not None:
            if self.units == "imperial" and not (-100 <= self.temperature <= 150):
                raise ValueError(f"Temperature {self.temperature}°F is out of reasonable range")
            elif self.units == "metric" and not (-73 <= self.temperature <= 66):
                raise ValueError(f"Temperature {self.temperature}°C is out of reasonable range")
        
        # Validate humidity
        if self.humidity is not None and not (0 <= self.humidity <= 100):
            raise ValueError(f"Humidity {self.humidity}% is out of range (0-100)")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API compatibility."""
        return {
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'temperature': self.temperature,
            'feels_like': self.feels_like,
            'temp_min': self.temp_min,
            'temp_max': self.temp_max,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'sea_level': self.sea_level,
            'ground_level': self.ground_level,
            'weather_main': self.weather_main,
            'weather_description': self.weather_description,
            'weather_icon': self.weather_icon,
            'wind_speed': self.wind_speed,
            'wind_direction': self.wind_direction,
            'wind_gust': self.wind_gust,
            'cloudiness': self.cloudiness,
            'visibility': self.visibility,
            'uv_index': self.uv_index,
            'timestamp': self.timestamp,
            'api_timestamp': self.api_timestamp,
            'sunrise': self.sunrise,
            'sunset': self.sunset,
            'api_source': self.api_source,
            'units': self.units
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherData':
        """Create WeatherData from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_api_response(cls, api_data: Dict[str, Any], units: str = "imperial") -> 'WeatherData':
        """Create WeatherData from OpenWeatherMap API response."""
        main_data = api_data.get('main', {})
        weather_data = api_data.get('weather', [{}])[0]
        wind_data = api_data.get('wind', {})
        coord_data = api_data.get('coord', {})
        sys_data = api_data.get('sys', {})
        
        return cls(
            city=api_data.get('name', 'Unknown'),
            country=sys_data.get('country', 'US'),
            latitude=coord_data.get('lat'),
            longitude=coord_data.get('lon'),
            temperature=main_data.get('temp'),
            feels_like=main_data.get('feels_like'),
            temp_min=main_data.get('temp_min'),
            temp_max=main_data.get('temp_max'),
            humidity=main_data.get('humidity'),
            pressure=main_data.get('pressure'),
            sea_level=main_data.get('sea_level'),
            ground_level=main_data.get('grnd_level'),
            weather_main=weather_data.get('main'),
            weather_description=weather_data.get('description'),
            weather_icon=weather_data.get('icon'),
            wind_speed=wind_data.get('speed'),
            wind_direction=wind_data.get('deg'),
            wind_gust=wind_data.get('gust'),
            cloudiness=api_data.get('clouds', {}).get('all'),
            visibility=api_data.get('visibility'),
            uv_index=api_data.get('uvi'),
            timestamp=datetime.now().isoformat(),
            api_timestamp=datetime.fromtimestamp(api_data.get('dt')).isoformat() if api_data.get('dt') else None,
            sunrise=datetime.fromtimestamp(sys_data.get('sunrise')).isoformat() if sys_data.get('sunrise') else None,
            sunset=datetime.fromtimestamp(sys_data.get('sunset')).isoformat() if sys_data.get('sunset') else None,
            api_source='openweathermap',
            units=units
        )


@dataclass
class ForecastData:
    """Standardized forecast data structure for weather predictions."""
    
    # Required fields first
    city: str
    forecast_date: datetime
    
    # Optional fields with defaults
    state: Optional[str] = None
    country: str = "US"
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    temp_day: Optional[float] = None
    temp_night: Optional[float] = None
    humidity: Optional[int] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    weather_main: Optional[str] = None
    weather_description: Optional[str] = None
    weather_icon: Optional[str] = None
    precipitation_probability: Optional[float] = None
    precipitation_amount: Optional[float] = None
    created_timestamp: Optional[datetime] = None
    api_data: Optional[Dict[str, Any]] = None
    units: str = "imperial"
    
    def __post_init__(self):
        """Validate data after initialization."""
        if not self.city:
            raise ValueError("City name is required")
        if not isinstance(self.forecast_date, datetime):
            raise ValueError("forecast_date must be a datetime object")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API compatibility."""
        return {
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'forecast_date': self.forecast_date.isoformat(),
            'temp_min': self.temp_min,
            'temp_max': self.temp_max,
            'temp_day': self.temp_day,
            'temp_night': self.temp_night,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'wind_speed': self.wind_speed,
            'weather_main': self.weather_main,
            'weather_description': self.weather_description,
            'weather_icon': self.weather_icon,
            'precipitation_probability': self.precipitation_probability,
            'precipitation_amount': self.precipitation_amount,
            'created_timestamp': self.created_timestamp.isoformat() if self.created_timestamp else None,
            'api_data': self.api_data,
            'units': self.units
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ForecastData':
        """Create ForecastData from dictionary."""
        # Convert timestamp strings back to datetime objects
        forecast_date = datetime.fromisoformat(data['forecast_date']) if data.get('forecast_date') else datetime.now()
        created_timestamp = datetime.fromisoformat(data['created_timestamp']) if data.get('created_timestamp') else None
        
        return cls(
            city=data['city'],
            forecast_date=forecast_date,
            state=data.get('state'),
            country=data.get('country', 'US'),
            temp_min=data.get('temp_min'),
            temp_max=data.get('temp_max'),
            temp_day=data.get('temp_day'),
            temp_night=data.get('temp_night'),
            humidity=data.get('humidity'),
            pressure=data.get('pressure'),
            wind_speed=data.get('wind_speed'),
            weather_main=data.get('weather_main'),
            weather_description=data.get('weather_description'),
            weather_icon=data.get('weather_icon'),
            precipitation_probability=data.get('precipitation_probability'),
            precipitation_amount=data.get('precipitation_amount'),
            created_timestamp=created_timestamp,
            api_data=data.get('api_data'),
            units=data.get('units', 'imperial')
        )


@dataclass
class ComprehensiveWeatherData:
    """Comprehensive weather data including current conditions and forecast."""
    
    current: WeatherData
    forecast: List[ForecastData] = field(default_factory=list)
    location: Dict[str, Any] = field(default_factory=dict)
    api_source: str = "unknown"
    
    def __post_init__(self):
        """Validate data after initialization."""
        if not isinstance(self.current, WeatherData):
            raise ValueError("current must be a WeatherData object")
        
        if not all(isinstance(f, ForecastData) for f in self.forecast):
            raise ValueError("All forecast items must be ForecastData objects")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API compatibility."""
        return {
            'current': self.current.to_dict(),
            'forecast': [f.to_dict() for f in self.forecast],
            'location': self.location,
            'api_source': self.api_source
        }


@dataclass
class SavedCity:
    """Data structure for saved city information."""
    
    city: str
    state: Optional[str] = None
    country: str = "US"
    nickname: Optional[str] = None
    saved_timestamp: datetime = field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    
    def __post_init__(self):
        """Validate data after initialization."""
        if not self.city:
            raise ValueError("City name is required")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'nickname': self.nickname,
            'saved_timestamp': self.saved_timestamp.isoformat(),
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'access_count': self.access_count
        }
    
    @property
    def display_name(self) -> str:
        """Get display name for the saved city."""
        if self.nickname:
            return self.nickname
        elif self.state:
            return f"{self.city}, {self.state}"
        else:
            return self.city
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SavedCity':
        """Create SavedCity from dictionary."""
        # Convert timestamp strings back to datetime objects
        saved_timestamp = datetime.fromisoformat(data['saved_timestamp']) if data.get('saved_timestamp') else datetime.now()
        last_accessed = datetime.fromisoformat(data['last_accessed']) if data.get('last_accessed') else None
        
        return cls(
            city=data['city'],
            state=data.get('state'),
            country=data.get('country', 'US'),
            nickname=data.get('nickname'),
            saved_timestamp=saved_timestamp,
            last_accessed=last_accessed,
            access_count=data.get('access_count', 0)
        ) 