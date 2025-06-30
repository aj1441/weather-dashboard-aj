import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from core.utils import load_user_theme, save_user_theme
from core.api import fetch_weather_data
from core.data_handler import save_weather_data

class WeatherDashboard:
    """Main GUI class for the weather dashboard."""

    def __init__(self):
        # Load last used theme
        self.current_theme = load_user_theme()
        self.app = tb.Window(themename=self.current_theme)
        self.app.title("Weather Dashboard")
        self.app.geometry("600x450")

        self.setup_gui()


    def setup_gui(self):
        """Create and layout all GUI components."""
        # Theme toggle
        self.theme_var = tb.BooleanVar(value=(self.current_theme == "pulse"))

        toggle = tb.Checkbutton(
            self.app,
            text="☀ Light / 🌙 Dark",
            variable=self.theme_var,
            command=self.toggle_theme,
            bootstyle="info-round-toggle"
        )
        toggle.pack(pady=10)

        # Weather input section
        input_frame = tb.Frame(self.app)
        input_frame.pack(pady=10, padx=20, fill=X)
        
        tb.Label(input_frame, text="City:").pack(side=LEFT)
        self.city_entry = tb.Entry(input_frame, width=15)
        self.city_entry.pack(side=LEFT, padx=(5, 10))
        
        tb.Label(input_frame, text="State:").pack(side=LEFT)
        self.state_entry = tb.Entry(input_frame, width=5)
        self.state_entry.pack(side=LEFT, padx=(5, 10))
        
        get_weather_btn = tb.Button(
            input_frame,
            text="Get Weather",
            command=self.get_weather,
            bootstyle="primary"
        )
        get_weather_btn.pack(side=LEFT, padx=10)

        # Results display area
        self.results_text = tb.Text(self.app, height=15, width=70)
        self.results_text.pack(pady=10, padx=20, fill=BOTH, expand=True)

    def toggle_theme(self):
        """Toggle between light and dark themes and save."""
        if self.theme_var.get():
            self.app.style.theme_use("pulse")
            self.current_theme = "pulse"
        else:
            self.app.style.theme_use("vapor")
            self.current_theme = "vapor"

        save_user_theme(self.current_theme)

    def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_entry.get().strip()
        state = self.state_entry.get().strip()
        
        if not city or not state:
            self.results_text.insert(END, "Please enter both city and state.\n")
            return
        
        # Fetch weather data
        weather_data = fetch_weather_data(city, state)
        
        if "error" in weather_data:
            self.results_text.insert(END, f"Error: {weather_data['error']}\n")
            return
        
        # Save data
        save_weather_data(weather_data)
        
        # Display results
        self.display_weather_data(weather_data)

    def display_weather_data(self, data):
        """Display weather data in the results area."""
        city = data.get("name", "Unknown")
        temp = data.get("main", {}).get("temp", "N/A")
        description = data.get("weather", [{}])[0].get("description", "N/A")
        humidity = data.get("main", {}).get("humidity", "N/A")
        pressure = data.get("main", {}).get("pressure", "N/A")
        wind_speed = data.get("wind", {}).get("speed", "N/A")
        
        display_text = f"""
Weather for {city}:
Temperature: {temp}°F
Description: {description.title()}
Humidity: {humidity}%
Pressure: {pressure} hPa
Wind Speed: {wind_speed} mph
---

"""
        self.results_text.insert(END, display_text)
        self.results_text.see(END)

    def run(self):
        self.app.mainloop()

