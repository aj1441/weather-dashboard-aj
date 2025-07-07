"""Saved cities component for managing favorite locations"""

import customtkinter as ctk
from core.data_handler import WeatherDataHandler
import logging

class SavedCitiesComponent:
    """Handles displaying and managing saved cities (customtkinter only)"""

    def __init__(self, parent, data_directory=None):
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.weather_callback = None
        
        # Use the same data directory as the main app if provided
        self.data_handler = WeatherDataHandler(data_directory=data_directory or "data")
        self.forecast_items = {}  # Store forecast widgets by city

    def setup_component(self):
        """Create the saved cities section (customtkinter only)"""
        self.cities_frame = ctk.CTkFrame(self.parent)

        # Title
        title_label = ctk.CTkLabel(
            self.cities_frame,
            text="💾 Saved Cities",
            font=("Helvetica Neue", 20, "bold")
        )
        title_label.pack(pady=10)

        # Scrollable frame for cities list
        self.cities_list_frame = ctk.CTkScrollableFrame(self.cities_frame, height=180)
        self.cities_list_frame.pack(fill="x", padx=20, pady=10)

        # No cities message (initially shown)
        self.no_cities_label = ctk.CTkLabel(
            self.cities_list_frame,
            text="No saved cities yet.\nGet weather for a city and click '💾 Save City' to add it here!",
            font=("Helvetica Neue", 14),
            justify="center"
        )
        self.no_cities_label.pack(pady=40)

        # Separator
        separator = ctk.CTkLabel(self.cities_frame, text="", height=2)
        separator.pack(fill="x", padx=20, pady=10)

        return self.cities_frame

    def set_weather_callback(self, callback):
        """Set the callback for when a city is selected"""
        self.weather_callback = callback

    def update_cities_list(self, cities):
        """Update the display with the provided cities list"""
        self.logger.info(f"Updating cities list with {len(cities)} cities")
        
        # Clear existing city widgets
        for widget in self.cities_list_frame.winfo_children():
            widget.destroy()

        if not cities:
            self.logger.debug("No cities to display")
            # Show no cities message
            self.no_cities_label = ctk.CTkLabel(
                self.cities_list_frame,
                text="No saved cities yet.\nGet weather for a city and click '💾 Save City' to add it here!",
                font=("Helvetica Neue", 14),
                justify="center"
            )
            self.no_cities_label.pack(pady=40)
        else:
            self.logger.debug(f"Displaying {len(cities)} cities")
            # Create city cards
            for city_data in cities:
                self._create_city_card(city_data)

    def _create_city_card(self, city_data):
        """Create a card for a saved city"""
        # Create card frame
        card = ctk.CTkFrame(self.cities_list_frame)
        card.pack(fill="x", padx=10, pady=5)

        # City info
        city_name = f"{city_data.get('city')}"
        if city_data.get('state'):
            city_name += f", {city_data.get('state')}"
        if city_data.get('country') and city_data.get('country') != 'US':
            city_name += f", {city_data.get('country')}"

        city_label = ctk.CTkLabel(
            card,
            text=city_name,
            font=("Helvetica Neue", 14, "bold")
        )
        city_label.pack(side="left", padx=10, pady=5)

        # Get Weather button
        def get_weather():
            if self.weather_callback:
                self.weather_callback(
                    city_data.get('city'),
                    city_data.get('state'),
                    city_data.get('country')
                )

        weather_btn = ctk.CTkButton(
            card,
            text="🌤️ Get Weather",
            command=get_weather,
            width=120,
            font=("Helvetica Neue", 12)
        )
        weather_btn.pack(side="right", padx=10, pady=5)

        # Delete button
        def delete_city():
            self.data_handler.delete_city(
                city_data.get('city'),
                city_data.get('state'),
                city_data.get('country')
            )
            # Refresh the list after deletion
            saved_cities = self.data_handler.load_saved_cities()
            self.update_cities_list(saved_cities)

        delete_btn = ctk.CTkButton(
            card,
            text="🗑️ Delete",
            command=delete_city,
            width=80,
            font=("Helvetica Neue", 12),
            fg_color="red",
            hover_color="darkred"
        )
        delete_btn.pack(side="right", padx=5, pady=5)
