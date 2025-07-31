"""GUI Components for the Weather Dashboard"""

from .theme_component import ThemeComponent
from .weather_input_component import WeatherInputComponent
from .weather_display_component import WeatherDisplayComponent
from .saved_cities_component import SavedCitiesComponent
from .forecast_display_component import ForecastDisplayComponent
from .history_component import HistoryComponent
from .trivia_tab import TriviaTab
# from .weather_trivia_component import WeatherTriviaComponent  # Archived

__all__ = [
    'ThemeComponent',
    'WeatherInputComponent', 
    'WeatherDisplayComponent',
    'SavedCitiesComponent',
    'ForecastDisplayComponent',
    'HistoryComponent',
    'TriviaTab'
    # 'WeatherTriviaComponent'  # Archived
]
