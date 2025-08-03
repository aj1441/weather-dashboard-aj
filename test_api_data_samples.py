"""
Test API data samples and validation for weather services.
This file contains sample API responses and validation tests to ensure
our weather data processing handles edge cases and invalid data properly.
"""

import json
from core.weather.data_validator import WeatherDataValidator
from core.weather.validation_rules import ValidationRules

# Sample API responses with various edge cases
SAMPLE_WEATHER_RESPONSES = {
    "normal_response": {
        "temperature": 75.5,
        "humidity": 45,
        "pressure": 1013.25,
        "wind_speed": 5.2,
        "pop": 0.3,
        "visibility": 10000,
        "uv_index": 6
    },
    
    "edge_case_temperatures": {
        "extreme_hot": {"temperature": 134.0},  # Death Valley record
        "extreme_cold": {"temperature": -128.6},  # Antarctica record
        "invalid_hot": {"temperature": 500.0},  # Invalid
        "invalid_cold": {"temperature": -500.0},  # Invalid
        "non_numeric": {"temperature": "hot"},  # Invalid
        "null_temp": {"temperature": None}  # Invalid
    },
    
    "edge_case_humidity": {
        "min_humidity": {"humidity": 0},  # Valid
        "max_humidity": {"humidity": 100},  # Valid
        "over_max": {"humidity": 120},  # Invalid
        "negative": {"humidity": -10},  # Invalid
        "non_numeric": {"humidity": "very humid"},  # Invalid
        "null_humidity": {"humidity": None}  # Valid (optional)
    },
    
    "edge_case_pop": {
        "min_pop": {"pop": 0.0},  # Valid
        "max_pop": {"pop": 1.0},  # Valid
        "percentage_format": {"pop": 45},  # Invalid (should be 0.45)
        "over_one": {"pop": 1.5},  # Invalid
        "negative": {"pop": -0.1},  # Invalid
        "non_numeric": {"pop": "likely"},  # Invalid
        "null_pop": {"pop": None}  # Valid (optional)
    },
    
    "problematic_real_data": {
        # Based on actual bugs we've encountered
        "pop_bug_7_6": {"pop": 7.6},  # Bug: POP as 760% instead of 0.76
        "temp_string": {"temperature": "75°F"},  # Bug: temp with units
        "wind_negative": {"wind_speed": -5.2},  # Bug: negative wind
        "pressure_zero": {"pressure": 0},  # Bug: invalid pressure
        "uv_extreme": {"uv_index": 50}  # Bug: extreme UV value
    }
}


def test_validator_with_samples():
    """Test the WeatherDataValidator with various sample data"""
    print("Testing WeatherDataValidator with sample data...")
    
    # Initialize validator
    rules = ValidationRules()
    validator = WeatherDataValidator(rules, temperature_unit="imperial")
    
    # Test normal response
    print("\n=== Testing Normal Response ===")
    result = validator.validate_comprehensive_weather_data(SAMPLE_WEATHER_RESPONSES["normal_response"])
    print(f"Validation errors: {len(result.get('validation_errors', []))}")
    if result.get('validation_errors'):
        print(f"Errors: {result['validation_errors']}")
    
    # Test edge cases
    print("\n=== Testing Edge Case Temperatures ===")
    for case_name, data in SAMPLE_WEATHER_RESPONSES["edge_case_temperatures"].items():
        result = validator.validate_comprehensive_weather_data(data)
        print(f"{case_name}: {len(result.get('validation_errors', []))} errors")
        if result.get('validation_errors'):
            print(f"  Errors: {result['validation_errors']}")
    
    # Test POP edge cases
    print("\n=== Testing Edge Case POP Values ===")
    for case_name, data in SAMPLE_WEATHER_RESPONSES["edge_case_pop"].items():
        result = validator.validate_comprehensive_weather_data(data)
        print(f"{case_name}: {len(result.get('validation_errors', []))} errors")
        if result.get('validation_errors'):
            print(f"  Errors: {result['validation_errors']}")
    
    # Test problematic real data
    print("\n=== Testing Problematic Real Data ===")
    for case_name, data in SAMPLE_WEATHER_RESPONSES["problematic_real_data"].items():
        result = validator.validate_comprehensive_weather_data(data)
        print(f"{case_name}: {len(result.get('validation_errors', []))} errors")
        if result.get('validation_errors'):
            print(f"  Errors: {result['validation_errors']}")


def test_pop_validation_specifically():
    """Specifically test POP validation to ensure the 7.6 bug is caught"""
    print("\n" + "="*50)
    print("SPECIFIC POP VALIDATION TEST")
    print("="*50)
    
    rules = ValidationRules()
    validator = WeatherDataValidator(rules, temperature_unit="imperial")
    
    test_cases = [
        {"name": "Valid: 0.0", "pop": 0.0, "should_pass": True},
        {"name": "Valid: 0.5", "pop": 0.5, "should_pass": True},
        {"name": "Valid: 1.0", "pop": 1.0, "should_pass": True},
        {"name": "Invalid: 7.6 (the bug)", "pop": 7.6, "should_pass": False},
        {"name": "Invalid: 45 (percentage)", "pop": 45, "should_pass": False},
        {"name": "Invalid: -0.1", "pop": -0.1, "should_pass": False},
        {"name": "Invalid: 'high'", "pop": "high", "should_pass": False},
        {"name": "Valid: None", "pop": None, "should_pass": True},
    ]
    
    for test_case in test_cases:
        data = {"pop": test_case["pop"]}
        result = validator.validate_comprehensive_weather_data(data)
        has_errors = len(result.get('validation_errors', [])) > 0
        passed = not has_errors if test_case["should_pass"] else has_errors
        
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_case['name']} - Expected: {'valid' if test_case['should_pass'] else 'invalid'}, Got: {'valid' if not has_errors else 'invalid'}")
        
        if result.get('validation_errors'):
            print(f"      Errors: {result['validation_errors']}")


if __name__ == "__main__":
    test_validator_with_samples()
    test_pop_validation_specifically()