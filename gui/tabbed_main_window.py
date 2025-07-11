"""Advanced tabbed weather dashboard with components"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import ttkbootstrap as tb
import logging
import threading
from core.state_utils import normalize_state_abbreviation
import time
from datetime import datetime
from ttkbootstrap.constants import LEFT, RIGHT, BOTH, X, Y, END
from ttkbootstrap.dialogs import Messagebox
from core.utils import load_user_theme
from core.api import WeatherAPI
from core.data_handler import WeatherDataHandler
from core.custom_themes import register_custom_themes, get_fallback_theme
from gui.components import ThemeComponent, WeatherInputComponent, WeatherDisplayComponent, SavedCitiesComponent, ForecastDisplayComponent

class TabbedWeatherDashboard:
    """Advanced tabbed GUI with components and additional features"""

    def __init__(self, config=None):
        # Store config for components that need it
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Load last used theme
        self.current_theme = load_user_theme()
        self.auto_theme = False
        self.auto_theme_thread = None
        self.auto_theme_running = False

        #1. Create the actual window BEFORE theme registration
        self.app = tb.Window()

        #2. Register themes now that we have a root window
        register_custom_themes()
        
        #3. Apply the user's theme
        try:
            style = tb.Style()
            style.theme_use(self.current_theme)
        except Exception as e:
            fallback = get_fallback_theme(self.current_theme)
            self.logger.warning(
                f"Failed to load theme {self.current_theme}, falling back to {fallback}: {e}"
            )
            style.theme_use(fallback)
            self.current_theme = fallback

        
        self.app.title("Advanced Weather Dashboard")
        self.app.geometry("1000x700")  # Increased from 800x600
        self.app.minsize(800, 600)  # Set minimum window size
        
        # Initialize data handler and API client with config
        self.data_handler = WeatherDataHandler(config)
        self.weather_api = WeatherAPI(config) if config else WeatherAPI()

        # Clean up old forecast data on startup
        self.data_handler.cleanup_old_forecast_data()

        self.setup_gui()
        
        # Load initial saved cities
        self.load_saved_cities()

    def start_auto_theme_refresh(self):
        """Start the auto theme refresh thread if auto theme is enabled"""
        self.auto_theme = True
        if not self.auto_theme_thread or not self.auto_theme_thread.is_alive():
                self.auto_theme_running = True
                self.auto_theme_thread = threading.Thread(target=self._auto_theme_loop, daemon=True)
                self.auto_theme_thread.start()
                self.logger.info("Auto theme refresh started")

    def stop_auto_theme_refresh(self):
        """Stop the auto theme refresh thread"""
        self.auto_theme_running = False
        if self.auto_theme_thread and self.auto_theme_thread.is_alive():
            self.auto_theme_thread.join(timeout=1.0)
            self.logger.info("Auto theme refresh stopped")


    def _auto_theme_loop(self):
        """Background thread for auto theme switching"""
        while self.auto_theme_running:
            try:
                self.logger.info(f"[auto_theme_loop] Checking time-based theme at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                current_hour = datetime.now().hour
                new_theme = "aj_darkly" if current_hour >= 18 or current_hour < 6 else "aj_lightly"
                
                if new_theme != self.current_theme:
                    self.logger.info(f"Auto switching theme to {new_theme}")
                    self.app.style.theme_use(new_theme)
                    self.current_theme = new_theme
                    self.app.update_idletasks()

                    #Notify all components to refresh
                    if hasattr(self, "restyle_all_components"):
                        self.restyle_all_components()
                        self.logger.info("[auto_theme_loop] Called restyle_all_components() after theme switch")

                
                # Sleep for 5 minutes before next check
                for _ in range(300):  # 5 minutes * 60 seconds = 300
                    if not self.auto_theme_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Error in auto theme refresh: {str(e)}")
                time.sleep(60)  # Wait a minute before trying again

    def setup_gui(self):
        """Create the tabbed interface"""
        # Theme controls at top
        self.theme_component = ThemeComponent(self.app, self.current_theme)
        theme_controls = self.theme_component.theme_frame
        theme_controls.pack(pady=10)

        # Create notebook for tabs
        self.notebook = tb.Notebook(self.app, bootstyle="primary")
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.setup_weather_tab()
        self.setup_saved_cities_tab()
        self.setup_history_tab()
        self.setup_about_tab()
        
        # Start periodic auto theme refresh if auto mode is enabled
        self.start_auto_theme_refresh()

    def setup_weather_tab(self):
        """Setup the main weather tab"""
        # Weather tab
        weather_tab = tb.Frame(self.notebook)
        self.notebook.add(weather_tab, text="🌤️ Weather")

        # Weather input component
        self.input_component = WeatherInputComponent(weather_tab)
        self.input_component.set_weather_callback(self.handle_weather_request)
        self.input_component.set_unit_change_callback(self.handle_unit_change)  # Add this line
        input_frame = self.input_component.setup_component()
        input_frame.pack(pady=10, padx=20, fill=X)

        # Weather display component
        self.display_component = WeatherDisplayComponent(weather_tab)
        self.display_component.set_save_city_callback(self.handle_save_city)
        display_frame = self.display_component.setup_component()
        display_frame.pack(pady=20, fill=X)

        # Forecast display component
        self.forecast_component = ForecastDisplayComponent(weather_tab)
        forecast_frame = self.forecast_component.setup_component()
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

        # Create title
        title_label = tb.Label(
            history_tab,
            text="Weather History",
            font=("Helvetica Neue", 20, "bold")
        )
        title_label.pack(pady=10)

        # Create scrollable frame for history entries
        self.history_frame = tb.Frame(history_tab)
        self.history_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create treeview for history
        columns = ("timestamp", "city", "temperature", "description")
        self.history_tree = tb.Treeview(
            self.history_frame,
            columns=columns,
            show="headings",
            height=10
        )

        # Configure columns
        self.history_tree.heading("timestamp", text="Date/Time")
        self.history_tree.heading("city", text="City")
        self.history_tree.heading("temperature", text="Temperature")
        self.history_tree.heading("description", text="Description")

        # Set column widths
        self.history_tree.column("timestamp", width=150)
        self.history_tree.column("city", width=150)
        self.history_tree.column("temperature", width=100)
        self.history_tree.column("description", width=200)

        # Add scrollbar
        scrollbar = tb.Scrollbar(
            self.history_frame,
            orient="vertical",
            command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        # Pack the treeview and scrollbar
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load initial history data
        self.load_history_data()

    def setup_about_tab(self):
        """Setup the about tab with application information"""
        about_tab = tb.Frame(self.notebook)
        self.notebook.add(about_tab, text="ℹ️ About")

        # Create scrollable frame for all content
        canvas = tb.Canvas(about_tab)
        scrollbar = tb.Scrollbar(about_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title
        title_label = tb.Label(
            scrollable_frame,
            text="🌦️ Weather Dashboard",
            font=("Helvetica Neue", 28, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(20, 10))

        # Version
        version_label = tb.Label(
            scrollable_frame,
            text="Version 2.0.0 - Component Architecture",
            font=("Helvetica Neue", 14),
            bootstyle="secondary"
        )
        version_label.pack(pady=(0, 20))

        # Description
        description = """
        A comprehensive weather dashboard application built with modern Python technologies.
        Features a component-based architecture for maintainability and extensibility.
        """
        desc_label = tb.Label(
            scrollable_frame,
            text=description,
            font=("Helvetica Neue", 12),
            justify="center",
            wraplength=600
        )
        desc_label.pack(pady=10)

        # Features frame
        features_frame = tb.Frame(scrollable_frame)
        features_frame.pack(fill="x", padx=40, pady=20)

        features = [
            ("🌤️ Current Weather", "Real-time weather data from OpenWeather API with detailed conditions"),
            ("� 7-Day Forecast", "Extended weather forecasts with intelligent data extension"),
            ("�💾 Save Cities", "Persistent storage of favorite locations with database integration"),
            ("📊 Weather History", "Complete weather history tracking with searchable records"),
            ("🎨 Custom Themes", "Multiple themes including custom aj_darkly and aj_lightly designs"),
            ("🌓 Auto Day/Night", "Automatic theme switching based on time and location"),
            ("🗄️ Database Storage", "SQLite database for reliable data persistence"),
            ("🔧 Component Architecture", "Modular design with reusable UI components")
        ]

        # Create feature labels
        for title, description in features:
            feature_frame = tb.Frame(features_frame)
            feature_frame.pack(fill="x", pady=8)
            
            tb.Label(
                feature_frame,
                text=title,
                font=("Helvetica Neue", 12, "bold"),
                bootstyle="primary"
            ).pack(anchor="w")
            
            tb.Label(
                feature_frame,
                text=description,
                font=("Helvetica Neue", 11),
                wraplength=500,
                bootstyle="secondary"
            ).pack(anchor="w", padx=(20, 0))

        # Technical Details
        tech_frame = tb.Frame(scrollable_frame)
        tech_frame.pack(fill="x", padx=40, pady=30)

        tb.Label(
            tech_frame,
            text="🔧 Technical Architecture",
            font=("Helvetica Neue", 16, "bold"),
            bootstyle="info"
        ).pack(pady=(0, 15))

        tech_details = [
            ("Frontend", "ttkbootstrap (modern tkinter)"),
            ("Backend", "Python 3.13+ with asyncio support"),
            ("Database", "SQLite with optimized schema design"),
            ("API Integration", "OpenWeather API with rate limiting and error handling"),
            ("Architecture", "Component-based with separation of concerns"),
            ("Configuration", "Centralized config management with environment variables")
        ]

        for tech, desc in tech_details:
            tech_item_frame = tb.Frame(tech_frame)
            tech_item_frame.pack(fill="x", pady=3)
            
            tb.Label(
                tech_item_frame,
                text=f"{tech}:",
                font=("Helvetica Neue", 11, "bold"),
                bootstyle="info"
            ).pack(anchor="w")
            
            tb.Label(
                tech_item_frame,
                text=desc,
                font=("Helvetica Neue", 10),
                wraplength=450
            ).pack(anchor="w", padx=(20, 0))

        # Status
        status_frame = tb.Frame(scrollable_frame)
        status_frame.pack(fill="x", padx=40, pady=20)

        tb.Label(
            status_frame,
            text="✅ Project Status: Fully Functional",
            font=("Helvetica Neue", 14, "bold"),
            bootstyle="success"
        ).pack(pady=10)

        status_items = [
            "✅ Current weather display working",
            "✅ 7-day forecast implementation complete",
            "✅ Save city functionality operational",
            "✅ Database persistence working",
            "✅ Theme system fully functional",
            "✅ Component architecture implemented"
        ]

        for status in status_items:
            tb.Label(
                status_frame,
                text=status,
                font=("Helvetica Neue", 11),
                bootstyle="success"
            ).pack(anchor="w", padx=20)

        # Credits
        credits_frame = tb.Frame(scrollable_frame)
        credits_frame.pack(fill="x", pady=30)

        tb.Label(
            credits_frame,
            text="Created by AJ",
            font=("Helvetica Neue", 12, "bold"),
            bootstyle="secondary"
        ).pack()

        tb.Label(
            credits_frame,
            text="Capstone Project - Weather Dashboard Application",
            font=("Helvetica Neue", 10),
            bootstyle="secondary"
        ).pack(pady=(5, 20))

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load_saved_cities(self):
        """Load and display saved cities"""
        try:
            saved_cities = self.data_handler.load_saved_cities()
            self.logger.info(f"Loaded {len(saved_cities)} saved cities")
            if hasattr(self, 'saved_cities_component'):
                self.saved_cities_component.update_cities_list(saved_cities)
        except Exception as e:
            self.logger.error(f"Error loading saved cities: {str(e)}")
            Messagebox.show_error(
                "Failed to load saved cities",
                "There was an error loading your saved cities. Please try again later."
            )

    def handle_save_city(self, city_data):
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

    def handle_weather_request(self, city, state=None, country=None):
        """Handle weather data request and display"""
        try:
            # Normalize state abbreviation to uppercase
            state = normalize_state_abbreviation(state)
            
            # Get comprehensive weather data from API (current + forecast)
            comprehensive_data = self.weather_api.fetch_comprehensive_weather(city, state)
            if comprehensive_data and 'error' not in comprehensive_data:
                # Extract current weather data for display and saving
                current_weather = comprehensive_data.get('current', {})
                location_data = comprehensive_data.get('location', {})
                
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
                
                # Update display with current weather data
                self.display_component.update_display(weather_data)
                
                # Save weather data
                self.data_handler.save_weather_data_validated(weather_data)
                
                # Update forecast if available
                forecast_data = comprehensive_data.get('forecast', [])
                if forecast_data:
                    self.forecast_component.update_forecast_display(forecast_data)
                    
                    # Save forecast data to database
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
            self.logger.error(f"Error in handle_weather_request: {str(e)}")
            Messagebox.show_error(
                message="Error: PLEASE ENTER A VALID CITY AND STATE",
                title="Invalid City"
            )

    def load_history_data(self):
        """Load weather history data into the treeview"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        try:
            # Get weather history from database
            with self.data_handler.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, city, temperature, weather_description
                    FROM current_weather
                    ORDER BY timestamp DESC
                    LIMIT 100
                ''')
                history_data = cursor.fetchall()

                # Add items to treeview
                for item in history_data:
                    # Convert timestamp to local time
                    try:
                        timestamp = datetime.fromisoformat(item['timestamp'])
                        formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                    except (ValueError, TypeError):
                        formatted_time = item['timestamp']

                    # Format temperature
                    try:
                        temp = f"{float(item['temperature']):.1f}°F"
                    except (ValueError, TypeError):
                        temp = "N/A"

                    self.history_tree.insert(
                        "",
                        "end",
                        values=(
                            formatted_time,
                            item['city'],
                            temp,
                            item['weather_description']
                        )
                    )

        except Exception as e:
            self.logger.error(f"Error loading history data: {str(e)}")
            # Show error in tree view
            self.history_tree.insert(
                "",
                "end",
                values=("Error", "Failed to load weather history", "", "")
            )

    def restyle_all_components(self):
        """Refresh the styles of all major components after a theme change."""
        if hasattr(self.input_component, "restyle"):
            self.input_component.restyle()
        if hasattr(self.display_component, "restyle"):
            self.display_component.restyle()
        if hasattr(self.forecast_component, "restyle"):
            self.forecast_component.restyle()
        if hasattr(self.saved_cities_component, "restyle"):
            self.saved_cities_component.restyle()

    def handle_unit_change(self, new_unit):
        """Handle temperature unit change and update displays"""
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
        
        # Convert temperatures without making API calls
        converted_data = self._convert_temperature_data(current_data, old_unit, new_unit)
        
        # Update displays with converted data
        self.weather_display.update_display(converted_data)
        if hasattr(self, 'forecast_display'):
            self.forecast_display.update_forecast(converted_data.get('forecast', []))

    def _convert_temperature_data(self, data: dict, from_unit: str, to_unit: str) -> dict:
        """Convert temperature values in weather data between units
        
        Args:
            data: Weather data dictionary
            from_unit: Current unit ('imperial' or 'metric')
            to_unit: Target unit ('imperial' or 'metric')
            
        Returns:
            Dictionary with converted temperature values
        """
        from core.conversion_utils import convert_to_celsius, convert_to_fahrenheit
        
        if from_unit == to_unit:
            return data
            
        converted = data.copy()
        
        # Convert main temperature values
        if 'temp' in converted.get('current', {}):
            if to_unit == 'metric':
                converted['current']['temp'] = convert_to_celsius(data['current']['temp'])
                if 'feels_like' in converted['current']:
                    converted['current']['feels_like'] = convert_to_celsius(data['current']['feels_like'])
            else:
                converted['current']['temp'] = convert_to_fahrenheit(data['current']['temp'])
                if 'feels_like' in converted['current']:
                    converted['current']['feels_like'] = convert_to_fahrenheit(data['current']['feels_like'])
        
        # Convert forecast temperatures
        for forecast in converted.get('forecast', []):
            if to_unit == 'metric':
                forecast['temp_min'] = convert_to_celsius(forecast['temp_min'])
                forecast['temp_max'] = convert_to_celsius(forecast['temp_max'])
                forecast['temp_day'] = convert_to_celsius(forecast['temp_day'])
                forecast['temp_night'] = convert_to_celsius(forecast['temp_night'])
            else:
                forecast['temp_min'] = convert_to_fahrenheit(forecast['temp_min'])
                forecast['temp_max'] = convert_to_fahrenheit(forecast['temp_max'])
                forecast['temp_day'] = convert_to_fahrenheit(forecast['temp_day'])
                forecast['temp_night'] = convert_to_fahrenheit(forecast['temp_night'])
        
        return converted

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
            try:
                self.data_handler.db.get_connection().close()  # Close database connection
            except Exception as e:
                self.logger.error(f"Error closing database connection: {str(e)}")
