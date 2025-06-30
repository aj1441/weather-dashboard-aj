"""Advanced tabbed weather dashboard with components"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, RIGHT, BOTH, X, Y, END
from ttkbootstrap.dialogs import Messagebox
from core.utils import load_user_theme
from core.api import fetch_weather_data
from core.data_handler import save_weather_data, WeatherDataHandler
from gui.components import ThemeComponent, WeatherInputComponent, WeatherDisplayComponent, SavedCitiesComponent

class TabbedWeatherDashboard:
    """Advanced tabbed GUI with components and additional features"""

    def __init__(self):
        # Load last used theme
        self.current_theme = load_user_theme()
        self.app = tb.Window(themename=self.current_theme)
        self.app.title("Advanced Weather Dashboard")
        self.app.geometry("800x600")
        
        # Initialize data handler
        self.data_handler = WeatherDataHandler()

        self.setup_gui()

    def setup_gui(self):
        """Create the tabbed interface"""
        # Theme toggle at top
        self.theme_component = ThemeComponent(self.app, self.current_theme)
        theme_toggle = self.theme_component.setup_component()
        theme_toggle.pack(pady=10)

        # Create notebook for tabs
        self.notebook = tb.Notebook(self.app, bootstyle="primary")
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.setup_weather_tab()
        self.setup_saved_cities_tab()
        self.setup_history_tab()
        self.setup_about_tab()

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

        # Add forecast placeholder (future enhancement)
        forecast_label = tb.Label(
            weather_tab, 
            text="7-Day Forecast (Coming Soon)", 
            font=("Helvetica Neue", 12),
            bootstyle="info"
        )
        forecast_label.pack(pady=20)

    def setup_saved_cities_tab(self):
        """Setup the saved cities tab"""
        saved_cities_tab = tb.Frame(self.notebook)
        self.notebook.add(saved_cities_tab, text="Saved Cities")
        
        # Saved cities component
        self.saved_cities_component = SavedCitiesComponent(saved_cities_tab)
        self.saved_cities_component.set_load_city_callback(self.handle_load_saved_city)
        self.saved_cities_component.set_remove_city_callback(self.handle_remove_saved_city)
        cities_frame = self.saved_cities_component.setup_component()
        cities_frame.pack(fill=BOTH, expand=True)
        
        # Refresh the cities list
        self.saved_cities_component.refresh_cities_list()

    def setup_history_tab(self):
        """Setup the weather history tab"""
        history_tab = tb.Frame(self.notebook)
        self.notebook.add(history_tab, text="History")

        # History content
        history_label = tb.Label(
            history_tab,
            text="Weather History & Charts",
            font=("Helvetica Neue", 16),
            anchor="center"
        )
        history_label.pack(pady=20)

        # Placeholder for history features
        placeholder = tb.Label(
            history_tab,
            text="- Temperature charts\n- Weather trends\n- Search history\n\n(Components coming soon...)",
            justify="center",
            font=("Helvetica Neue", 12)
        )
        placeholder.pack(pady=40)

    def setup_about_tab(self):
        """Setup the about tab"""
        about_tab = tb.Frame(self.notebook)
        self.notebook.add(about_tab, text="About")

        about_content = tb.Label(
            about_tab,
            text="""🌦️ Advanced Weather Dashboard

Built with component-based architecture using:
• ttkbootstrap for modern UI
• Modular components for maintainability  
• OpenWeatherMap API integration
• Theme switching capabilities

Features:
* Current weather display
* Temperature unit conversion
* Weather data persistence
* Component-based design
* 7-day forecasts (coming soon)
* Weather charts (coming soon)
* Mobile-responsive design (future)

Version 2.0 - Component Architecture""",
            justify="center",
            wraplength=600,
            font=("Helvetica Neue", 12)
        )
        about_content.pack(pady=60)

    def handle_weather_request(self, city, state, units):
        """Handle weather data request from input component"""
        if not city or not state:
            Messagebox.show_warning("Input Error", "Please enter both city and state.")
            return

        # Fetch weather data  
        weather_data = fetch_weather_data(city, state, units)

        if "error" in weather_data:
            Messagebox.show_error("Weather Error", weather_data["error"])
            return

        # Save data
        save_weather_data(weather_data)

        # Display results
        unit_label = self.input_component.get_unit_label()
        self.display_component.update_weather_display(weather_data, unit_label)

        # Show success message
        city_name = weather_data.get("name", city)
        Messagebox.show_info("Success", f"Weather data updated for {city_name}!")

    def handle_save_city(self, weather_data):
        """Handle saving a city from the weather display"""
        # Get the state from the input component
        state = self.input_component.get_state()
        
        # Save the city
        success = self.data_handler.save_city(weather_data, state)
        
        if success:
            city_name = weather_data.get("name", "City")
            Messagebox.show_info("City Saved", f"{city_name} has been saved to your favorites!")
            # Refresh the saved cities list if the tab is visible
            if hasattr(self, 'saved_cities_component'):
                self.saved_cities_component.refresh_cities_list()
        else:
            Messagebox.show_error("Save Error", "Failed to save city. Please try again.")

    def handle_load_saved_city(self, city_data):
        """Handle loading weather for a saved city"""
        city = city_data.get('city', '')
        state = city_data.get('state', '')
        
        if city:
            # Set the input fields
            self.input_component.city_var.set(city)
            if state:
                self.input_component.state_var.set(state)
            
            # Get the weather
            units = self.input_component.get_units()
            self.handle_weather_request(city, state, units)
            
            # Switch to weather tab
            self.notebook.select(0)  # Weather tab is first

    def handle_remove_saved_city(self, index):
        """Handle removing a saved city"""
        success = self.data_handler.remove_saved_city(index)
        if success:
            Messagebox.show_info("City Removed", "City has been removed from your favorites.")
        else:
            Messagebox.show_error("Remove Error", "Failed to remove city. Please try again.")

    def run(self):
        """Start the application"""
        self.app.mainloop()

if __name__ == "__main__":
    app = TabbedWeatherDashboard()
    app.run()
