"""Database table schemas and model definitions for weather data storage"""

# Table creation SQL statements
CURRENT_WEATHER_TABLE = """
CREATE TABLE IF NOT EXISTS current_weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    state TEXT,
    temperature REAL,
    humidity INTEGER,
    weather_main TEXT,
    weather_description TEXT,
    wind_speed REAL,
    pressure INTEGER,
    visibility INTEGER,
    sunrise INTEGER,
    sunset INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city, state, timestamp)
)
"""

FORECAST_WEATHER_TABLE = """
CREATE TABLE IF NOT EXISTS forecast_weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    state TEXT,
    forecast_date TEXT NOT NULL,
    temp_min REAL,
    temp_max REAL,
    humidity INTEGER,
    weather_main TEXT,
    weather_description TEXT,
    wind_speed REAL,
    pressure INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city, state, forecast_date, timestamp)
)
"""

SAVED_LOCATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS saved_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    state TEXT,
    nickname TEXT,
    latitude REAL,
    longitude REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city, state)
)
"""

USER_PREFERENCES_TABLE = """
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""

HISTORICAL_WEATHER_TABLE = """
CREATE TABLE IF NOT EXISTS historical_weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    state TEXT,
    date TEXT NOT NULL,
    temp_min REAL,
    temp_max REAL,
    humidity INTEGER,
    weather_main TEXT,
    weather_description TEXT,
    wind_speed REAL,
    pressure INTEGER,
    precipitation REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city, state, date)
)
"""

RECENT_HISTORICAL_WEATHER_TABLE = """
CREATE TABLE IF NOT EXISTS recent_historical_weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    state TEXT,
    date TEXT NOT NULL,
    temp_min REAL,
    temp_max REAL,
    humidity INTEGER,
    weather_main TEXT,
    weather_description TEXT,
    wind_speed REAL,
    pressure INTEGER,
    precipitation REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city, state, date)
)
"""

WEATHER_PREDICTIONS_TABLE = """
CREATE TABLE IF NOT EXISTS weather_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    state TEXT,
    prediction_date TEXT NOT NULL,
    predicted_temp_max REAL,
    predicted_temp_min REAL,
    predicted_precipitation REAL,
    predicted_humidity REAL,
    predicted_conditions TEXT,
    confidence_score REAL,
    model_type TEXT,
    actual_temp_max REAL,
    actual_temp_min REAL,
    actual_precipitation REAL,
    actual_humidity REAL,
    actual_conditions TEXT,
    accuracy_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city, state, prediction_date, model_type)
)
"""

# All table schemas in one place for easy management
TABLE_SCHEMAS = {
    'current_weather': CURRENT_WEATHER_TABLE,
    'forecast_weather': FORECAST_WEATHER_TABLE,
    'saved_locations': SAVED_LOCATIONS_TABLE,
    'user_preferences': USER_PREFERENCES_TABLE,
    'historical_weather': HISTORICAL_WEATHER_TABLE,
    'recent_historical_weather': RECENT_HISTORICAL_WEATHER_TABLE,
    'weather_predictions': WEATHER_PREDICTIONS_TABLE
}

# Required tables for verification
REQUIRED_TABLES = set(TABLE_SCHEMAS.keys()) 