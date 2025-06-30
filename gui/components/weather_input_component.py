"""Weather input component for the weather dashboard"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *

class WeatherInputComponent:
    """Handles weather input fields and unit selection"""
    
    def __init__(self, parent):
        self.parent = parent
        self.city_var = tb.StringVar()
        self.state_var = tb.StringVar()
        self.unit_var = tb.StringVar(value="imperial")  # default to Fahrenheit
        self.setup_component()
    
    def setup_component(self):
        """Create the input section with city, state, and unit toggle"""
        # Main input frame
        self.input_frame = tb.Frame(self.parent)
        
        # Unit toggle (F/C)
        self.unit_toggle = tb.Checkbutton(
            self.input_frame,
            text="°F / °C",
            variable=self.unit_var,
            onvalue="metric",
            offvalue="imperial",
            command=self.toggle_units,
            bootstyle="round-toggle"
        )
        self.unit_toggle.pack(side=RIGHT, padx=5)
        
        # City input
        tb.Label(self.input_frame, text="City:").pack(side=LEFT)
        self.city_entry = tb.Entry(self.input_frame, textvariable=self.city_var, width=15)
        self.city_entry.pack(side=LEFT, padx=(5, 10))
        
        # State input
        tb.Label(self.input_frame, text="State:").pack(side=LEFT)
        self.state_entry = tb.Entry(self.input_frame, textvariable=self.state_var, width=5)
        self.state_entry.pack(side=LEFT, padx=(5, 10))
        
        # Get weather button
        self.get_weather_btn = tb.Button(
            self.input_frame,
            text="Get Weather",
            command=self.on_get_weather,
            bootstyle="primary"
        )
        self.get_weather_btn.pack(side=LEFT, padx=10)
        
        return self.input_frame
    
    def toggle_units(self):
        """Toggle between Fahrenheit and Celsius"""
        # This will trigger any callbacks if set
        if hasattr(self, 'on_unit_change'):
            self.on_unit_change(self.unit_var.get())
    
    def on_get_weather(self):
        """Handle get weather button click"""
        city = self.city_var.get().strip()
        state = self.state_var.get().strip()
        units = self.unit_var.get()
        
        if hasattr(self, 'weather_callback'):
            self.weather_callback(city, state, units)
    
    def get_city(self):
        """Get the current city value"""
        return self.city_var.get().strip()
    
    def get_state(self):
        """Get the current state value"""
        return self.state_var.get().strip()
    
    def get_units(self):
        """Get the current units (imperial/metric)"""
        return self.unit_var.get()
    
    def get_unit_label(self):
        """Get the unit label for display (°F or °C)"""
        return "°C" if self.unit_var.get() == "metric" else "°F"
    
    def set_weather_callback(self, callback):
        """Set the callback function for when weather is requested"""
        self.weather_callback = callback
    
    def clear_inputs(self):
        """Clear all input fields"""
        self.city_var.set("")
        self.state_var.set("")
