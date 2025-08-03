"""
Tests for WeatherFeatureEngineer service.

Tests the extracted feature engineering functionality to ensure
the refactoring maintains the same behavior.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.feature_engineering_service import WeatherFeatureEngineer, FeatureValidator


class TestWeatherFeatureEngineer(unittest.TestCase):
    """Test the weather feature engineering service."""
    
    def setUp(self):
        """Set up test data."""
        self.feature_engineer = WeatherFeatureEngineer()
        
        # Create sample weather data
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        np.random.seed(42)  # For reproducible tests
        
        self.sample_data = pd.DataFrame({
            'date': dates,
            'temperature_max': 70 + 10 * np.sin(np.arange(100) * 2 * np.pi / 365) + np.random.normal(0, 5, 100),
            'temperature_min': 50 + 10 * np.sin(np.arange(100) * 2 * np.pi / 365) + np.random.normal(0, 3, 100),
            'precipitation': np.abs(np.random.normal(0, 0.5, 100)),
            'humidity': 50 + np.random.normal(0, 15, 100).clip(0, 100),
            'wind_speed_max': 5 + np.abs(np.random.normal(0, 3, 100)),
            'city': ['TestCity'] * 100,
            'state': ['TS'] * 100
        })
    
    def test_feature_engineering_basic(self):
        """Test basic feature engineering functionality."""
        X, y_dict = self.feature_engineer.prepare_features_and_targets(self.sample_data)
        
        # Check output types
        self.assertIsInstance(X, pd.DataFrame)
        self.assertIsInstance(y_dict, dict)
        
        # Check target variables
        expected_targets = ['temperature_max', 'temperature_min', 'precipitation', 'humidity']
        self.assertEqual(set(y_dict.keys()), set(expected_targets))
        
        # Check that we have features
        self.assertGreater(len(X.columns), 0)
        
        # Check data consistency
        for target_name, target_series in y_dict.items():
            self.assertEqual(len(target_series), len(X))
    
    def test_lag_features_created(self):
        """Test that lag features are created correctly."""
        X, _ = self.feature_engineer.prepare_features_and_targets(self.sample_data)
        
        # Check for lag features
        lag_features = [col for col in X.columns if 'lag_' in col]
        self.assertGreater(len(lag_features), 0)
        
        # Should have lag features for configured lag days
        for lag_day in self.feature_engineer.lag_days:
            self.assertIn(f'temp_max_lag_{lag_day}', X.columns)
            self.assertIn(f'temp_min_lag_{lag_day}', X.columns)
            self.assertIn(f'precip_lag_{lag_day}', X.columns)
            self.assertIn(f'humidity_lag_{lag_day}', X.columns)
    
    def test_moving_averages_created(self):
        """Test that moving average features are created."""
        X, _ = self.feature_engineer.prepare_features_and_targets(self.sample_data)
        
        # Check for moving average features
        ma_features = [col for col in X.columns if '_ma_' in col]
        self.assertGreater(len(ma_features), 0)
        
        # Should have MA features for configured windows
        for window in self.feature_engineer.moving_average_windows:
            self.assertIn(f'temp_max_ma_{window}', X.columns)
            self.assertIn(f'temp_min_ma_{window}', X.columns)
            self.assertIn(f'precip_ma_{window}', X.columns)
    
    def test_seasonal_features_created(self):
        """Test that seasonal features are created."""
        X, _ = self.feature_engineer.prepare_features_and_targets(self.sample_data)
        
        # Check for seasonal features
        seasonal_features = ['day_of_year', 'month', 'day_of_week', 'week_of_year']
        for feature in seasonal_features:
            self.assertIn(feature, X.columns)
        
        # Check cyclical encoding
        cyclical_features = ['day_of_year_sin', 'day_of_year_cos', 'month_sin', 'month_cos']
        for feature in cyclical_features:
            self.assertIn(feature, X.columns)
    
    def test_trend_features_created(self):
        """Test that trend features are created."""
        X, _ = self.feature_engineer.prepare_features_and_targets(self.sample_data)
        
        trend_features = ['temp_trend_7d', 'precip_trend_7d']
        for feature in trend_features:
            self.assertIn(feature, X.columns)
    
    def test_variability_features_created(self):
        """Test that variability features are created."""
        X, _ = self.feature_engineer.prepare_features_and_targets(self.sample_data)
        
        variability_features = ['temp_range', 'temp_range_ma_7']
        for feature in variability_features:
            self.assertIn(feature, X.columns)
    
    def test_no_target_leakage(self):
        """Test that target variables are not included in features."""
        X, _ = self.feature_engineer.prepare_features_and_targets(self.sample_data)
        
        # Target variables should not be in features
        target_columns = ['temperature_max', 'temperature_min', 'precipitation', 'humidity']
        for target in target_columns:
            self.assertNotIn(target, X.columns)
        
        # Non-predictive columns should not be in features
        non_predictive = ['date', 'city', 'state', 'latitude', 'longitude', 'sunrise', 'sunset']
        for col in non_predictive:
            if col in self.sample_data.columns:
                self.assertNotIn(col, X.columns)
    
    def test_insufficient_data_error(self):
        """Test error handling for insufficient data."""
        # Create very small dataset
        small_data = self.sample_data.head(5)
        
        with self.assertRaises(ValueError) as context:
            self.feature_engineer.prepare_features_and_targets(small_data)
        
        self.assertIn("Insufficient clean data", str(context.exception))
    
    def test_missing_columns_error(self):
        """Test error handling for missing required columns."""
        # Remove required column
        incomplete_data = self.sample_data.drop('temperature_max', axis=1)
        
        with self.assertRaises(ValueError) as context:
            self.feature_engineer.prepare_features_and_targets(incomplete_data)
        
        self.assertIn("Missing required columns", str(context.exception))
    
    def test_custom_configuration(self):
        """Test feature engineer with custom configuration."""
        custom_engineer = WeatherFeatureEngineer(
            lag_days=[1, 2],
            moving_average_windows=[7, 14],
            min_data_points=20
        )
        
        X, y_dict = custom_engineer.prepare_features_and_targets(self.sample_data)
        
        # Check that only configured lag days are present
        for lag_day in [1, 2]:
            self.assertIn(f'temp_max_lag_{lag_day}', X.columns)
        
        # Should not have lag_3 or lag_7 (not in custom config)
        self.assertNotIn('temp_max_lag_3', X.columns)
        self.assertNotIn('temp_max_lag_7', X.columns)
    
    def test_feature_names_tracking(self):
        """Test that feature names are properly tracked."""
        X, _ = self.feature_engineer.prepare_features_and_targets(self.sample_data)
        
        feature_names = self.feature_engineer.get_feature_names()
        
        # Feature names should match columns
        self.assertEqual(set(feature_names), set(X.columns))
        self.assertEqual(len(feature_names), len(X.columns))
    
    def test_feature_info(self):
        """Test feature information retrieval."""
        self.feature_engineer.prepare_features_and_targets(self.sample_data)
        
        feature_info = self.feature_engineer.get_feature_info()
        
        # Check info structure
        self.assertIn('lag_days', feature_info)
        self.assertIn('moving_average_windows', feature_info)
        self.assertIn('total_features', feature_info)
        self.assertIn('feature_categories', feature_info)
        
        # Check values
        self.assertEqual(feature_info['lag_days'], self.feature_engineer.lag_days)
        self.assertGreater(feature_info['total_features'], 0)


class TestFeatureValidator(unittest.TestCase):
    """Test the feature validation utility."""
    
    def setUp(self):
        """Set up test data."""
        self.feature_engineer = WeatherFeatureEngineer()
        
        # Create sample data
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        self.sample_data = pd.DataFrame({
            'date': dates,
            'temperature_max': np.random.normal(70, 10, 50),
            'temperature_min': np.random.normal(50, 8, 50),
            'precipitation': np.abs(np.random.normal(0, 0.5, 50)),
            'humidity': np.random.uniform(30, 90, 50),
            'city': ['TestCity'] * 50,
            'state': ['TS'] * 50
        })
    
    def test_valid_features(self):
        """Test validation of good features."""
        X, y_dict = self.feature_engineer.prepare_features_and_targets(self.sample_data)
        
        validation_results = FeatureValidator.validate_features(X, y_dict)
        
        # All validations should pass
        for key, result in validation_results.items():
            if key != 'all_valid':  # Check individual validations
                self.assertTrue(result, f"Validation failed for {key}")
        
        self.assertTrue(validation_results['all_valid'])


if __name__ == '__main__':
    unittest.main()