"""Weather prediction module using Random Forest and Linear Regression from scikit-learn"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

from core.database.database import WeatherDatabase
from services.feature_engineering_service import WeatherFeatureEngineer


class WeatherPredictor:
    """Predicts 3-day weather forecast using Random Forest and trend analysis with Linear Regression"""
    
    def __init__(self, feature_engineer: WeatherFeatureEngineer = None):
        self.logger = logging.getLogger(__name__)
        self.db = WeatherDatabase()
        self.models = {}
        self.scalers = {}
        # Dependency injection: use provided feature engineer or create default
        self.feature_engineer = feature_engineer or WeatherFeatureEngineer()
        
    def predict_weather(self, city: str, state: str) -> Tuple[bool, Dict]:
        """
        Generate 3-day weather predictions for a city using Random Forest
        
        Returns:
            (success: bool, predictions: Dict) where predictions contains:
            - forecast: List of 3 daily predictions
            - trend: Dict with trend analysis
            - confidence: float (0-1)
            - model_performance: Dict with accuracy metrics
        """
        try:
            # Get historical data
            historical_data = self._get_historical_data(city, state)
            
            if historical_data is None or len(historical_data) < 60:
                return False, {"error": "Please get history first - need at least 60 days of data for predictions"}
            
            # Prepare features and train models using feature engineering service
            X, y_dict = self.feature_engineer.prepare_features_and_targets(historical_data)
            
            if len(X) < 30:
                return False, {"error": "Insufficient data for reliable predictions"}
            
            # Train models for each weather variable
            model_performance = self._train_models(X, y_dict)
            
            # Generate 3-day forecast
            forecast = self._generate_forecast(historical_data, X)
            
            # Analyze trends using Linear Regression
            trend_analysis = self._analyze_trends(historical_data)
            
            # Calculate confidence based on model performance
            confidence = self._calculate_confidence(model_performance, len(historical_data))
            
            predictions = {
                "forecast": forecast,
                "trend": trend_analysis,
                "confidence": confidence,
                "model_performance": model_performance,
                "city": city,
                "state": state,
                "generated_at": datetime.now().isoformat(),
                "data_points_used": len(historical_data)
            }
            
            # Save predictions to database for future comparison
            try:
                self.db.save_weather_prediction(city, state, predictions)
                self.logger.info(f"Saved weather predictions to database for {city}, {state}")
            except Exception as e:
                self.logger.error(f"Failed to save predictions to database: {e}")
                # Don't fail the entire prediction if saving fails
            
            return True, predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting weather for {city}, {state}: {e}")
            return False, {"error": str(e)}
    
    def _get_historical_data(self, city: str, state: str) -> Optional[pd.DataFrame]:
        """Retrieve and process COMBINED historical data for a city (hybrid approach)"""
        try:
            from .hybrid_data_coordinator import HybridWeatherDataCoordinator
            
            # Use hybrid coordinator to get combined data
            coordinator = HybridWeatherDataCoordinator(self.db)
            combined_data = coordinator._get_combined_historical_data(city, state)
            
            if not combined_data:
                # Fallback to original method for backward compatibility
                self.logger.warning(f"No combined data found, falling back to bulk historical data only")
                data = self.db.get_historical_weather(city, state)
                if not data:
                    return None
                combined_data = data
                
            df = pd.DataFrame(combined_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)
            
            # Remove any duplicates (prefer recent data over bulk data)
            df = df.drop_duplicates(subset=['date'], keep='last')
            
            # Fill missing values with interpolation
            numeric_columns = ['temperature_max', 'temperature_min', 'precipitation', 
                             'humidity', 'wind_speed_max', 'cloud_cover']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].interpolate(method='linear')
            
            self.logger.info(f"Retrieved {len(df)} days of combined historical data for {city}, {state}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error getting historical data: {e}")
            return None
    
    
    def _train_models(self, X: pd.DataFrame, y_dict: Dict) -> Dict:
        """Train Random Forest models for each weather variable"""
        
        model_performance = {}
        
        # Split data for training and validation
        X_train, X_test, _, _ = train_test_split(X, X, test_size=0.2, random_state=42)
        
        for target_name, y in y_dict.items():
            try:
                # Split target variable
                y_train = y.loc[X_train.index]
                y_test = y.loc[X_test.index]
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train Random Forest
                rf_model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=15,
                    min_samples_split=5,
                    min_samples_leaf=2,
                    random_state=42,
                    n_jobs=-1
                )
                
                rf_model.fit(X_train_scaled, y_train)
                
                # Evaluate model
                y_pred = rf_model.predict(X_test_scaled)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                # Store model and metrics
                self.models[target_name] = rf_model
                self.scalers[target_name] = scaler
                
                model_performance[target_name] = {
                    'mae': round(mae, 3),
                    'r2_score': round(r2, 3),
                    'feature_importance': dict(zip(
                        self.feature_engineer.get_feature_names(), 
                        rf_model.feature_importances_
                    ))
                }
                
                self.logger.info(f"Trained {target_name} model - MAE: {mae:.3f}, R²: {r2:.3f}")
                
            except Exception as e:
                self.logger.error(f"Error training model for {target_name}: {e}")
                model_performance[target_name] = {'error': str(e)}
        
        return model_performance
    
    def _generate_forecast(self, df: pd.DataFrame, X: pd.DataFrame) -> List[Dict]:
        """Generate 3-day forecast using trained models"""
        
        forecast = []
        
        # Get the most recent data for prediction
        latest_data = df.iloc[-1].copy()
        latest_features = X.iloc[-1].copy()
        
        for day in range(1, 4):
            prediction_date = datetime.now() + timedelta(days=day)
            
            # Update cyclical features for prediction date
            day_of_year = prediction_date.timetuple().tm_yday
            month = prediction_date.month
            
            latest_features['day_of_year'] = day_of_year
            latest_features['month'] = month
            latest_features['day_of_year_sin'] = np.sin(2 * np.pi * day_of_year / 365.25)
            latest_features['day_of_year_cos'] = np.cos(2 * np.pi * day_of_year / 365.25)
            latest_features['month_sin'] = np.sin(2 * np.pi * month / 12)
            latest_features['month_cos'] = np.cos(2 * np.pi * month / 12)
            
            # Make predictions for each weather variable
            predictions = {}
            for target_name in ['temperature_max', 'temperature_min', 'precipitation', 'pop']:
                if target_name in self.models:
                    try:
                        # Scale features
                        features_scaled = self.scalers[target_name].transform([latest_features])
                        
                        # Predict
                        pred_value = self.models[target_name].predict(features_scaled)[0]
                        
                        # Apply constraints
                        if target_name == 'precipitation':
                            pred_value = max(0, pred_value)
                        elif target_name == 'humidity':
                            pred_value = max(0, min(100, pred_value))
                        
                        predictions[target_name] = round(pred_value, 1)
                        
                    except Exception as e:
                        self.logger.error(f"Error predicting {target_name}: {e}")
                        predictions[target_name] = None
            
            # Estimate wind speed based on historical patterns
            wind_speed = round(df['wind_speed_max'].tail(30).mean() + np.random.normal(0, 2), 1)
            wind_speed = max(0, wind_speed)
            
            # Determine weather conditions
            conditions = self._predict_conditions(
                predictions.get('precipitation', 0),
                predictions.get('humidity', 50)
            )
            
            daily_prediction = {
                "date": prediction_date.strftime("%Y-%m-%d"),
                "day_name": prediction_date.strftime("%A"),
                "temperature_max": predictions.get('temperature_max'),
                "temperature_min": predictions.get('temperature_min'),
                "precipitation": predictions.get('precipitation'),
                "humidity": predictions.get('humidity'),
                "wind_speed": wind_speed,
                "conditions": conditions,
                "day_number": day
            }
            
            forecast.append(daily_prediction)
            
            # Update features for next day prediction (simple approach)
            if predictions.get('temperature_max') is not None:
                latest_features['temp_max_lag_1'] = predictions['temperature_max']
            if predictions.get('precipitation') is not None:
                latest_features['precip_lag_1'] = predictions['precipitation']
        
        return forecast
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze weather trends using Linear Regression"""
        
        trends = {}
        
        try:
            # Prepare data for trend analysis
            df_recent = df.tail(60)  # Last 60 days
            
            if len(df_recent) < 14:
                return {"error": "Insufficient data for trend analysis"}
            
            # Create time index for regression
            X_time = np.arange(len(df_recent)).reshape(-1, 1)
            
            # Temperature trend analysis
            temp_avg = (df_recent['temperature_max'] + df_recent['temperature_min']) / 2
            temp_model = LinearRegression().fit(X_time, temp_avg)
            temp_slope = temp_model.coef_[0]
            temp_r2 = temp_model.score(X_time, temp_avg)
            
            trends["temperature"] = {
                "direction": "rising" if temp_slope > 0.1 else "falling" if temp_slope < -0.1 else "stable",
                "slope_per_day": round(temp_slope, 3),
                "slope_per_week": round(temp_slope * 7, 2),
                "confidence": round(temp_r2, 3),
                "description": self._describe_temp_trend(temp_slope)
            }
            
            # Precipitation trend analysis
            precip_model = LinearRegression().fit(X_time, df_recent['precipitation'])
            precip_slope = precip_model.coef_[0]
            precip_r2 = precip_model.score(X_time, df_recent['precipitation'])
            
            trends["precipitation"] = {
                "direction": "increasing" if precip_slope > 0.01 else "decreasing" if precip_slope < -0.01 else "stable",
                "slope_per_day": round(precip_slope, 4),
                "slope_per_week": round(precip_slope * 7, 3),
                "confidence": round(precip_r2, 3),
                "description": self._describe_precip_trend(precip_slope)
            }
            
            # Seasonal comparison (current month vs same month last year)
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            this_month = df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year)]
            last_year_month = df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year - 1)]
            
            if len(this_month) > 0 and len(last_year_month) > 0:
                this_temp_avg = (this_month['temperature_max'] + this_month['temperature_min']).mean() / 2
                last_temp_avg = (last_year_month['temperature_max'] + last_year_month['temperature_min']).mean() / 2
                seasonal_change = this_temp_avg - last_temp_avg
                
                trends["seasonal"] = {
                    "direction": "warmer" if seasonal_change > 2 else "cooler" if seasonal_change < -2 else "similar",
                    "change_vs_last_year": round(seasonal_change, 1),
                    "description": f"{'Warmer' if seasonal_change > 0 else 'Cooler'} than last year by {abs(seasonal_change):.1f}°F"
                }
            
        except Exception as e:
            self.logger.error(f"Error in trend analysis: {e}")
            trends["error"] = str(e)
        
        return trends
    
    def _calculate_confidence(self, model_performance: Dict, data_points: int) -> float:
        """Calculate overall prediction confidence"""
        
        # Base confidence on amount of data
        if data_points < 60:
            base_confidence = 0.4
        elif data_points < 365:
            base_confidence = 0.6
        elif data_points < 365 * 3:
            base_confidence = 0.8
        else:
            base_confidence = 0.9
        
        # Adjust based on model performance
        performance_scores = []
        for target, metrics in model_performance.items():
            if 'r2_score' in metrics:
                performance_scores.append(max(0, metrics['r2_score']))
        
        if performance_scores:
            avg_performance = np.mean(performance_scores)
            confidence = (base_confidence + avg_performance) / 2
        else:
            confidence = base_confidence * 0.5  # Lower confidence if models failed
        
        return round(min(1.0, max(0.1, confidence)), 2)
    
    def _predict_conditions(self, precipitation: float, humidity: float) -> str:
        """Predict weather conditions based on precipitation and humidity"""
        if precipitation > 0.5:
            return "Rainy"
        elif precipitation > 0.1:
            return "Light Rain"
        elif humidity > 80:
            return "Cloudy"
        elif humidity > 60:
            return "Partly Cloudy"
        else:
            return "Sunny"
    
    def _describe_temp_trend(self, slope: float) -> str:
        """Generate descriptive text for temperature trends"""
        weekly_change = slope * 7
        if weekly_change > 3:
            return f"Rapidly warming ({weekly_change:.1f}°F/week)"
        elif weekly_change > 1:
            return f"Warming trend ({weekly_change:.1f}°F/week)"
        elif weekly_change > 0.5:
            return f"Slight warming ({weekly_change:.1f}°F/week)"
        elif weekly_change < -3:
            return f"Rapidly cooling ({abs(weekly_change):.1f}°F/week)"
        elif weekly_change < -1:
            return f"Cooling trend ({abs(weekly_change):.1f}°F/week)"
        elif weekly_change < -0.5:
            return f"Slight cooling ({abs(weekly_change):.1f}°F/week)"
        else:
            return "Stable temperatures"
    
    def _describe_precip_trend(self, slope: float) -> str:
        """Generate descriptive text for precipitation trends"""
        weekly_change = slope * 7
        if weekly_change > 0.2:
            return f"Much wetter trend (+{weekly_change:.2f}\"/week)"
        elif weekly_change > 0.05:
            return f"Wetter trend (+{weekly_change:.2f}\"/week)"
        elif weekly_change < -0.2:
            return f"Much drier trend ({weekly_change:.2f}\"/week)"
        elif weekly_change < -0.05:
            return f"Drier trend ({weekly_change:.2f}\"/week)"
        else:
            return "Stable precipitation"
    
    def has_sufficient_data(self, city: str, state: str) -> bool:
        """Check if there's sufficient COMBINED historical data for predictions (hybrid approach)"""
        try:
            from .hybrid_data_coordinator import HybridWeatherDataCoordinator
            
            # Use hybrid coordinator to check combined data
            coordinator = HybridWeatherDataCoordinator(self.db)
            return coordinator.has_sufficient_data_for_predictions(city, state)
            
        except Exception as e:
            self.logger.error(f"Error checking data sufficiency: {e}")
            # Fallback to original method
            try:
                data = self.db.get_historical_weather(city, state)
                return data and len(data) >= 60
            except:
                return False
    
    def get_prediction_history(self, city: str, state: str, days: int = 30) -> List[Dict]:
        """
        Get prediction history for a city
        
        Args:
            city: City name
            state: State code
            days: Number of days back to look (default 30)
            
        Returns:
            List of prediction records
        """
        try:
            from datetime import datetime, timedelta
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            predictions = self.db.get_weather_predictions(
                city, state, 
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error getting prediction history: {e}")
            return []
    
    def update_predictions_with_actual_data(self, city: str, state: str) -> bool:
        """
        Update predictions with actual weather data from historical records
        
        Args:
            city: City name
            state: State code
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get recent predictions that don't have actual data yet
            predictions = self.db.get_weather_predictions(city, state)
            
            # Filter for predictions that need actual data
            predictions_to_update = [
                p for p in predictions 
                if p['actual_temp_max'] is None and p['prediction_date'] <= datetime.now().date().strftime('%Y-%m-%d')
            ]
            
            if not predictions_to_update:
                self.logger.info(f"No predictions need updating for {city}, {state}")
                return True
            
            # Get historical data for comparison
            historical_data = self.db.get_historical_weather(city, state)
            
            if not historical_data:
                self.logger.warning(f"No historical data available for updating predictions for {city}, {state}")
                return False
            
            # Create lookup dictionary for historical data
            historical_lookup = {
                record['date']: record for record in historical_data
            }
            
            updated_count = 0
            
            # Update predictions with actual data
            for pred in predictions_to_update:
                pred_date = pred['prediction_date']
                
                if pred_date in historical_lookup:
                    actual_data = historical_lookup[pred_date]
                    
                    # Map weather conditions from historical data
                    actual_conditions = self._map_historical_to_conditions(actual_data)
                    
                    success = self.db.update_prediction_with_actual(
                        city, state, pred_date,
                        actual_data['temperature_max'],
                        actual_data['temperature_min'],
                        actual_data['precipitation'],
                        actual_data['humidity'],
                        actual_conditions
                    )
                    
                    if success:
                        updated_count += 1
            
            self.logger.info(f"Updated {updated_count} predictions with actual data for {city}, {state}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating predictions with actual data: {e}")
            return False
    
    def _map_historical_to_conditions(self, historical_data: Dict) -> str:
        """
        Map historical weather data to weather conditions
        
        Args:
            historical_data: Dictionary with historical weather data
            
        Returns:
            Weather condition string
        """
        try:
            precipitation = historical_data.get('precipitation', 0) or 0
            humidity = historical_data.get('humidity', 0) or 0
            cloud_cover = historical_data.get('cloud_cover', 0) or 0
            
            # Use similar logic as predictions
            if precipitation > 0.5:
                return "Rainy"
            elif precipitation > 0.1:
                return "Light Rain"
            elif cloud_cover > 80 or humidity > 80:
                return "Cloudy"
            elif cloud_cover > 50 or humidity > 60:
                return "Partly Cloudy"
            else:
                return "Sunny"
                
        except Exception as e:
            self.logger.error(f"Error mapping historical data to conditions: {e}")
            return "Unknown"
    
    def get_prediction_accuracy_summary(self, city: str, state: str) -> Dict:
        """
        Get prediction accuracy summary for a city
        
        Args:
            city: City name
            state: State code
            
        Returns:
            Dictionary with accuracy statistics
        """
        try:
            # Update predictions with actual data first
            self.update_predictions_with_actual_data(city, state)
            
            # Get accuracy statistics
            stats = self.db.get_prediction_accuracy_stats(city, state)
            
            # Add some additional context
            predictions = self.get_prediction_history(city, state, 90)  # Last 90 days
            
            verified_predictions = [p for p in predictions if p['accuracy_score'] is not None]
            
            summary = {
                'city': city,
                'state': state,
                'total_predictions': len(predictions),
                'verified_predictions': len(verified_predictions),
                'average_accuracy': stats.get('avg_accuracy', 0),
                'average_confidence': stats.get('avg_confidence', 0),
                'accuracy_range': {
                    'min': stats.get('min_accuracy', 0),
                    'max': stats.get('max_accuracy', 0)
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting prediction accuracy summary: {e}")
            return {}