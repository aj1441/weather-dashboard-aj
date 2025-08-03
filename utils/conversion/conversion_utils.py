"""Utility functions for unit conversions and calculations."""

def add_numbers(a: float, b: float) -> float:
    """
    Return the sum of two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of the two numbers
    """
    return a + b

def convert_to_fahrenheit(celsius: float) -> float:
    """
    Convert Celsius temperature to Fahrenheit.
    
    Args:
        celsius: Temperature in Celsius
        
    Returns:
        Temperature in Fahrenheit
    """
    return celsius * 9 / 5 + 32

def convert_to_celsius(fahrenheit: float) -> float:
    """
    Convert Fahrenheit temperature to Celsius.
    
    Args:
        fahrenheit: Temperature in Fahrenheit
        
    Returns:
        Temperature in Celsius
    """
    return (fahrenheit - 32) * 5 / 9
