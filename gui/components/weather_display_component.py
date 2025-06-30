"""Weather display component for showing current weather"""

import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, RIGHT, BOTH, X, Y, END
from core.icon_manager import get_weather_icon

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
        self.save_city_btn = tb.Button(
            desc_frame,
            text="💾 Save City",
            bootstyle="success-outline",
            command=self.on_save_city
        )
        # Don't pack initially - will be shown when weather data is displayed
        
        # Additional details frame
        self.details_frame = tb.Frame(self.display_frame)
        self.details_frame.pack(pady=10)
        
        # Details labels (will be created when data is displayed)
        self.humidity_label = tb.Label(self.details_frame, text="")
        self.pressure_label = tb.Label(self.details_frame, text="")
        self.wind_label = tb.Label(self.details_frame, text="")
        
        return self.display_frame
    
    def update_weather_display(self, weather_data, unit_label="°F"):
        """
        Update the display with new weather data
        
        Args:
            weather_data: Dictionary with weather information
            unit_label: Temperature unit label (°F or °C)
        """
        if "error" in weather_data:
            self.show_error(weather_data["error"])
            return
        
        # Store current weather data for saving
        self.current_weather_data = weather_data
        
        # Extract weather information
        city = weather_data.get("name", "Unknown")
        temp = weather_data.get("main", {}).get("temp", "N/A")
        description = weather_data.get("weather", [{}])[0].get("description", "N/A")
        humidity = weather_data.get("main", {}).get("humidity", "N/A")
        pressure = weather_data.get("main", {}).get("pressure", "N/A")
        wind_speed = weather_data.get("wind", {}).get("speed", "N/A")
        
        # Update emoji using IconManager
        emoji = get_weather_icon(description)
        self.weather_icon_label.config(text=emoji)
        
        # Update main description
        temp_display = f"{round(temp)}" if temp != "N/A" else "N/A"
        self.weather_desc_label.config(
            text=f"{description.title()} | {temp_display}{unit_label}\n{city}"
        )
        
        # Show save button
        self.save_city_btn.pack(side=LEFT, padx=10)
        
        # Update details
        self.humidity_label.config(text=f"💧 Humidity: {humidity}%")
        self.humidity_label.pack(side=LEFT, padx=10)
        
        self.pressure_label.config(text=f"🌡️ Pressure: {pressure} hPa")
        self.pressure_label.pack(side=LEFT, padx=10)
        
        wind_display = f"{wind_speed} mph" if unit_label == "°F" else f"{wind_speed} m/s"
        self.wind_label.config(text=f"🌬️ Wind: {wind_display}")
        self.wind_label.pack(side=LEFT, padx=10)
    
    def show_error(self, error_message):
        """Display an error message"""
        self.weather_icon_label.config(text="❌")
        self.weather_desc_label.config(text=f"Error: {error_message}")
        
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
    
    def on_save_city(self):
        """Handle save city button click"""
        if self.current_weather_data and hasattr(self, 'save_city_callback'):
            self.save_city_callback(self.current_weather_data)
    
    def set_save_city_callback(self, callback):
        """Set the callback function for when a city is saved"""
        self.save_city_callback = callback
