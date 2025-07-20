"""
Prediction services for weather forecasting.

This package contains modular services for weather prediction following
Python best practices:
- Single Responsibility Principle
- Dependency Injection  
- Protocol-based interfaces
- Pure functions where possible
"""

from .feature_engineer import WeatherFeatureEngineer, FeatureValidator

__all__ = ['WeatherFeatureEngineer', 'FeatureValidator']