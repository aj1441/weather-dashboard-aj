"""Saved cities component for managing favorite locations"""

import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, RIGHT, BOTH, X, Y, END
from core.data_handler import WeatherDataHandler

class SavedCitiesComponent:
    """Handles displaying and managing saved cities"""
    
    def __init__(self, parent):
        self.parent = parent
        self.data_handler = WeatherDataHandler()
        self.setup_component()
    
    def setup_component(self):
        """Create the saved cities section"""
        self.cities_frame = tb.Frame(self.parent)
        
        # Title
        title_label = tb.Label(
            self.cities_frame,
            text="💾 Saved Cities",
            font=("Helvetica Neue", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Scrollable frame for cities list
        self.cities_list_frame = tb.Frame(self.cities_frame)
        self.cities_list_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # No cities message (initially shown)
        self.no_cities_label = tb.Label(
            self.cities_list_frame,
            text="No saved cities yet.\nGet weather for a city and click '💾 Save City' to add it here!",
            font=("Helvetica Neue", 12),
            justify="center"
        )
        self.no_cities_label.pack(pady=40)
        
        return self.cities_frame
    
    def refresh_cities_list(self):
        """Refresh the display of saved cities"""
        # Clear existing city widgets
        for widget in self.cities_list_frame.winfo_children():
            widget.destroy()
        
        # Load saved cities
        saved_cities = self.data_handler.load_saved_cities()
        
        if not saved_cities:
            # Show no cities message
            self.no_cities_label = tb.Label(
                self.cities_list_frame,
                text="No saved cities yet.\nGet weather for a city and click '💾 Save City' to add it here!",
                font=("Helvetica Neue", 12),
                justify="center"
            )
            self.no_cities_label.pack(pady=40)
        else:
            # Create city cards
            for i, city_data in enumerate(saved_cities):
                self.create_city_card(city_data, i)
    
    def create_city_card(self, city_data, index):
        """Create a card widget for a saved city"""
        # Main card frame
        card_frame = tb.Frame(self.cities_list_frame, bootstyle="secondary")
        card_frame.pack(fill=X, pady=5, padx=10)
        
        # City info frame (left side)
        info_frame = tb.Frame(card_frame)
        info_frame.pack(side=LEFT, fill=X, expand=True, padx=10, pady=10)
        
        # City name and state
        city_name = city_data.get('city', 'Unknown')
        state_name = city_data.get('state', '')
        location_text = f"{city_name}, {state_name}" if state_name else city_name
        
        city_label = tb.Label(
            info_frame,
            text=location_text,
            font=("Helvetica Neue", 14, "bold")
        )
        city_label.pack(anchor="w")
        
        # Last updated info
        last_updated = city_data.get('last_updated', 'Unknown')
        if last_updated != 'Unknown':
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_updated)
                time_str = dt.strftime("%b %d, %Y at %I:%M %p")
                last_updated = time_str
            except:
                pass
        
        time_label = tb.Label(
            info_frame,
            text=f"Saved: {last_updated}",
            font=("Helvetica Neue", 10),
            bootstyle="secondary"
        )
        time_label.pack(anchor="w")
        
        # Button frame (right side)
        button_frame = tb.Frame(card_frame)
        button_frame.pack(side=RIGHT, padx=10, pady=10)
        
        # Load weather button
        load_btn = tb.Button(
            button_frame,
            text="🌡️ Get Weather",
            bootstyle="primary-outline",
            command=lambda: self.on_load_city(city_data)
        )
        load_btn.pack(side=LEFT, padx=5)
        
        # Remove city button
        remove_btn = tb.Button(
            button_frame,
            text="🗑️ Remove",
            bootstyle="danger-outline",
            command=lambda: self.on_remove_city(index)
        )
        remove_btn.pack(side=LEFT, padx=5)
    
    def on_load_city(self, city_data):
        """Handle loading weather for a saved city"""
        if hasattr(self, 'load_city_callback'):
            self.load_city_callback(city_data)
    
    def on_remove_city(self, index):
        """Handle removing a saved city"""
        if hasattr(self, 'remove_city_callback'):
            self.remove_city_callback(index)
        self.refresh_cities_list()
    
    def set_load_city_callback(self, callback):
        """Set callback for when a city is loaded"""
        self.load_city_callback = callback
    
    def set_remove_city_callback(self, callback):
        """Set callback for when a city is removed"""
        self.remove_city_callback = callback
