"""
Comprehensive validation tests for weather data processing.
Tests the complete validation pipeline including edge cases and error handling.
"""

import unittest
from core.weather.data_validator import WeatherDataValidator, ValidationRules


class TestComprehensiveValidation(unittest.TestCase):
    """Test comprehensive weather data validation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.rules = ValidationRules()
        self.validator_imperial = WeatherDataValidator(self.rules, temperature_unit="imperial")
        self.validator_metric = WeatherDataValidator(self.rules, temperature_unit="metric")
    
    def test_temperature_validation_imperial(self):
        """Test temperature validation with imperial units"""
        # Valid temperatures
        self.assertTrue(self.validator_imperial._is_valid_temperature(32))  # Freezing
        self.assertTrue(self.validator_imperial._is_valid_temperature(75))  # Room temp
        self.assertTrue(self.validator_imperial._is_valid_temperature(100)) # Hot
        
        # Edge cases
        self.assertTrue(self.validator_imperial._is_valid_temperature(-40))  # Very cold but valid
        self.assertTrue(self.validator_imperial._is_valid_temperature(130)) # Very hot but valid
        
        # Invalid temperatures
        self.assertFalse(self.validator_imperial._is_valid_temperature(500))  # Too hot
        self.assertFalse(self.validator_imperial._is_valid_temperature(-500)) # Too cold
        self.assertFalse(self.validator_imperial._is_valid_temperature("hot")) # Non-numeric
        self.assertFalse(self.validator_imperial._is_valid_temperature(None))  # None
    
    def test_temperature_validation_metric(self):
        """Test temperature validation with metric units"""
        # Valid temperatures
        self.assertTrue(self.validator_metric._is_valid_temperature(0))    # Freezing
        self.assertTrue(self.validator_metric._is_valid_temperature(25))   # Room temp
        self.assertTrue(self.validator_metric._is_valid_temperature(40))   # Hot
        
        # Invalid temperatures
        self.assertFalse(self.validator_metric._is_valid_temperature(200))  # Too hot
        self.assertFalse(self.validator_metric._is_valid_temperature(-200)) # Too cold
    
    def test_humidity_validation(self):
        """Test humidity validation"""
        # Valid humidity
        self.assertTrue(self.validator_imperial._is_valid_humidity(0))     # Min
        self.assertTrue(self.validator_imperial._is_valid_humidity(50))    # Normal
        self.assertTrue(self.validator_imperial._is_valid_humidity(100))   # Max
        self.assertTrue(self.validator_imperial._is_valid_humidity(None))  # Optional
        
        # Invalid humidity
        self.assertFalse(self.validator_imperial._is_valid_humidity(-10))   # Below min
        self.assertFalse(self.validator_imperial._is_valid_humidity(120))   # Above max
        self.assertFalse(self.validator_imperial._is_valid_humidity("high")) # Non-numeric
    
    def test_pressure_validation(self):
        """Test atmospheric pressure validation"""
        # Valid pressure
        self.assertTrue(self.validator_imperial._is_valid_pressure(1013.25)) # Standard
        self.assertTrue(self.validator_imperial._is_valid_pressure(900))     # Low but valid
        self.assertTrue(self.validator_imperial._is_valid_pressure(1100))    # High but valid
        self.assertTrue(self.validator_imperial._is_valid_pressure(None))    # Optional
        
        # Invalid pressure
        self.assertFalse(self.validator_imperial._is_valid_pressure(0))      # Too low
        self.assertFalse(self.validator_imperial._is_valid_pressure(2000))   # Too high
        self.assertFalse(self.validator_imperial._is_valid_pressure("normal")) # Non-numeric
    
    def test_wind_speed_validation(self):
        """Test wind speed validation"""
        # Valid wind speeds
        self.assertTrue(self.validator_imperial._is_valid_wind_speed(0))     # Calm
        self.assertTrue(self.validator_imperial._is_valid_wind_speed(10))    # Light breeze
        self.assertTrue(self.validator_imperial._is_valid_wind_speed(50))    # Strong wind
        self.assertTrue(self.validator_imperial._is_valid_wind_speed(None))  # Optional
        
        # Invalid wind speeds
        self.assertFalse(self.validator_imperial._is_valid_wind_speed(-5))   # Negative
        self.assertFalse(self.validator_imperial._is_valid_wind_speed(300))  # Too high
        self.assertFalse(self.validator_imperial._is_valid_wind_speed("windy")) # Non-numeric
    
    def test_pop_validation(self):
        """Test probability of precipitation validation"""
        # Valid POP values
        self.assertTrue(self.validator_imperial._is_valid_pop(0.0))    # No precipitation
        self.assertTrue(self.validator_imperial._is_valid_pop(0.5))    # 50% chance
        self.assertTrue(self.validator_imperial._is_valid_pop(1.0))    # Certain precipitation
        self.assertTrue(self.validator_imperial._is_valid_pop(None))   # Optional
        
        # Invalid POP values (the main bug we're fixing)
        self.assertFalse(self.validator_imperial._is_valid_pop(7.6))   # The 760% bug
        self.assertFalse(self.validator_imperial._is_valid_pop(45))    # Percentage format
        self.assertFalse(self.validator_imperial._is_valid_pop(-0.1))  # Negative
        self.assertFalse(self.validator_imperial._is_valid_pop(1.5))   # Over 100%
        self.assertFalse(self.validator_imperial._is_valid_pop("likely")) # Non-numeric
    
    def test_uv_index_validation(self):
        """Test UV index validation"""
        # Valid UV index
        self.assertTrue(self.validator_imperial._is_valid_uv_index(0))     # Min
        self.assertTrue(self.validator_imperial._is_valid_uv_index(5))     # Moderate
        self.assertTrue(self.validator_imperial._is_valid_uv_index(15))    # Very high
        self.assertTrue(self.validator_imperial._is_valid_uv_index(None))  # Optional
        
        # Invalid UV index
        self.assertFalse(self.validator_imperial._is_valid_uv_index(-1))   # Negative
        self.assertFalse(self.validator_imperial._is_valid_uv_index(50))   # Unrealistically high
        self.assertFalse(self.validator_imperial._is_valid_uv_index("high")) # Non-numeric
    
    def test_visibility_validation(self):
        """Test visibility validation"""
        # Valid visibility
        self.assertTrue(self.validator_imperial._is_valid_visibility(0))      # Fog
        self.assertTrue(self.validator_imperial._is_valid_visibility(10000))  # Clear
        self.assertTrue(self.validator_imperial._is_valid_visibility(50000))  # Very clear
        self.assertTrue(self.validator_imperial._is_valid_visibility(None))   # Optional
        
        # Invalid visibility
        self.assertFalse(self.validator_imperial._is_valid_visibility(-100))  # Negative
        self.assertFalse(self.validator_imperial._is_valid_visibility(200000)) # Too high
        self.assertFalse(self.validator_imperial._is_valid_visibility("clear")) # Non-numeric
    
    def test_comprehensive_validation_complete_data(self):
        """Test comprehensive validation with complete weather data"""
        complete_data = {
            "temperature": 75.5,
            "feels_like": 78.0,
            "humidity": 45,
            "pressure": 1013.25,
            "wind_speed": 5.2,
            "pop": 0.3,
            "uv_index": 6,
            "visibility": 10000,
            "city": "Test City",
            "description": "Partly cloudy"
        }
        
        result = self.validator_imperial.validate_comprehensive_weather_data(complete_data)
        
        # Should have no validation errors
        self.assertEqual(len(result.get('validation_errors', [])), 0)
        
        # Should preserve all valid data
        self.assertEqual(result['temperature'], 75.5)
        self.assertEqual(result['humidity'], 45)
        self.assertEqual(result['pop'], 0.3)
        self.assertEqual(result['city'], "Test City")
    
    def test_comprehensive_validation_problematic_data(self):
        """Test comprehensive validation with problematic data"""
        problematic_data = {
            "temperature": 500,      # Invalid: too hot
            "humidity": 120,         # Invalid: over 100%
            "pressure": 0,           # Invalid: too low
            "wind_speed": -5,        # Invalid: negative
            "pop": 7.6,              # Invalid: the main bug (760%)
            "uv_index": 50,          # Invalid: too high
            "visibility": -100,      # Invalid: negative
            "city": "Test City"      # Valid: string field
        }
        
        result = self.validator_imperial.validate_comprehensive_weather_data(problematic_data)
        
        # Should have validation errors for all invalid fields
        validation_errors = result.get('validation_errors', [])
        self.assertGreater(len(validation_errors), 0)
        
        # Should set invalid fields to None
        self.assertIsNone(result['temperature'])
        self.assertIsNone(result['humidity'])
        self.assertIsNone(result['pressure'])
        self.assertIsNone(result['wind_speed'])
        self.assertIsNone(result['pop'])
        self.assertIsNone(result['uv_index'])
        self.assertIsNone(result['visibility'])
        
        # Should preserve valid string fields
        self.assertEqual(result['city'], "Test City")
    
    def test_edge_case_pop_bug_specifically(self):
        """Specifically test the POP bug (7.6 instead of 0.76)"""
        test_data = {"pop": 7.6}
        result = self.validator_imperial.validate_comprehensive_weather_data(test_data)
        
        # Should detect the error
        validation_errors = result.get('validation_errors', [])
        self.assertGreater(len(validation_errors), 0)
        
        # Should contain POP-specific error
        pop_errors = [error for error in validation_errors if 'pop' in error.lower()]
        self.assertGreater(len(pop_errors), 0)
        
        # Should set POP to None
        self.assertIsNone(result['pop'])


if __name__ == '__main__':
    unittest.main(verbosity=2)