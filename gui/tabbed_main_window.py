"""Advanced tabbed weather dashboard with components"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import ttkbootstrap as tb
import logging
import threading
import time
from datetime import datetime
from ttkbootstrap.constants import LEFT, RIGHT, BOTH, X, Y, END
from ttkbootstrap.dialogs import Messagebox
from core.utils import load_user_theme
from core.api import WeatherAPI
from core.data_handler import WeatherDataHandler
from core.custom_themes import register_custom_themes
from gui.components import ThemeComponent, WeatherInputComponent, WeatherDisplayComponent, SavedCitiesComponent, ForecastDisplayComponent

class TabbedWeatherDashboard:
    """Advanced tabbed GUI with components and additional features"""

    def __init__(self, config=None):
        # Store config for components that need it
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Register custom themes first
        register_custom_themes()
        
        # Load last used theme
        self.current_theme = load_user_theme()
        self.auto_theme = False
        self.auto_theme_thread = None
        self.auto_theme_running = False
        
        # Initialize the window with the current theme
        try:
            self.app = tb.Window(themename=self.current_theme)
        except Exception as e:
            self.logger.warning(f"Failed to load custom theme {self.current_theme}, using default: {e}")
            self.app = tb.Window(themename="aj_darkly")
            self.current_theme = "aj_darkly"
        
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

    def sync_customtkinter_theme(self, theme_name):
        """Synchronize customtkinter theme with ttkbootstrap theme"""
        import customtkinter as ctk
        # Map our theme names to customtkinter appearance modes
        if theme_name == "aj_darkly":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        self.logger.info(f"Synchronized customtkinter theme to: {theme_name}")

    def _auto_theme_loop(self):
        """Background thread for auto theme switching"""
        while self.auto_theme_running:
            try:
                current_hour = datetime.now().hour
                new_theme = "aj_darkly" if current_hour >= 18 or current_hour < 6 else "aj_lightly"
                
                if new_theme != self.current_theme:
                    self.logger.info(f"Auto switching theme to {new_theme}")
                    self.app.style.theme_use(new_theme)
                    self.sync_customtkinter_theme(new_theme)  # Sync customtkinter theme
                    self.current_theme = new_theme
                
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
        theme_controls = self.theme_component.setup_component()
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
            ("Frontend", "ttkbootstrap (modern tkinter), customtkinter integration"),
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
        print(f"[DEBUG] handle_save_city called with city_data: {city_data}")
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
                Messagebox.show_error(
                    "Error",
                    f"Failed to get weather data for {city}. Please try again."
                )
        except Exception as e:
            self.logger.error(f"Error in handle_weather_request: {str(e)}")
            Messagebox.show_error(
                "Error",
                "An unexpected error occurred while getting weather data."
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
