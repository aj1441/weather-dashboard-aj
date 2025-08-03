"""
Weather feature engineering service following Python best practices.

This service provides pure functions for preparing weather data features
for machine learning models without side effects.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
import logging

logger = logging.getLogger(__name__)


class WeatherFeatureEngineer:
    """
    Service for engineering weather features for machine learning.
    
    Uses pure functions that don't mutate input data, following functional programming
    principles for predictable, testable feature engineering.
    """
    
    def __init__(self, 
                 lag_days: List[int] = None,
                 moving_average_windows: List[int] = None,
                 min_data_points: int = 30):
        """
        Initialize feature engineer with configurable parameters.
        
        Args:
            lag_days: Days to create lag features for (default: [1, 2, 3, 7])
            moving_average_windows: Window sizes for moving averages (default: [3, 7, 14, 30])
            min_data_points: Minimum data points required after cleaning (default: 30)
        """
        self.lag_days = lag_days or [1, 2, 3, 7]
        self.moving_average_windows = moving_average_windows or [3, 7, 14, 30]
        self.min_data_points = min_data_points
        self.feature_names = []
        
    def prepare_features_and_targets(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, pd.Series]]:
        """
        Prepare features for ML models and target variables.
        
        Args:
            df: Historical weather DataFrame with required columns
            
        Returns:
            Tuple of (features DataFrame, targets dictionary)
            
        Raises:
            ValueError: If insufficient data after feature engineering
        """
        if df is None or len(df) == 0:
            raise ValueError("Input DataFrame is empty")
            
        # Verify required columns
        required_columns = ['date', 'temperature_max', 'temperature_min', 'precipitation', 'humidity']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Work with a copy to avoid mutating input data
        df_features = df.copy()
        
        # Create all feature types
        df_features = self._create_lag_features(df_features)
        df_features = self._create_moving_averages(df_features)
        df_features = self._create_seasonal_features(df_features)
        df_features = self._create_trend_features(df_features)
        df_features = self._create_variability_features(df_features)
        
        # Prepare final features and targets
        return self._finalize_features_and_targets(df_features)
    
    def _create_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create lag features (previous days' weather)."""
        logger.debug(f"Creating lag features for days: {self.lag_days}")
        
        for lag in self.lag_days:
            df[f'temp_max_lag_{lag}'] = df['temperature_max'].shift(lag)
            df[f'temp_min_lag_{lag}'] = df['temperature_min'].shift(lag)
            df[f'precip_lag_{lag}'] = df['precipitation'].shift(lag)
            df[f'humidity_lag_{lag}'] = df['humidity'].shift(lag)
        
        return df
    
    def _create_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create moving average features."""
        logger.debug(f"Creating moving averages for windows: {self.moving_average_windows}")
        
        for window in self.moving_average_windows:
            df[f'temp_max_ma_{window}'] = df['temperature_max'].rolling(
                window=window, min_periods=1
            ).mean()
            df[f'temp_min_ma_{window}'] = df['temperature_min'].rolling(
                window=window, min_periods=1
            ).mean()
            df[f'precip_ma_{window}'] = df['precipitation'].rolling(
                window=window, min_periods=1
            ).mean()
        
        return df
    
    def _create_seasonal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create seasonal and temporal features."""
        logger.debug("Creating seasonal features")
        
        # Basic temporal features
        df['day_of_year'] = df['date'].dt.dayofyear
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        df['week_of_year'] = df['date'].dt.isocalendar().week
        
        # Cyclical encoding for seasonal features (captures periodicity)
        df['day_of_year_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
        df['day_of_year_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        return df
    
    def _create_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create trend features using rolling linear regression."""
        logger.debug("Creating trend features")
        
        # Temperature and precipitation trends over 7 days
        df['temp_trend_7d'] = df['temperature_max'].rolling(window=7, min_periods=1).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0, 
            raw=False
        )
        df['precip_trend_7d'] = df['precipitation'].rolling(window=7, min_periods=1).apply(
            lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0, 
            raw=False
        )
        
        return df
    
    def _create_variability_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create weather variability features."""
        logger.debug("Creating variability features")
        
        # Temperature range and its moving average
        df['temp_range'] = df['temperature_max'] - df['temperature_min']
        df['temp_range_ma_7'] = df['temp_range'].rolling(window=7, min_periods=1).mean()
        
        return df
    
    def _finalize_features_and_targets(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, pd.Series]]:
        """Prepare final feature matrix and target variables."""
        logger.debug("Finalizing features and targets")
        
        # Define columns to exclude from features (targets and non-predictive)
        excluded_columns = {
            'date', 'city', 'state', 'latitude', 'longitude', 'sunrise', 'sunset',
            'temperature_max', 'temperature_min', 'precipitation', 'humidity', 'wind_speed_max',
            'id', 'created_at', 'temperature_mean', 'rain', 'wind_gusts_max'
        }
        
        # Select feature columns
        feature_columns = [col for col in df.columns if col not in excluded_columns]
        
        # Define columns needed for features and targets (to avoid dropping based on irrelevant columns)
        target_columns = ['temperature_max', 'temperature_min', 'precipitation', 'humidity']
        columns_to_check = feature_columns + target_columns
        
        # Remove rows with NaN values only from the columns we actually need
        df_clean = df[columns_to_check].dropna()
        
        if len(df_clean) < self.min_data_points:
            raise ValueError(f"Insufficient clean data after feature engineering: {len(df_clean)} < {self.min_data_points}")
        
        # Prepare feature matrix
        X = df_clean[feature_columns].copy()
        self.feature_names = feature_columns
        
        # Prepare target variables
        y_dict = {
            'temperature_max': df_clean['temperature_max'].copy(),
            'temperature_min': df_clean['temperature_min'].copy(),
            'precipitation': df_clean['precipitation'].copy(),
            'humidity': df_clean['humidity'].copy()
        }
        
        logger.info(f"Feature engineering completed: {len(X)} samples, {len(feature_columns)} features")
        return X, y_dict
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names from the last feature engineering run."""
        return self.feature_names.copy()
    
    def get_feature_info(self) -> Dict[str, any]:
        """Get information about the feature engineering configuration."""
        return {
            'lag_days': self.lag_days,
            'moving_average_windows': self.moving_average_windows,
            'min_data_points': self.min_data_points,
            'total_features': len(self.feature_names),
            'feature_categories': {
                'lag_features': len(self.lag_days) * 4,  # 4 variables (temp_max, temp_min, precip, humidity)
                'moving_averages': len(self.moving_average_windows) * 3,  # 3 variables
                'seasonal_features': 8,  # day_of_year, month, etc.
                'trend_features': 2,  # temp_trend_7d, precip_trend_7d
                'variability_features': 2  # temp_range, temp_range_ma_7
            }
        }


class FeatureValidator:
    """Utility class for validating feature engineering results."""
    
    @staticmethod
    def validate_features(X: pd.DataFrame, y_dict: Dict[str, pd.Series]) -> Dict[str, bool]:
        """
        Validate feature engineering output.
        
        Args:
            X: Feature matrix
            y_dict: Target variables
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {}
        
        # Check for NaN values
        validation_results['no_nan_features'] = not X.isnull().any().any()
        validation_results['no_nan_targets'] = not any(y.isnull().any() for y in y_dict.values())
        
        # Check data shapes
        validation_results['consistent_lengths'] = all(len(y) == len(X) for y in y_dict.values())
        
        # Check for infinite values
        validation_results['no_infinite_features'] = not np.isinf(X.select_dtypes(include=[np.number])).any().any()
        validation_results['no_infinite_targets'] = not any(np.isinf(y).any() for y in y_dict.values())
        
        # Check for sufficient variance
        numeric_features = X.select_dtypes(include=[np.number])
        validation_results['sufficient_variance'] = (numeric_features.std() > 1e-10).all()
        
        validation_results['all_valid'] = all(validation_results.values())
        
        return validation_results