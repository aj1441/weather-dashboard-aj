"""History component for analyzing historical weather data"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import logging
from typing import Dict, List, Optional, Callable
from core.database import get_database

logger = logging.getLogger(__name__)

class HistoryComponent:
    """Component for analyzing historical weather data with city comparison"""
    
    def __init__(self, parent):
        self.parent = parent
        self.db = get_database()
        self.logger = logging.getLogger(__name__)
        
        # State variables
        self.compare_mode = tb.BooleanVar(value=False)
        self.city1_var = tb.StringVar()
        self.city2_var = tb.StringVar()
        
        # Store available cities with historical data
        self.cities_with_data = []
        
        # UI components
        self.main_frame = None
        self.city1_dropdown = None
        self.city2_dropdown = None
        self.city2_frame = None
        self.analyze_button = None
        self.chart_area = None
        
    def setup_component(self):
        """Create and setup the history component"""
        # Main container frame
        self.main_frame = tb.Frame(self.parent)
        
        # Title
        title_label = tb.Label(
            self.main_frame,
            text="📊 Historical Weather Analysis",
            font=("Helvetica Neue", 18, "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Controls frame
        controls_frame = tb.Frame(self.main_frame)
        controls_frame.pack(fill=X, padx=20, pady=10)
        
        # City 1 selection
        city1_frame = tb.Frame(controls_frame)
        city1_frame.pack(fill=X, pady=(0, 10))
        
        tb.Label(
            city1_frame,
            text="Select City:",
            font=("Helvetica Neue", 12, "bold")
        ).pack(anchor=W)
        
        self.city1_dropdown = tb.Combobox(
            city1_frame,
            textvariable=self.city1_var,
            state="readonly",
            width=40
        )
        self.city1_dropdown.pack(pady=(5, 0), anchor=W)
        self.city1_dropdown.bind('<<ComboboxSelected>>', self._on_city_selection_changed)
        
        # Compare mode radio button
        compare_frame = tb.Frame(controls_frame)
        compare_frame.pack(fill=X, pady=(10, 0))
        
        self.compare_checkbox = tb.Checkbutton(
            compare_frame,
            text="Compare 2 Cities",
            variable=self.compare_mode,
            command=self._on_compare_mode_changed,
            bootstyle="primary"
        )
        self.compare_checkbox.pack(anchor=W)
        
        # City 2 selection (initially hidden)
        self.city2_frame = tb.Frame(controls_frame)
        
        tb.Label(
            self.city2_frame,
            text="Select Second City:",
            font=("Helvetica Neue", 12, "bold")
        ).pack(anchor=W)
        
        self.city2_dropdown = tb.Combobox(
            self.city2_frame,
            textvariable=self.city2_var,
            state="readonly",
            width=40
        )
        self.city2_dropdown.pack(pady=(5, 0), anchor=W)
        self.city2_dropdown.bind('<<ComboboxSelected>>', self._on_city_selection_changed)
        
        # Analyze button
        button_frame = tb.Frame(controls_frame)
        button_frame.pack(fill=X, pady=(20, 0))
        
        self.analyze_button = tb.Button(
            button_frame,
            text="Analyze Historical Data",
            command=self._on_analyze_clicked,
            bootstyle="primary",
            state="disabled"
        )
        self.analyze_button.pack(anchor=W)
        
        # Separator
        separator = tb.Separator(self.main_frame, orient="horizontal")
        separator.pack(fill=X, padx=20, pady=20)
        
        # Chart area
        self.chart_area = tb.Frame(self.main_frame)
        self.chart_area.pack(fill=BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Initial placeholder
        self._show_placeholder()
        
        # Load cities with historical data
        self._load_cities_with_data()
        
        return self.main_frame
    
    def _load_cities_with_data(self):
        """Load cities that have historical data"""
        try:
            # Get saved locations
            saved_locations = self.db.get_saved_locations()
            
            # Filter locations that have historical data
            self.cities_with_data = []
            for location in saved_locations:
                city = location.get('city')
                state = location.get('state')
                
                if city and state:
                    # Check if this city has historical data
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            SELECT COUNT(*) as count 
                            FROM historical_weather 
                            WHERE city = ? AND state = ?
                        ''', (city, state))
                        result = cursor.fetchone()
                        
                        if result and result['count'] > 0:
                            display_name = f"{city}, {state}"
                            self.cities_with_data.append({
                                'display_name': display_name,
                                'city': city,
                                'state': state,
                                'latitude': location.get('latitude'),
                                'longitude': location.get('longitude'),
                                'data_count': result['count']
                            })
            
            # Update dropdown values
            city_names = [city['display_name'] for city in self.cities_with_data]
            self.city1_dropdown['values'] = city_names
            self.city2_dropdown['values'] = city_names
            
            # Update placeholder if no data
            if not self.cities_with_data:
                self._show_no_data_message()
            
            self.logger.info(f"Loaded {len(self.cities_with_data)} cities with historical data")
            
        except Exception as e:
            self.logger.error(f"Error loading cities with historical data: {e}")
            self._show_error_message("Failed to load cities with historical data")
    
    def _on_compare_mode_changed(self):
        """Handle compare mode checkbox change"""
        if self.compare_mode.get():
            # Show second city dropdown
            self.city2_frame.pack(fill=X, pady=(10, 0))
            self._update_city2_options()
        else:
            # Hide second city dropdown
            self.city2_frame.pack_forget()
            self.city2_var.set("")
        
        self._update_analyze_button_state()
    
    def _on_city_selection_changed(self, event=None):
        """Handle city selection changes"""
        if self.compare_mode.get():
            self._update_city2_options()
        self._update_analyze_button_state()
    
    def _update_city2_options(self):
        """Update city2 dropdown to exclude city1 selection"""
        if not self.compare_mode.get():
            return
            
        selected_city1 = self.city1_var.get()
        available_cities = [
            city['display_name'] for city in self.cities_with_data
            if city['display_name'] != selected_city1
        ]
        
        self.city2_dropdown['values'] = available_cities
        
        # Clear city2 selection if it matches city1
        if self.city2_var.get() == selected_city1:
            self.city2_var.set("")
    
    def _update_analyze_button_state(self):
        """Update analyze button enabled/disabled state"""
        city1_selected = bool(self.city1_var.get())
        
        if self.compare_mode.get():
            # Need both cities selected for comparison
            city2_selected = bool(self.city2_var.get())
            can_analyze = city1_selected and city2_selected
        else:
            # Only need one city selected
            can_analyze = city1_selected
        
        self.analyze_button.configure(state="normal" if can_analyze else "disabled")
    
    def _on_analyze_clicked(self):
        """Handle analyze button click"""
        try:
            selected_city1 = self.city1_var.get()
            selected_city2 = self.city2_var.get() if self.compare_mode.get() else None
            
            if not selected_city1:
                return
            
            # Get city data
            city1_data = next((city for city in self.cities_with_data 
                             if city['display_name'] == selected_city1), None)
            
            city2_data = None
            if selected_city2:
                city2_data = next((city for city in self.cities_with_data 
                                 if city['display_name'] == selected_city2), None)
            
            if not city1_data:
                self._show_error_message("Selected city data not found")
                return
            
            # Clear chart area and show loading
            self._show_loading()
            
            # For now, show a placeholder chart message
            # This is where the actual chart will be implemented later
            self._show_chart_placeholder(city1_data, city2_data)
            
        except Exception as e:
            self.logger.error(f"Error analyzing historical data: {e}")
            self._show_error_message("Failed to analyze historical data")
    
    def _show_placeholder(self):
        """Show initial placeholder message"""
        self._clear_chart_area()
        
        placeholder_label = tb.Label(
            self.chart_area,
            text="📊 Select a city to analyze historical weather data\n\n" +
                 "Choose a city from the dropdown above, then click\n" +
                 "'Analyze Historical Data' to see the chart.\n\n" +
                 "Check 'Compare 2 Cities' to compare weather patterns\n" +
                 "between two different locations.",
            font=("Helvetica Neue", 12),
            justify=CENTER,
            bootstyle="secondary"
        )
        placeholder_label.pack(expand=True)
    
    def _show_no_data_message(self):
        """Show message when no historical data is available"""
        self._clear_chart_area()
        
        no_data_label = tb.Label(
            self.chart_area,
            text="⚠️ No Historical Data Available\n\n" +
                 "To use this feature:\n" +
                 "1. Go to the 'Saved Cities' tab\n" +
                 "2. Click 'History' button for any saved city\n" +
                 "3. Wait for historical data to be collected\n" +
                 "4. Return here to analyze the data",
            font=("Helvetica Neue", 12),
            justify=CENTER,
            bootstyle="warning"
        )
        no_data_label.pack(expand=True)
    
    def _show_loading(self):
        """Show loading message"""
        self._clear_chart_area()
        
        loading_label = tb.Label(
            self.chart_area,
            text="⏳ Loading historical data...",
            font=("Helvetica Neue", 14),
            bootstyle="info"
        )
        loading_label.pack(expand=True)
    
    def _show_chart_placeholder(self, city1_data: Dict, city2_data: Optional[Dict] = None):
        """Show placeholder for where the actual chart will be"""
        self._clear_chart_area()
        
        if city2_data:
            # Comparison mode
            chart_text = f"📊 Chart Area - Comparing:\n\n" +\
                        f"🏙️ {city1_data['display_name']} ({city1_data['data_count']} data points)\n" +\
                        f"🏙️ {city2_data['display_name']} ({city2_data['data_count']} data points)\n\n" +\
                        f"This is where the comparison chart will be displayed.\n" +\
                        f"The chart will show historical weather patterns\n" +\
                        f"for both cities side by side."
        else:
            # Single city mode
            chart_text = f"📊 Chart Area - Single City Analysis:\n\n" +\
                        f"🏙️ {city1_data['display_name']} ({city1_data['data_count']} data points)\n\n" +\
                        f"This is where the historical weather chart will be displayed.\n" +\
                        f"The chart will show weather patterns and trends\n" +\
                        f"for the selected city over time."
        
        chart_label = tb.Label(
            self.chart_area,
            text=chart_text,
            font=("Helvetica Neue", 12),
            justify=CENTER,
            bootstyle="primary"
        )
        chart_label.pack(expand=True)
    
    def _show_error_message(self, message: str):
        """Show error message in chart area"""
        self._clear_chart_area()
        
        error_label = tb.Label(
            self.chart_area,
            text=f"❌ Error: {message}",
            font=("Helvetica Neue", 12),
            justify=CENTER,
            bootstyle="danger"
        )
        error_label.pack(expand=True)
    
    def _clear_chart_area(self):
        """Clear all widgets from chart area"""
        for widget in self.chart_area.winfo_children():
            widget.destroy()
    
    def refresh_cities(self):
        """Refresh the list of cities with historical data"""
        self._load_cities_with_data()
        
        # Reset selections
        self.city1_var.set("")
        self.city2_var.set("")
        self.compare_mode.set(False)
        self.city2_frame.pack_forget()
        
        # Update UI
        self._update_analyze_button_state()
        if self.cities_with_data:
            self._show_placeholder()
        else:
            self._show_no_data_message()