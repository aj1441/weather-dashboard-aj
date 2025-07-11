"""Weather display component for showing current weather"""

import logging
import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, RIGHT, BOTH, X, Y, END
from core.icon_manager import get_weather_icon
from core.weather_utils import parse_weather_data

logger = logging.getLogger(__name__)

class WeatherDisplayComponent:
    """Handles displaying current weather data with emoji and save functionality"""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_weather_data = None
        self.setup_component()
    
    def setup_component(self):
        """Create the weather display section"""
        self.display_frame = tb.Frame(self.parent)
        
        # Weather emoji/icon
        self.weather_icon_label = tb.Label(
            self.display_frame, 
            text="🌡️", 
            font=("Helvetica Neue", 40)
        )
        self.weather_icon_label.pack(pady=10)
        
        # Weather description and temperature with save button
        desc_frame = tb.Frame(self.display_frame)
        desc_frame.pack(pady=5)
        
        self.weather_desc_label = tb.Label(
            desc_frame, 
            text="Enter a city to get weather data", 
            font=("Helvetica Neue", 14)
        )
        self.weather_desc_label.pack(side=LEFT)
        
        # Save city button (initially hidden)
        from core.save_city_utils import create_save_city_button
        self.save_city_btn = create_save_city_button(
            desc_frame,
            city_data=None,  # Will be set when weather is loaded
            on_save_callback=self.on_save_city,
            style='success-outline'
        )
        # Don't pack initially - will be shown when weather data is displayed
        
        # Additional details frame
        self.details_frame = tb.Frame(self.display_frame)
        self.details_frame.pack(pady=10)
        
        # Details labels (will be created when data is displayed)
        self.humidity_label = tb.Label(self.details_frame, text="")
        self.pressure_label = tb.Label(self.details_frame, text="")
        self.wind_label = tb.Label(self.details_frame, text="")
        
        # Progress bar (initially hidden)
        self.progress_bar = tb.Progressbar(
            self.display_frame,
            mode='indeterminate',
            bootstyle="info-striped"
        )
        
        return self.display_frame
    
    def update_weather_display(self, weather_data, temp_unit="imperial"):
        """
        Update the display with new weather data
        
        Args:
            weather_data: Dictionary with weather information (cleaned or raw format)
            temp_unit: 'imperial', 'metric', or 'kelvin'
        """
        logger.debug("update_weather_display called with weather_data: %s", weather_data)
        from core.unit_label_utils import get_unit_label, get_wind_unit_label
        unit_label = get_unit_label(temp_unit)
        wind_unit_label = get_wind_unit_label(temp_unit)
        if "error" in weather_data:
            logger.debug("Weather error: %s", weather_data['error'])
            self.show_error(weather_data["error"])
            return
        
        # Store current weather data for saving
        self.current_weather_data = weather_data
        
        # Use modularized parser
        parsed = parse_weather_data(weather_data, unit_label)
        logger.debug("Parsed weather data: %s", parsed)
        
        # Update emoji using IconManager
        emoji = get_weather_icon(parsed['description'])
        self.weather_icon_label.config(text=emoji)
        
        # Update main description
        temp_display = f"{round(parsed['temp'])}" if parsed['temp'] != "N/A" and parsed['temp'] is not None else "N/A"
        self.weather_desc_label.config(
            text=f"{parsed['description'].title() if parsed['description'] != 'N/A' else 'Unknown'} | {temp_display}{parsed['unit_label']}\n{parsed['city']}"
        )
        
        # Update save_city_btn city_data - make sure we're using the proper city name from API response
        self.save_city_btn.city_data = weather_data
        
        # Show save button
        self.save_city_btn.pack(side=LEFT, padx=10)
        
        # Update details
        from core.details_row_utils import update_weather_details_row
        update_weather_details_row(self.humidity_label, self.pressure_label, self.wind_label, {**parsed, 'wind_unit_label': wind_unit_label})
        self.humidity_label.pack(side=LEFT, padx=10)
        self.pressure_label.pack(side=LEFT, padx=10)
        self.wind_label.pack(side=LEFT, padx=10)
    
    def update_display(self, weather_data):
        """Update the weather display with new data"""
        if isinstance(weather_data, dict) and weather_data.get("error"):
            self.show_error(weather_data["error"])
            return

        try:
            # Store current weather data
            self.current_weather_data = weather_data

            # Set weather icon/emoji
            icon = weather_data.get('weather_icon', '')
            description = weather_data.get('weather_description', '').title()
            emoji = get_weather_icon(description)
            self.weather_icon_label.configure(text=emoji)

            # Format temperature
            temp = weather_data.get('temperature')
            if temp is not None:
                temp_str = f"{temp:.1f}°F"
            else:
                temp_str = "N/A"

            # Update description label
            city = weather_data.get('city', '')
            state = weather_data.get('state', '')
            location = f"{city}, {state}" if state else city
            desc_text = f"{location}: {temp_str} - {description}"
            self.weather_desc_label.configure(text=desc_text)

            # Update details
            humidity = weather_data.get('humidity', 'N/A')
            pressure = weather_data.get('pressure', 'N/A')
            wind_speed = weather_data.get('wind_speed', 'N/A')

            self.humidity_label.configure(text=f"💧 Humidity: {humidity}%")
            self.humidity_label.pack(side=LEFT, padx=10)

            self.pressure_label.configure(text=f"⭕ Pressure: {pressure} hPa")
            self.pressure_label.pack(side=LEFT, padx=10)

            self.wind_label.configure(text=f"💨 Wind: {wind_speed} mph")
            self.wind_label.pack(side=LEFT, padx=10)

            # Update save_city_btn city_data
            self.save_city_btn.city_data = weather_data

            # Show save button
            self.save_city_btn.pack(side=RIGHT, padx=10)

        except Exception as e:
            self.logger.error(f"Error updating weather display: {str(e)}")
            self.show_error("Failed to update weather display")

    def show_error(self, error_message):
        """Display an error message"""
        self.weather_icon_label.config(text="❌")
        
        # Check for specific error messages and make them more user-friendly
        if error_message == "City not found" or "not found" in error_message.lower():
            display_message = "PLEASE ENTER A VALID CITY AND STATE"
        elif "api" in error_message.lower() and "error" in error_message.lower():
            display_message = "WEATHER SERVICE UNAVAILABLE - Please try again later"
        elif "timeout" in error_message.lower() or "connection" in error_message.lower():
            display_message = "CONNECTION ERROR - Please check your internet connection"
        else:
            display_message = error_message
            
        self.weather_desc_label.config(text=f"Error: {display_message}")
        
        # Hide save button and details
        self.save_city_btn.pack_forget()
        self.humidity_label.pack_forget()
        self.pressure_label.pack_forget()
        self.wind_label.pack_forget()
    
    def clear_display(self):
        """Clear the weather display"""
        self.weather_icon_label.config(text="🌡️")
        self.weather_desc_label.config(text="Enter a city to get weather data")
        self.current_weather_data = None
        
        # Hide save button and details
        self.save_city_btn.pack_forget()
        self.humidity_label.pack_forget()
        self.pressure_label.pack_forget()
        self.wind_label.pack_forget()
    
    def on_save_city(self, city_data=None):
        """Handle save city button click"""
        logger.debug("on_save_city called with city_data: %s", city_data)
        logger.debug("Has save_city_callback: %s", hasattr(self, 'save_city_callback'))
        if city_data and hasattr(self, 'save_city_callback'):
            logger.debug("Calling save_city_callback with city_data: %s", city_data)
            self.save_city_callback(city_data)
        else:
            logger.debug("Not calling save_city_callback - city_data is None or callback not set")
    
    def set_save_city_callback(self, callback):
        """Set the callback function for when a city is saved"""
        self.save_city_callback = callback
    
    def show_loading_indicator(self):
        """Show loading spinner/indicator"""
        self.weather_icon_label.config(text="⏳")
        self.weather_desc_label.config(text="Loading weather data...")
        
        # Hide save button and details during loading
        self.save_city_btn.pack_forget()
        self.humidity_label.pack_forget()
        self.pressure_label.pack_forget()
        self.wind_label.pack_forget()
        
        # Start the progress bar animation
        self.progress_bar.pack(fill=X, padx=10, pady=5)
        self.progress_bar.start()
    
    def hide_loading_indicator(self):
        """Hide loading indicator"""
        # Stop and hide the progress bar
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        
        # Reset to default state if no data will be shown
        # The update_weather_display method will override these if data is available
        self.weather_icon_label.config(text="🌡️")
        self.weather_desc_label.config(text="Enter a city to get weather data")

    def restyle(self):
        try:
            def refresh_widget(widget):
                try:
                    widget.configure()
                except:
                    pass
                for child in widget.winfo_children():
                    refresh_widget(child)

            if hasattr(self, "display_frame"):
                self.display_frame.update_idletasks()
                refresh_widget(self.display_frame)

            self.logger.info("WeatherDisplayComponent restyled.")
        except Exception as e:
            self.logger.error(f"Error during restyle in WeatherDisplayComponent: {e}")

    def get_current_data(self) -> dict:
        """Get the currently displayed weather data
        
        Returns:
            Dictionary containing the current weather data and forecast
        """
        return self.current_data

