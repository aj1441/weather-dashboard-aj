"""Backup manager for weather data - Continuous CSV and JSON exports"""

import os
import csv
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from pathlib import Path

logger = logging.getLogger(__name__)

class BackupManager:
    """Handles continuous backup operations for weather database"""
    
    def __init__(self, backup_dir: str = "data/backups"):
        self.backup_dir = Path(backup_dir)
        self._ensure_backup_directory()
        
        # Define continuous CSV file paths
        self.csv_files = {
            'current_weather': self.backup_dir / "csv" / "current_weather.csv",
            'forecast_weather': self.backup_dir / "csv" / "forecast_weather.csv",
            'historical_weather': self.backup_dir / "csv" / "historical_weather.csv",
            'weather_predictions': self.backup_dir / "csv" / "weather_predictions.csv"
        }
        
    def _ensure_backup_directory(self):
        """Create backup directories if they don't exist"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            (self.backup_dir / "csv").mkdir(exist_ok=True)
            (self.backup_dir / "json").mkdir(exist_ok=True)
            logger.debug(f"Backup directories ensured at {self.backup_dir}")
        except Exception as e:
            logger.error(f"Error creating backup directories: {e}")
            raise
    
    def _ensure_csv_headers(self, csv_path: Path, headers: List[str]):
        """Ensure CSV file has proper headers, create if file doesn't exist"""
        try:
            if not csv_path.exists():
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                logger.debug(f"Created CSV file with headers: {csv_path}")
        except Exception as e:
            logger.error(f"Error ensuring CSV headers for {csv_path}: {e}")
            raise
    
    def _get_existing_csv_records(self, csv_path: Path, key_columns: List[str]) -> Set[tuple]:
        """Get existing records from CSV to prevent duplicates"""
        existing_records = set()
        try:
            if csv_path.exists():
                with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    if reader.fieldnames:
                        for row in reader:
                            key = tuple(row.get(col, '') for col in key_columns)
                            existing_records.add(key)
        except Exception as e:
            logger.error(f"Error reading existing CSV records from {csv_path}: {e}")
        
        return existing_records
    
    def append_current_weather_to_csv(self, weather_data: Dict, city: str, state: str = None) -> bool:
        """Append new current weather data to continuous CSV file"""
        try:
            csv_path = self.csv_files['current_weather']
            
            # Define headers
            headers = [
                'id', 'city', 'state', 'country', 'latitude', 'longitude',
                'temperature', 'feels_like', 'humidity', 'pressure', 'wind_speed',
                'wind_direction', 'weather_description', 'weather_main', 'weather_icon',
                'visibility', 'uv_index', 'timestamp', 'api_response'
            ]
            
            # Ensure CSV file and headers exist
            self._ensure_csv_headers(csv_path, headers)
            
            # Check for duplicates based on city, state, and timestamp
            key_columns = ['city', 'state', 'timestamp']
            existing_records = self._get_existing_csv_records(csv_path, key_columns)
            
            # Create record key from the new data
            timestamp_str = weather_data.get('timestamp', datetime.now().isoformat())
            record_key = (city, state or '', timestamp_str)
            
            # Skip if record already exists
            if record_key in existing_records:
                logger.debug(f"Current weather record already exists in CSV: {city}, {state}, {timestamp_str}")
                return True
            
            # Append new record
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                
                # Prepare row data
                row_data = {
                    'id': weather_data.get('id', ''),
                    'city': city,
                    'state': state or '',
                    'country': weather_data.get('country', 'US'),
                    'latitude': weather_data.get('latitude', ''),
                    'longitude': weather_data.get('longitude', ''),
                    'temperature': weather_data.get('temperature', ''),
                    'feels_like': weather_data.get('feels_like', ''),
                    'humidity': weather_data.get('humidity', ''),
                    'pressure': weather_data.get('pressure', ''),
                    'wind_speed': weather_data.get('wind_speed', ''),
                    'wind_direction': weather_data.get('wind_direction', ''),
                    'weather_description': weather_data.get('weather_description', ''),
                    'weather_main': weather_data.get('weather_main', ''),
                    'weather_icon': weather_data.get('weather_icon', ''),
                    'visibility': weather_data.get('visibility', ''),
                    'uv_index': weather_data.get('uv_index', ''),
                    'timestamp': timestamp_str,
                    'api_response': json.dumps(weather_data.get('api_response', {})) if weather_data.get('api_response') else ''
                }
                
                writer.writerow(row_data)
            
            logger.info(f"Appended current weather data to CSV: {city}, {state}")
            return True
            
        except Exception as e:
            logger.error(f"Error appending current weather to CSV: {e}")
            return False
    
    def append_forecast_weather_to_csv(self, forecast_data: List[Dict], city: str, state: str = None) -> bool:
        """Append new forecast weather data to continuous CSV file"""
        try:
            csv_path = self.csv_files['forecast_weather']
            
            # Define headers
            headers = [
                'id', 'city', 'state', 'country', 'forecast_date', 'temperature_min',
                'temperature_max', 'temperature_day', 'temperature_night', 'humidity',
                'pressure', 'wind_speed', 'weather_description', 'weather_main',
                'weather_icon', 'precipitation_probability', 'precipitation_amount',
                'created_timestamp', 'api_response'
            ]
            
            # Ensure CSV file and headers exist
            self._ensure_csv_headers(csv_path, headers)
            
            # Check for duplicates based on city, state, and forecast_date
            key_columns = ['city', 'state', 'forecast_date']
            existing_records = self._get_existing_csv_records(csv_path, key_columns)
            
            # Append new forecast records
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                
                appended_count = 0
                for forecast_item in forecast_data:
                    forecast_date = forecast_item.get('forecast_date', '')
                    record_key = (city, state or '', str(forecast_date))
                    
                    # Skip if record already exists
                    if record_key in existing_records:
                        logger.debug(f"Forecast record already exists: {city}, {state}, {forecast_date}")
                        continue
                    
                    # Prepare row data
                    row_data = {
                        'id': forecast_item.get('id', ''),
                        'city': city,
                        'state': state or '',
                        'country': forecast_item.get('country', 'US'),
                        'forecast_date': forecast_date,
                        'temperature_min': forecast_item.get('temperature_min', ''),
                        'temperature_max': forecast_item.get('temperature_max', ''),
                        'temperature_day': forecast_item.get('temperature_day', ''),
                        'temperature_night': forecast_item.get('temperature_night', ''),
                        'humidity': forecast_item.get('humidity', ''),
                        'pressure': forecast_item.get('pressure', ''),
                        'wind_speed': forecast_item.get('wind_speed', ''),
                        'weather_description': forecast_item.get('weather_description', ''),
                        'weather_main': forecast_item.get('weather_main', ''),
                        'weather_icon': forecast_item.get('weather_icon', ''),
                        'precipitation_probability': forecast_item.get('precipitation_probability', ''),
                        'precipitation_amount': forecast_item.get('precipitation_amount', ''),
                        'created_timestamp': forecast_item.get('created_timestamp', datetime.now().isoformat()),
                        'api_response': json.dumps(forecast_item.get('api_response', {})) if forecast_item.get('api_response') else ''
                    }
                    
                    writer.writerow(row_data)
                    existing_records.add(record_key)  # Add to prevent duplicates within this batch
                    appended_count += 1
                
            logger.info(f"Appended {appended_count} forecast weather records to CSV: {city}, {state}")
            return True
            
        except Exception as e:
            logger.error(f"Error appending forecast weather to CSV: {e}")
            return False
    
    def append_historical_weather_to_csv(self, historical_data: Dict, city: str, state: str = None) -> bool:
        """Append historical weather data to continuous CSV file (no duplicates by city/state/date)"""
        try:
            csv_path = self.csv_files['historical_weather']
            
            # Define headers
            headers = [
                'id', 'city', 'state', 'date', 'temperature_max', 'temperature_min',
                'temperature_mean', 'precipitation', 'rain', 'wind_speed_max',
                'wind_gusts_max', 'cloud_cover', 'humidity', 'latitude', 'longitude',
                'sunrise', 'sunset'
            ]
            
            # Ensure CSV file and headers exist
            self._ensure_csv_headers(csv_path, headers)
            
            # Check for duplicates based on city, state, and date
            key_columns = ['city', 'state', 'date']
            existing_records = self._get_existing_csv_records(csv_path, key_columns)
            
            date_str = str(historical_data.get('date', ''))
            record_key = (city, state or '', date_str)
            
            # Skip if record already exists (same logic as database)
            if record_key in existing_records:
                logger.debug(f"Historical weather record already exists: {city}, {state}, {date_str}")
                return True
            
            # Append new record
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                
                # Prepare row data
                row_data = {
                    'id': historical_data.get('id', ''),
                    'city': city,
                    'state': state or '',
                    'date': date_str,
                    'temperature_max': historical_data.get('temperature_2m_max', ''),
                    'temperature_min': historical_data.get('temperature_2m_min', ''),
                    'temperature_mean': historical_data.get('temperature_2m_mean', ''),
                    'precipitation': historical_data.get('precipitation_sum', ''),
                    'rain': historical_data.get('rain_sum', ''),
                    'wind_speed_max': historical_data.get('wind_speed_10m_max', ''),
                    'wind_gusts_max': historical_data.get('wind_gusts_10m_max', ''),
                    'cloud_cover': historical_data.get('cloud_cover_mean', ''),
                    'humidity': historical_data.get('relative_humidity_2m_mean', ''),
                    'latitude': historical_data.get('latitude', ''),
                    'longitude': historical_data.get('longitude', ''),
                    'sunrise': historical_data.get('sunrise', ''),
                    'sunset': historical_data.get('sunset', '')
                }
                
                writer.writerow(row_data)
            
            logger.info(f"Appended historical weather data to CSV: {city}, {state}, {date_str}")
            return True
            
        except Exception as e:
            logger.error(f"Error appending historical weather to CSV: {e}")
            return False
    
    def append_weather_predictions_to_csv(self, prediction_data: Dict, city: str, state: str = None) -> bool:
        """Append weather predictions to continuous CSV file (always append with generation timestamp)"""
        try:
            csv_path = self.csv_files['weather_predictions']
            
            # Define headers
            headers = [
                'id', 'city', 'state', 'prediction_date', 'prediction_day',
                'predicted_temp_max', 'predicted_temp_min', 'predicted_precipitation',
                'predicted_humidity', 'predicted_wind_speed', 'predicted_conditions',
                'model_confidence', 'data_points_used', 'created_at', 'generated_at',
                'model_performance', 'trend_analysis', 'actual_temp_max', 'actual_temp_min',
                'actual_precipitation', 'actual_humidity', 'actual_conditions',
                'accuracy_score', 'is_latest'
            ]
            
            # Ensure CSV file and headers exist
            self._ensure_csv_headers(csv_path, headers)
            
            # Always append predictions with generation timestamp
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                
                generated_at = datetime.now().isoformat()
                forecast = prediction_data.get('forecast', [])
                
                appended_count = 0
                for prediction_item in forecast:
                    # Prepare row data
                    row_data = {
                        'id': prediction_item.get('id', ''),
                        'city': city,
                        'state': state or '',
                        'prediction_date': prediction_item.get('date', ''),
                        'prediction_day': prediction_item.get('day_number', ''),
                        'predicted_temp_max': prediction_item.get('temperature_max', ''),
                        'predicted_temp_min': prediction_item.get('temperature_min', ''),
                        'predicted_precipitation': prediction_item.get('precipitation', ''),
                        'predicted_humidity': prediction_item.get('humidity', ''),
                        'predicted_wind_speed': prediction_item.get('wind_speed', ''),
                        'predicted_conditions': prediction_item.get('conditions', ''),
                        'model_confidence': prediction_data.get('confidence', ''),
                        'data_points_used': prediction_data.get('data_points_used', ''),
                        'created_at': prediction_item.get('created_at', generated_at),
                        'generated_at': generated_at,  # Always record when this prediction was generated
                        'model_performance': json.dumps(prediction_data.get('model_performance', {})),
                        'trend_analysis': json.dumps(prediction_data.get('trend', {})),
                        'actual_temp_max': prediction_item.get('actual_temp_max', ''),
                        'actual_temp_min': prediction_item.get('actual_temp_min', ''),
                        'actual_precipitation': prediction_item.get('actual_precipitation', ''),
                        'actual_humidity': prediction_item.get('actual_humidity', ''),
                        'actual_conditions': prediction_item.get('actual_conditions', ''),
                        'accuracy_score': prediction_item.get('accuracy_score', ''),
                        'is_latest': prediction_item.get('is_latest', '')
                    }
                    
                    writer.writerow(row_data)
                    appended_count += 1
                
            logger.info(f"Appended {appended_count} weather prediction records to CSV: {city}, {state}")
            return True
            
        except Exception as e:
            logger.error(f"Error appending weather predictions to CSV: {e}")
            return False
    
    
    def get_backup_summary(self) -> Dict[str, int]:
        """Get summary of continuous CSV backup files"""
        try:
            csv_dir = self.backup_dir / "csv"
            
            csv_count = len(list(csv_dir.glob("*.csv"))) if csv_dir.exists() else 0
            
            # Check continuous CSV files
            continuous_files = {}
            for name, path in self.csv_files.items():
                continuous_files[name] = {
                    'exists': path.exists(),
                    'size': path.stat().st_size if path.exists() else 0,
                    'last_modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat() if path.exists() else None
                }
            
            return {
                'csv_backups': csv_count,
                'backup_directory': str(self.backup_dir),
                'continuous_csv_files': continuous_files
            }
            
        except Exception as e:
            logger.error(f"Error getting backup summary: {e}")
            return {'error': str(e)}


# Singleton pattern for backup manager
_backup_manager_instance = None

def get_backup_manager() -> BackupManager:
    """Get the singleton backup manager instance"""
    global _backup_manager_instance
    if _backup_manager_instance is None:
        _backup_manager_instance = BackupManager()
    return _backup_manager_instance