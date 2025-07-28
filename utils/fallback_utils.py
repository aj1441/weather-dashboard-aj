import functools
import json
import os
import random
import time
from typing import Optional, Dict, Any
from utils.fallback_tracker import track_fallback_usage

FALLBACK_DATA_PATH = os.path.join('data', 'fallback_weather.json')

# --- Static Fallback Loader ---
def load_static_fallback(location: Optional[str] = None) -> Optional[Dict[str, Any]]:
    try:
        with open(FALLBACK_DATA_PATH) as f:
            data = json.load(f)
        if location and location in data:
            return data[location]
        return random.choice(list(data.values()))
    except Exception:
        return None

# --- Random Weather Generator ---
def generate_random_weather(location: Optional[str] = None) -> Dict[str, Any]:
    return {
        "location": location or "Unknown",
        "temperature": round(random.uniform(60, 100), 1),
        "humidity": round(random.uniform(20, 80), 1),
        "condition": random.choice(["Clear", "Cloudy", "Rain", "Thunderstorm"]),
        "source": "random_fallback"
    }

# --- Hybrid Fallback Decorator ---
def fallback_handler(api_func):
    @functools.wraps(api_func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        api_name = api_func.__module__.split('.')[-1]
        endpoint = api_func.__name__
        location = kwargs.get('city') or kwargs.get('location') or 'Unknown'
        
        # Try live API call
        try:
            result = api_func(*args, **kwargs)
            if result and not (isinstance(result, dict) and result.get("error")):
                response_time = int((time.time() - start_time) * 1000)
                track_fallback_usage(
                    api_name=api_name,
                    endpoint=endpoint,
                    location=location,
                    fallback_type='none',
                    success=True,
                    response_time_ms=response_time
                )
                return result, False  # No fallback used
        except Exception as e:
            pass
        
        # Try static fallback
        static = load_static_fallback(location)
        if static:
            response_time = int((time.time() - start_time) * 1000)
            track_fallback_usage(
                api_name=api_name,
                endpoint=endpoint,
                location=location,
                fallback_type='static',
                success=True,
                error_message="API failed, using static fallback",
                response_time_ms=response_time
            )
            return static, True
        
        # Try random fallback
        response_time = int((time.time() - start_time) * 1000)
        track_fallback_usage(
            api_name=api_name,
            endpoint=endpoint,
            location=location,
            fallback_type='random',
            success=True,
            error_message="API and static fallback failed, using random data",
            response_time_ms=response_time
        )
        return generate_random_weather(location), True
    return wrapper

# --- Enhanced Fallback for Historical Data ---
def generate_random_historical_data(location: Optional[str] = None) -> Dict[str, Any]:
    """Generate random historical weather data for fallback scenarios."""
    return {
        "location": location or "Unknown",
        "temperature_max": round(random.uniform(70, 95), 1),
        "temperature_min": round(random.uniform(50, 75), 1),
        "temperature_mean": round(random.uniform(60, 85), 1),
        "precipitation": round(random.uniform(0, 2), 2),
        "humidity": round(random.uniform(30, 80), 1),
        "wind_speed": round(random.uniform(5, 20), 1),
        "condition": random.choice(["Clear", "Cloudy", "Rain", "Thunderstorm"]),
        "source": "random_historical_fallback"
    }

# --- Specialized Fallback Handler for Historical Data ---
def historical_fallback_handler(api_func):
    """Specialized fallback handler for historical data that returns DataFrames"""
    @functools.wraps(api_func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        api_name = api_func.__module__.split('.')[-1]
        endpoint = api_func.__name__
        location = f"{kwargs.get('city', 'Unknown')}, {kwargs.get('state', 'Unknown')}"
        
        try:
            result = api_func(*args, **kwargs)
            if result and isinstance(result, tuple) and len(result) == 2:
                df, error = result
                if df is not None and not (isinstance(df, dict) and df.get("error")):
                    response_time = int((time.time() - start_time) * 1000)
                    track_fallback_usage(
                        api_name=api_name,
                        endpoint=endpoint,
                        location=location,
                        fallback_type='none',
                        success=True,
                        response_time_ms=response_time
                    )
                    return result, False  # No fallback used
        except Exception as e:
            pass
        
        # For historical data, we'll create a simple fallback DataFrame
        import pandas as pd
        from datetime import datetime, timedelta
        
        # Create a simple fallback DataFrame with 7 days of data
        fallback_data = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            fallback_data.append({
                'city': kwargs.get('city', 'Unknown'),
                'state': kwargs.get('state', 'Unknown'),
                'date': date.strftime('%Y-%m-%d'),
                'temperature_max': round(random.uniform(70, 95), 1),
                'temperature_min': round(random.uniform(50, 75), 1),
                'temperature_mean': round(random.uniform(60, 85), 1),
                'precipitation': round(random.uniform(0, 2), 2),
                'rain': round(random.uniform(0, 1), 2),
                'wind_speed_max': round(random.uniform(5, 20), 1),
                'wind_gusts_max': round(random.uniform(10, 25), 1),
                'cloud_cover': random.randint(0, 100),
                'humidity': random.randint(30, 80),
                'latitude': kwargs.get('latitude', 0),
                'longitude': kwargs.get('longitude', 0),
                'sunrise': None,
                'sunset': None
            })
        
        fallback_df = pd.DataFrame(fallback_data)
        response_time = int((time.time() - start_time) * 1000)
        track_fallback_usage(
            api_name=api_name,
            endpoint=endpoint,
            location=location,
            fallback_type='historical_random',
            success=True,
            error_message="Historical API failed, using random historical data",
            response_time_ms=response_time
        )
        return (fallback_df, None), True  # Return (DataFrame, error), used_fallback=True
    return wrapper 