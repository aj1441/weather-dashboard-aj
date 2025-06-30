'''use different test files for different parts of the codebase
   e.g. test_gui.py for GUI related tests, test_utils.py for utility functions, etc.
   This helps in organizing tests and makes it easier to run specific tests.
   But do not create a test file for every single function.
   Instead, group related functions together in a single test file.
   For example, all functions related to weather data handling can be in test_weather_data.py.
   This way, you can run all tests related to weather data handling with a single command.
   Also, use descriptive names for test functions to indicate what they are testing.
   For example, test_get_weather_data_success, test_get_weather_data_failure, etc.
   This makes it easier to understand what each test is doing and helps in debugging when a test fails.
'''

'''try to test all edge cases and possible inputs for each function.
   For example, if a function takes a number as input, test it with positive numbers, negative numbers, zero, and non-numeric inputs.
   This ensures that the function handles all possible inputs correctly and does not crash or produce unexpected results.
   Also, test the function with large inputs to check for performance issues.
   For example, if a function processes a list, test it with an empty list, a single element list, and a large list with thousands of elements.
   This helps in identifying any performance bottlenecks in the code.
'''
from main import add_numbers, convert_to_fahrenheit

def test_add_numbers():
    """Test the add_numbers function."""
    assert add_numbers(2, 3) == 5
    assert add_numbers(-1, 1) == 0
    assert add_numbers(0, 0) == 0
    assert add_numbers(-5, -5) == -10
    assert add_numbers(100, 200) == 300
    assert add_numbers(1.5, 2.5) == 4.0
    assert add_numbers(-1.5, 1.5) == 0.0
    assert add_numbers(1000000, 2000000) == 3000000
    assert add_numbers(-1000000, -2000000) == -3000000
    assert add_numbers(1, -1) == 0
    assert add_numbers(-1, 1) == 0
    assert add_numbers(2.5, 3.5) == 6.0
    assert add_numbers(-2.5, -3.5) == -6.0
    assert add_numbers(0.5, 0.5) == 1.0
    assert add_numbers(10, 20) == 30
    assert add_numbers(-10, -20) == -30
    assert add_numbers(0, 100) == 100
    assert add_numbers(100, 0) == 100
    assert add_numbers(1e6, 2e6) == 3e6
    assert add_numbers(-1e6, -2e6) == -3e6
    assert add_numbers(0.01, 0.02) == 0.03
    assert add_numbers(1000000000, 2000000000) == 3000000000
    assert add_numbers(-1000000000, -2000000000) == -3000000000
    assert add_numbers(1.5, -1.5) == 0.0
    assert add_numbers(-1.5, 1.5) == 0.0
    

def test_convert_to_fahrenheit():
    """Test the convert_to_fahrenheit function.""" 
    assert convert_to_fahrenheit(0) == 32.0  # Freezing point of water
    assert convert_to_fahrenheit(100) == 212.0  # Boiling point of water
    assert convert_to_fahrenheit(-40) == -40.0  # -40 degrees is the same in both Celsius and Fahrenheit
    assert convert_to_fahrenheit(37) == 98.6  # Average human body temperature
    assert convert_to_fahrenheit(20) == 68.0  # Room temperature
    assert convert_to_fahrenheit(-20) == -4.0  # Cold temperature
    assert convert_to_fahrenheit(30) == 86.0  # Warm temperature
    assert convert_to_fahrenheit(15) == 59.0  # Mild temperature
    assert convert_to_fahrenheit(25) == 77.0  # Comfortable temperature
    assert convert_to_fahrenheit(10) == 50.0
