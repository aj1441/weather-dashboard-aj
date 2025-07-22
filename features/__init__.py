"""Feature modules for the weather dashboard.

This package currently provides optional add-on functionality.
"""

from .weather_trivia_generator import WeatherTriviaGenerator, create_trivia_generator

__all__ = [
    'WeatherTriviaGenerator',
    'create_trivia_generator'
]
