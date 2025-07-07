"""7-day forecast display component for weather dashboard"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import LEFT, RIGHT, BOTH, X, Y, TOP, BOTTOM
from datetime import datetime
from core.icon_manager import get_icon_manager

class ForecastDisplayComponent:
    """Handles displaying 7-day weather forecast (starting from tomorrow)"""
    
    def __init__(self, parent):
        self.parent = parent
        self.forecast_data = None
        self.forecast_cards = []
        
    def setup_component(self):
        """Create the forecast display section"""
        # Main forecast frame
        self.forecast_frame = tb.Frame(self.parent)
        
        # Forecast title
        self.forecast_title = tb.Label(
            self.forecast_frame,
            text="📅 7-Day Forecast",
            font=("Helvetica Neue", 16, "bold"),
            bootstyle="primary"
        )
        self.forecast_title.pack(pady=(10, 20))
        
        # Cards container - make it responsive
        # Create a scrollable frame for the forecast cards
        self.forecast_cards_frame = tb.Frame(self.forecast_frame)
        self.forecast_cards_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Initial placeholder
        self.show_placeholder()
        
        return self.forecast_frame
    
    def show_placeholder(self):
        """Show placeholder when no forecast data is available"""
        placeholder = tb.Label(
            self.forecast_cards_frame,
            text="Search for a city to see the 7-day forecast",
            font=("Helvetica Neue", 12),
            bootstyle="info"
        )
        placeholder.pack(pady=40, expand=True)
    
    def update_forecast_display(self, forecast_data):
        """Update the forecast display with new data"""
        self.forecast_data = forecast_data
        
        # Clear existing forecast cards
        for widget in self.forecast_cards_frame.winfo_children():
            widget.destroy()
        self.forecast_cards.clear()
        
        if not forecast_data:
            self.show_placeholder()
            return
        
        # Create forecast cards with uniform grid layout
        from core.forecast_card import create_forecast_card_tk
        icon_manager = get_icon_manager()
        
        # Create a container frame that uses grid for equal sizing
        cards_container = tb.Frame(self.forecast_cards_frame)
        cards_container.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create forecast cards using grid for equal distribution
        for i, day_data in enumerate(forecast_data[:7]):  # Show 7 days starting from tomorrow
            card = create_forecast_card_tk(cards_container, day_data, i, icon_manager, style='main')
            # Use grid with equal weight for all columns
            card.grid(row=0, column=i, padx=2, pady=5, sticky="nsew")
            self.forecast_cards.append(card)
        
        # Configure all columns to have equal weight (uniform sizing)
        for i in range(7):
            cards_container.grid_columnconfigure(i, weight=1, uniform="forecast_cards")
        
        # Configure row to expand vertically
        cards_container.grid_rowconfigure(0, weight=1)
    
    def create_forecast_card(self, day_data, index):
        """(Deprecated: replaced by create_forecast_card_tk)"""
        pass
    
    def clear_forecast(self):
        """Clear the forecast display"""
        for widget in self.forecast_cards_frame.winfo_children():
            widget.destroy()
        self.forecast_cards.clear()
        
        self.show_placeholder()
