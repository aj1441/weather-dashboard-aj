"""Advanced tabbed weather dashboard with components"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from typing import Optional, Dict, Any, List
import tkinter as tk
import ttkbootstrap as tb
import logging
import threading
from utils.data.state_utils import normalize_state_abbreviation
import time
from datetime import datetime
from PIL import Image, ImageTk
from ttkbootstrap.constants import LEFT, RIGHT, BOTH, X, Y, END
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.widgets import Sizegrip
from core.weather.api import WeatherAPI
from core.database.data_handler import WeatherDataHandler
from core.theme.theme_factory import create_theme_manager
from gui.shared.theme_component import ThemeComponent
from gui.tabs.weather_tab.input_component import WeatherInputComponent
from gui.tabs.weather_tab.display_component import WeatherDisplayComponent
from gui.tabs.weather_tab.forecast_component import ForecastDisplayComponent
from gui.tabs.saved_cities_tab.saved_cities_component import SavedCitiesComponent
from gui.tabs.history_tab.history_component import HistoryComponent
from gui.tabs.trivia_tab.trivia_tab import TriviaTab
from gui.tabs.about_tab.about_component import AboutComponent


class TabbedWeatherDashboard:
    """Advanced tabbed GUI with components and additional features"""

    def __init__(self, config: Optional[Any] = None) -> None:
        # Store config for components that need it
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        #1. Create the actual window FIRST
        self.app = tb.Window()

        #2. Initialize new theme system (auto-enabled by default)
        self.theme_manager = create_theme_manager(self.app)
        
        #3. Apply initial theme (auto or manual based on settings)
        self.theme_manager.apply_current_theme()
        
        # Auto theme refresh setup
        self.auto_theme_thread = None
        self.auto_theme_running = False

        # Sizegrip Setup
        sizegrip = Sizegrip(self.app, bootstyle="info")
        sizegrip.place(relx=1.0, rely=1.0, anchor="se")

        
        self.app.title("Advanced Weather Dashboard")
        
        # Get screen dimensions
        screen_width = self.app.winfo_screenwidth()
        screen_height = self.app.winfo_screenheight()
        
        # Calculate window size (90% of screen size)
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Calculate position to center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window geometry (width x height + x_offset + y_offset)
        self.app.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.app.minsize(800, 600)  # Set minimum window size
        
        # Initialize data handler and API client with config
        self.data_handler = WeatherDataHandler(config)
        self.weather_api = WeatherAPI(config) if config else WeatherAPI()

        # Clean up old forecast data on startup
        self.data_handler.cleanup_old_forecast_data()

        # Forecast cache for robust display updates
        from utils.conversion.weather_conversion_service import ForecastCache
        self.forecast_cache = ForecastCache()

        self.setup_gui()
        

        
        # Load initial saved cities
        self.load_saved_cities()

    def start_auto_theme_refresh(self) -> None:
        """Start the auto theme refresh thread if auto mode is enabled"""
        if not self.theme_manager.is_auto_enabled():
            self.logger.info("Auto mode disabled - not starting refresh thread")
            return

        if not self.auto_theme_thread or not self.auto_theme_thread.is_alive():
            self.auto_theme_running = True
            self.auto_theme_thread = threading.Thread(target=self._auto_theme_loop, daemon=True)
            self.auto_theme_thread.start()
            self.logger.info("Auto theme refresh started")

    def stop_auto_theme_refresh(self) -> None:
        """Stop the auto theme refresh thread"""
        self.auto_theme_running = False
        if self.auto_theme_thread and self.auto_theme_thread.is_alive():
            self.auto_theme_thread.join(timeout=1.0)
            self.logger.info("Auto theme refresh stopped")


    def _auto_theme_loop(self) -> None:
        """Background thread for auto theme switching"""
        while self.auto_theme_running:
            try:
                self.logger.info(
                    f"[auto_theme_loop] Checking auto theme at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )

                # Get current theme from theme manager
                current_theme = self.theme_manager.current_theme
                
                # Apply current theme (will be auto-determined if auto mode is on)
                if self.theme_manager.apply_current_theme():
                    # Check if theme actually changed
                    new_theme = self.theme_manager.current_theme
                    if new_theme != getattr(self, '_last_auto_theme', None):
                        self.logger.info(f"Auto theme changed to: {new_theme}")
                        self._last_auto_theme = new_theme
                        
                        # Schedule component restyling on main thread to avoid segfaults
                        if hasattr(self, "restyle_all_components"):
                            self.app.after(0, self._restyle_components_safe)
                            self.logger.info("[auto_theme_loop] Components restyle scheduled on main thread")

                # Sleep for 30 minutes before next check
                for _ in range(1800):
                    if not self.auto_theme_running:
                        break
                    time.sleep(1)

            except Exception as e:
                self.logger.error(f"Error in auto theme refresh: {str(e)}")
                time.sleep(60)  # Wait a minute before trying again



    def setup_gui(self) -> None:
        """Create the tabbed interface"""
        # Theme controls at top (pass theme_manager instead of current_theme)
        self.theme_component = ThemeComponent(self.app, self.theme_manager)
        theme_controls = self.theme_component.theme_frame
        theme_controls.pack(pady=10)

        # Create notebook for tabs
        self.notebook = tb.Notebook(self.app, bootstyle="primary")
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.setup_weather_tab()
        self.setup_saved_cities_tab()
        self.setup_history_tab()
        self.setup_trivia_tab()
        self.setup_about_tab()
        
        # Start periodic auto theme refresh only when auto mode is enabled
        if self.theme_manager.is_auto_enabled():
            self.start_auto_theme_refresh()

    def setup_weather_tab(self):
        """Setup the main weather tab"""
        # Weather tab
        weather_tab = tb.Frame(self.notebook)
        self.notebook.add(weather_tab, text="🌤️ Weather")



        # Weather input component
        self.input_component = WeatherInputComponent(weather_tab)
        # Ensure callback signature matches: city, state, units
        self.input_component.set_weather_callback(lambda city, state, units: self.handle_weather_request(city, state, units))
        self.input_component.set_unit_change_callback(self.handle_unit_change)  # Add this line
        input_frame = self.input_component.setup_component()
        input_frame.pack(pady=10, padx=20, fill=X)

        # Weather display component
        self.weather_display = WeatherDisplayComponent(weather_tab)
        self.weather_display.set_save_city_callback(self.handle_save_city)
        display_frame = self.weather_display.setup_component()
        display_frame.pack(pady=20, fill=X)

        # Forecast display component
        self.forecast_display = ForecastDisplayComponent(weather_tab)
        forecast_frame = self.forecast_display.setup_component()
        forecast_frame.pack(pady=20, fill=BOTH, expand=True)  # Added expand=True

    def setup_saved_cities_tab(self):
        """Setup the saved cities tab"""
        saved_cities_tab = tb.Frame(self.notebook)
        self.notebook.add(saved_cities_tab, text="💾 Saved Cities")
        

        
        # Create saved cities component
        self.saved_cities_component = SavedCitiesComponent(saved_cities_tab)
        self.saved_cities_component.set_weather_callback(self.handle_weather_request)
        saved_cities_frame = self.saved_cities_component.setup_component()
        saved_cities_frame.pack(pady=10, padx=20, fill=BOTH, expand=True)

    def setup_history_tab(self):
        """Setup the weather history tab"""
        history_tab = tb.Frame(self.notebook)
        self.notebook.add(history_tab, text="📊 History")



        # Create history component
        self.history_component = HistoryComponent(history_tab)
        history_frame = self.history_component.setup_component()
        history_frame.pack(fill=BOTH, expand=True)

    def setup_trivia_tab(self):
        """Setup the trivia tab using modular TriviaTab"""
        try:
            trivia_tab = TriviaTab(self.notebook, csv_path="data/combined_data.csv")
            self.notebook.add(trivia_tab, text="🧠 Weather Trivia")
            
            
            
            self.logger.info("TriviaTab successfully added to notebook")
        except Exception as e:
            self.logger.error(f"Error setting up TriviaTab: {e}", exc_info=True)

    def setup_about_tab(self):
        """Setup the about tab with application information"""
        about_tab = tb.Frame(self.notebook)
        self.notebook.add(about_tab, text="ℹ️ About")

        # Create and setup the about component
        self.about_component = AboutComponent(about_tab)
        about_frame = self.about_component.setup_component()
        about_frame.pack(fill=BOTH, expand=True)
        
        return about_tab



    def load_saved_cities(self):
        """Load and display saved cities"""
        try:
            saved_cities = self.data_handler.load_saved_cities()
            self.logger.info(f"Loaded {len(saved_cities)} saved cities")
            if hasattr(self, 'saved_cities_component'):
                self.saved_cities_component.update_cities_list(saved_cities)
            if hasattr(self, 'history_component'):
                self.history_component.refresh_cities()
        except Exception as e:
            self.logger.error(f"Error loading saved cities: {str(e)}")
            Messagebox.show_error(
                "Failed to load saved cities",
                "There was an error loading your saved cities. Please try again later."
            )

    def handle_save_city(self, city_data: Dict[str, Any]) -> None:
        """Handle saving a city"""
        self.logger.debug("handle_save_city called with city_data: %s", city_data)
        try:
            if self.data_handler.save_city(city_data):
                self.logger.info(f"Successfully saved city: {city_data.get('city')}")
                self.load_saved_cities()  # Refresh the saved cities list
                Messagebox.show_info(
                    "City Saved",
                    f"Successfully saved {city_data.get('city')} to your saved cities."
                )
            else:
                self.logger.error(f"Failed to save city: {city_data.get('city')}")
                Messagebox.show_error(
                    "Error",
                    "Failed to save the city. Please try again."
                )
        except Exception as e:
            self.logger.error(f"Error in handle_save_city: {str(e)}")
            Messagebox.show_error(
                "Error",
                "An unexpected error occurred while saving the city."
            )

    def handle_weather_request(self, city: str, state: Optional[str] = None, units: Optional[str] = None, country: Optional[str] = None) -> None:
        """Handle weather data request and display, with forecast cache update. Units-aware."""
        try:
            # Show loading indicator
            self.weather_display.show_loading_indicator()
            
            # Normalize state abbreviation to uppercase
            state = normalize_state_abbreviation(state)
            
            # Get comprehensive weather data from API (current + forecast), passing units
            comprehensive_data = self.weather_api.fetch_comprehensive_weather(city, state, units)
            
            # Hide loading indicator
            self.weather_display.hide_loading_indicator()
            
            if comprehensive_data and 'error' not in comprehensive_data:
                # Extract current weather data for display and saving
                current_weather = comprehensive_data.get('current', {})
                location_data = comprehensive_data.get('location', {})
                
                # Check if fallback data was used (look for source field)
                used_fallback = False
                if current_weather.get('source') in ['static_fallback', 'random_fallback', 'random_historical_fallback']:
                    used_fallback = True
                
                # Build current weather data in expected format
                weather_data = {
                    "city": location_data.get('name', city),
                    "state": location_data.get('state', state),
                    "country": location_data.get('country', country or 'US'),
                    "latitude": location_data.get('lat'),
                    "longitude": location_data.get('lon'),
                    "temperature": current_weather.get('temp'),
                    "feels_like": current_weather.get('feels_like'),
                    "humidity": current_weather.get('humidity'),
                    "pressure": current_weather.get('pressure'),
                    "weather_main": current_weather.get('main'),
                    "weather_description": current_weather.get('description'),
                    "weather_icon": current_weather.get('icon'),
                    "wind_speed": current_weather.get('wind_speed'),
                    "wind_direction": current_weather.get('wind_deg'),
                    "visibility": current_weather.get('visibility'),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Set the correct unit label for display
                if units == 'metric':
                    weather_data['unit'] = '°C'
                else:
                    weather_data['unit'] = '°F'
                
                # Update display with current weather data and fallback status
                self.weather_display.update_display(weather_data, used_fallback)
                
                # Save weather data only if not using fallback
                if not used_fallback:
                    self.data_handler.save_weather_data_validated(weather_data)
                else:
                    self.logger.info(f"Using fallback data for {city} - skipping database save")
                
                # Update forecast if available
                forecast_data = comprehensive_data.get('forecast', [])
                if forecast_data:
                    # Set the correct unit label for each forecast day
                    unit_label = '°C' if units == 'metric' else '°F'
                    for day in forecast_data:
                        day['unit'] = unit_label
                    self.forecast_display.update_forecast_display(forecast_data)
                    # Store forecast data in cache with its unit
                    self.forecast_cache.store(forecast_data, units)
                    # Save forecast data to database only if not using fallback
                    if not used_fallback:
                        location_data = comprehensive_data.get('location', {})
                        forecast_city = location_data.get('name', city)
                        forecast_state = location_data.get('state', state)
                        forecast_country = location_data.get('country', country or 'US')
                        if self.data_handler.save_forecast_data(forecast_city, forecast_state, forecast_country, forecast_data):
                            self.logger.info(f"Successfully saved {len(forecast_data)} forecast days to database")
                        else:
                            self.logger.warning("Failed to save forecast data to database")
                        self.logger.info(f"Updated forecast with {len(forecast_data)} days")
                    else:
                        self.logger.info(f"Using fallback data for {city} forecast - skipping database save")
                else:
                    self.logger.warning("No forecast data available")
            else:
                error_msg = comprehensive_data.get('error', 'Unknown error') if comprehensive_data else 'No data received'
                self.logger.error(f"Failed to get weather data for {city}: {error_msg}")
                # Show a more user-friendly error message based on the error type
                if "city not found" in error_msg.lower() or "not found" in error_msg.lower():
                    error_display = f"City '{city}' was not found. Please check your spelling or try another city."
                elif "api key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    error_display = "Weather service access error. Please try again later."
                elif "limit" in error_msg.lower() and "rate" in error_msg.lower():
                    error_display = "Too many requests to the weather service. Please try again in a few minutes."
                elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                    error_display = "Connection timeout. Please check your internet connection and try again."
                else:
                    error_display = f"Failed to get weather data for '{city}'. Please try again later."
                # Display the popup error message
                Messagebox.show_error(
                    message="Error: PLEASE ENTER A VALID CITY AND STATE",
                    title="Invalid City"
                )
        except Exception as e:
            # Hide loading indicator on error
            self.weather_display.hide_loading_indicator()
            self.logger.error(f"Error in handle_weather_request: {str(e)}")
            Messagebox.show_error(
                message="Error: PLEASE ENTER A VALID CITY AND STATE",
                title="Invalid City"
            )


    def restyle_all_components(self):
        """Refresh the styles of all major components after a theme change."""
        if hasattr(self.input_component, "restyle"):
            self.input_component.restyle()
        if hasattr(self.weather_display, "restyle"):
            self.weather_display.restyle()
        if hasattr(self.forecast_display, "restyle"):
            self.forecast_display.restyle()
        if hasattr(self.saved_cities_component, "restyle"):
            self.saved_cities_component.restyle()
        if hasattr(self.history_component, "restyle"):
            self.history_component.restyle()
        if hasattr(self, 'trivia_component') and hasattr(self.trivia_component, "restyle"):
            try:
                self.trivia_component.restyle()
            except Exception as e:
                self.logger.error(f"Error restyling trivia component: {e}")

    def _restyle_components_safe(self):
        """Thread-safe wrapper for component restyling - called from main thread only."""
        try:
            self.restyle_all_components()
            self.logger.info("[main_thread] Components restyled after theme change")
        except Exception as e:
            self.logger.error(f"Error during safe component restyle: {e}")

    def handle_unit_change(self, new_unit: str) -> None:
        """Handle temperature unit change and update displays, using forecast cache for robustness"""
        self.logger.debug(f"Temperature unit changed to {new_unit}")
        # Get the currently displayed city and state
        city = self.input_component.get_city()
        state = self.input_component.get_state()
        if not city:
            return
        # Get current weather data from display
        current_data = self.weather_display.get_current_data()
        if not current_data:
            return
        # Get current unit before switching
        old_unit = 'metric' if new_unit == 'imperial' else 'imperial'
        # Convert temperatures without making API calls using clean service
        from utils.conversion.weather_conversion_service import WeatherConversionService
        converted_data = WeatherConversionService.convert_current_weather_data(current_data, old_unit, new_unit)
        # Set unit label for display (F/C)
        unit_label = '°C' if new_unit == 'metric' else '°F'
        # For flat structure
        if 'temperature' in converted_data:
            converted_data['unit'] = unit_label
        # For nested structure
        if 'current' in converted_data:
            converted_data['current']['unit'] = unit_label
        # Try to get forecast from converted_data, else use cache
        forecast_list = converted_data.get('forecast', [])
        if (not forecast_list or not isinstance(forecast_list, list)) and self.forecast_cache.has_data():
            # Get converted forecast data from cache (pure function, no mutation)
            forecast_list = self.forecast_cache.get_converted(new_unit)
        else:
            # Update forecast items with unit label if present
            for forecast in forecast_list:
                forecast['unit'] = unit_label
        # Update displays with converted data
        self.weather_display.update_display(converted_data)
        if hasattr(self, 'forecast_display'):
            if not isinstance(forecast_list, list):
                forecast_list = []
            self.forecast_display.update_forecast_display(forecast_list)


    def run(self):
        """Start the application main loop with proper cleanup"""
        try:
            self.logger.info("Starting main application loop")
            self.app.mainloop()
        except Exception as e:
            self.logger.error(f"Error in main loop: {str(e)}")
            raise
        finally:
            self.logger.info("Cleaning up resources...")
            self.stop_auto_theme_refresh()  # Stop auto theme thread
            
            # Close API session to clean up urllib3 connection pools
            try:
                if hasattr(self.weather_api, 'session'):
                    self.weather_api.session.close()
                    self.logger.info("API session closed")
            except Exception as e:
                self.logger.error(f"Error closing API session: {str(e)}")
            
            # Close database connection
            try:
                # The database uses context managers, so we don't need to manually close
                # SQLite connections are automatically closed when the context manager exits
                self.logger.info("Database connections will be closed automatically")
            except Exception as e:
                self.logger.error(f"Error during database cleanup: {str(e)}")
