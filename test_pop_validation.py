"""
Specific tests for Probability of Precipitation (POP) validation.
This module focuses on testing the POP validation fix that addresses
the bug where POP values were incorrectly calculated as 7.6 instead of 0.76.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.weather.data_validator import WeatherDataValidator
from core.weather.validation_rules import ValidationRules


def test_pop_validation_edge_cases():
    """Test POP validation with various edge cases"""
    print("Testing POP Validation Edge Cases")
    print("=" * 40)
    
    # Initialize validator
    rules = ValidationRules()
    validator = WeatherDataValidator(rules, temperature_unit="imperial")
    
    # Test cases: (value, expected_valid, description)
    test_cases = [
        # Valid cases
        (0.0, True, "Minimum valid POP (0%)"),
        (0.1, True, "Low POP (10%)"),
        (0.5, True, "Medium POP (50%)"),
        (0.76, True, "Specific case (76%)"),
        (1.0, True, "Maximum valid POP (100%)"),
        (None, True, "None (optional field)"),
        
        # Invalid cases - The main bugs we're fixing
        (7.6, False, "THE BUG: 7.6 instead of 0.76 (760% - clearly wrong)"),
        (45, False, "Percentage format bug (45 instead of 0.45)"),
        (2.5, False, "Over 100% (250%)"),
        (10.0, False, "Way over 100% (1000%)"),
        
        # Other invalid cases
        (-0.1, False, "Negative POP"),
        (-1.0, False, "Negative 100%"),
        (1.5, False, "Over 100% (150%)"),
        ("high", False, "Non-numeric string"),
        ("0.5", False, "String number (should be float)"),
        (float('inf'), False, "Infinity"),
        (float('nan'), False, "NaN"),
    ]
    
    passed = 0
    failed = 0
    
    for pop_value, expected_valid, description in test_cases:
        try:
            is_valid = validator._is_valid_pop(pop_value)
            
            if is_valid == expected_valid:
                status = "PASS"
                passed += 1
            else:
                status = "FAIL"
                failed += 1
            
            print(f"{status}: {description}")
            print(f"       Value: {pop_value}, Expected: {'valid' if expected_valid else 'invalid'}, Got: {'valid' if is_valid else 'invalid'}")
            
            # For the main bug case, show the calculation
            if pop_value == 7.6:
                print(f"       This represents {pop_value * 100:.1f}% which is clearly impossible!")
                print(f"       Should probably be {pop_value / 10:.1f} = {(pop_value / 10) * 100:.1f}%")
            
            print()
            
        except Exception as e:
            if expected_valid:
                print(f"FAIL: {description}")
                print(f"       Unexpected exception: {e}")
                failed += 1
            else:
                print(f"PASS: {description}")
                print(f"       Expected exception caught: {e}")
                passed += 1
            print()
    
    print(f"Results: {passed} passed, {failed} failed")
    return failed == 0


def test_pop_in_comprehensive_validation():
    """Test POP validation within the comprehensive validation system"""
    print("\nTesting POP in Comprehensive Validation")
    print("=" * 40)
    
    rules = ValidationRules()
    validator = WeatherDataValidator(rules, temperature_unit="imperial")
    
    # Test the main bug scenario
    bug_data = {
        "city": "Test City",
        "temperature": 75.0,
        "humidity": 50,
        "pop": 7.6  # THE BUG: This should be 0.76
    }
    
    result = validator.validate_comprehensive_weather_data(bug_data)
    
    print("Input data with POP bug:")
    print(f"  Original POP: {bug_data['pop']} (represents {bug_data['pop'] * 100:.1f}%)")
    print()
    
    print("Validation result:")
    validation_errors = result.get('validation_errors', [])
    print(f"  Validation errors: {len(validation_errors)}")
    
    for error in validation_errors:
        print(f"    - {error}")
    
    print(f"  Result POP: {result.get('pop')} (should be None due to invalid value)")
    print(f"  Other fields preserved: temperature={result.get('temperature')}, city={result.get('city')}")
    
    # Check that the bug was caught
    pop_error_found = any('pop' in error.lower() for error in validation_errors)
    if pop_error_found and result.get('pop') is None:
        print("\n✓ SUCCESS: POP bug was detected and handled correctly!")
        return True
    else:
        print("\n✗ FAILURE: POP bug was not detected properly!")
        return False


def test_pop_calculation_examples():
    """Show examples of correct vs incorrect POP calculations"""
    print("\nPOP Calculation Examples")
    print("=" * 30)
    
    examples = [
        {"wrong": 7.6, "correct": 0.76, "percentage": "76%"},
        {"wrong": 3.5, "correct": 0.35, "percentage": "35%"},
        {"wrong": 9.0, "correct": 0.90, "percentage": "90%"},
        {"wrong": 12.5, "correct": 1.0, "percentage": "100% (capped)"},  # Over 100% should be capped
    ]
    
    rules = ValidationRules()
    validator = WeatherDataValidator(rules, temperature_unit="imperial")
    
    for example in examples:
        wrong_val = example["wrong"]
        correct_val = example["correct"]
        percentage = example["percentage"]
        
        wrong_valid = validator._is_valid_pop(wrong_val)
        correct_valid = validator._is_valid_pop(correct_val)
        
        print(f"Percentage: {percentage}")
        print(f"  Wrong value: {wrong_val} -> {'Valid' if wrong_valid else 'Invalid (Good!)'}")
        print(f"  Correct value: {correct_val} -> {'Valid (Good!)' if correct_valid else 'Invalid'}")
        print()


if __name__ == "__main__":
    print("POP Validation Test Suite")
    print("=" * 50)
    print("This test specifically addresses the bug where POP values")
    print("were calculated as 7.6 instead of 0.76 (760% vs 76%)")
    print("=" * 50)
    print()
    
    # Run all tests
    test1_passed = test_pop_validation_edge_cases()
    test2_passed = test_pop_in_comprehensive_validation()
    test_pop_calculation_examples()
    
    # Summary
    print("\n" + "=" * 50)
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED! POP validation is working correctly.")
        print("The 7.6 POP bug should now be caught and handled properly.")
    else:
        print("❌ SOME TESTS FAILED! Please check the validation logic.")
    print("=" * 50)