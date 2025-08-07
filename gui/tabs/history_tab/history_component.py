"""History component for analyzing historical weather data"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
# Defer matplotlib imports to prevent early bus errors
MATPLOTLIB_AVAILABLE = False
plt = None
FigureCanvasTkAgg = None
Figure = None
np = None

def _import_matplotlib():
    """Lazy import matplotlib when actually needed"""
    global MATPLOTLIB_AVAILABLE, plt, FigureCanvasTkAgg, Figure, np
    if MATPLOTLIB_AVAILABLE:
        return True
    try:
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from matplotlib.figure import Figure
        import numpy as np
        MATPLOTLIB_AVAILABLE = True
        return True
    except ImportError as e:
        logger.error(f"Failed to import matplotlib: {e}")
        return False
from core.database.database import get_database
from services.chart_data_service import ChartDataService
from utils.decorators import log_execution_time
# Add import for the new analysis window
from gui.tabs.history_tab.historical_analysis_window import HistoricalAnalysisWindow

logger = logging.getLogger(__name__)

class HistoryComponent:
    """Component for analyzing historical weather data with city comparison"""
    
    def __init__(self, parent):
        self.parent = parent
        self.db = get_database()
        self.chart_service = ChartDataService()
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
        self.city2_label = None
        self.city2_frame = None
        self.analyze_button = None
        self.chart_area = None
        
        # Chart quadrants
        self.temp_chart_frame = None
        self.precip_chart_frame = None
        self.humidity_chart_frame = None
        self.weather_chart_frame = None
        
        # Chart data storage
        self.chart_data = {}
        
        # Fallback notification
        self.fallback_notification = None
        
    def setup_component(self):
        """Create and setup the history component"""
        # Main container frame
        self.main_frame = tb.Frame(self.parent)
        
        # Create main grid container
        main_container = tb.Frame(self.main_frame)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Configure grid weights - fix layout constraints
        main_container.rowconfigure(0, weight=0, minsize=120)  # Top section (fixed height)
        main_container.rowconfigure(1, weight=0)  # Separator
        main_container.rowconfigure(2, weight=0)  # Fallback notification
        main_container.rowconfigure(3, weight=1)  # Chart area (expandable)
        main_container.columnconfigure(0, weight=1)
        
        # Top section frame (1/4 of height)
        top_frame = tb.Frame(main_container)
        top_frame.grid(row=0, column=0, sticky="ew", pady=(5, 10))
        top_frame.columnconfigure(0, weight=1)
        
        # Title in top section
        title_label = tb.Label(
            top_frame,
            text="📊 Historical Weather Analysis",
            font=("Helvetica Neue", 16, "bold")
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=(2, 8))
        title_label.configure(anchor="center")
        
        # Controls frame (full width)
        controls_frame = tb.Frame(top_frame)
        controls_frame.grid(row=1, column=0, sticky="ew", padx=(10, 10))
        controls_frame.columnconfigure(0, weight=1)
        controls_frame.columnconfigure(1, weight=1)
        controls_frame.columnconfigure(2, weight=1)
        controls_frame.columnconfigure(3, weight=0)
        controls_frame.columnconfigure(4, weight=0)
        controls_frame.columnconfigure(5, weight=0)
        controls_frame.columnconfigure(6, weight=0)
        
        # City 1 selection
        tb.Label(
            controls_frame,
            text="Select City:",
            font=("Helvetica Neue", 11, "bold")
        ).grid(row=0, column=0, sticky="w", padx=(0, 5), pady=(0, 3))
        
        self.city1_dropdown = tb.Combobox(
            controls_frame,
            textvariable=self.city1_var,
            state="readonly",
            width=18
        )
        self.city1_dropdown.grid(row=1, column=0, sticky="w", padx=(0, 15))
        self.city1_dropdown.bind('<<ComboboxSelected>>', self._on_city_selection_changed)
        
        # City 2 selection (initially hidden)
        self.city2_label = tb.Label(
            controls_frame,
            text="Second City:",
            font=("Helvetica Neue", 11, "bold")
        )
        self.city2_label.grid(row=0, column=1, sticky="w", padx=(0, 5), pady=(0, 3))
        self.city2_label.grid_remove()  # Initially hidden
        
        self.city2_dropdown = tb.Combobox(
            controls_frame,
            textvariable=self.city2_var,
            state="readonly",
            width=18
        )
        self.city2_dropdown.grid(row=1, column=1, sticky="w", padx=(0, 15))
        self.city2_dropdown.grid_remove()  # Initially hidden
        self.city2_dropdown.bind('<<ComboboxSelected>>', self._on_city_selection_changed)
        
        # Compare checkbox
        self.compare_checkbox = tb.Checkbutton(
            controls_frame,
            text="Compare 2 Cities",
            variable=self.compare_mode,
            command=self._on_compare_mode_changed,
            bootstyle="primary"
        )
        self.compare_checkbox.grid(row=1, column=2, sticky="w", padx=(0, 15))
        
        # Analyze button
        self.analyze_button = tb.Button(
            controls_frame,
            text="📊 Analyze Historical Data",
            command=self._on_analyze_clicked,
            bootstyle="primary",
            state="disabled"
        )
        self.analyze_button.grid(row=1, column=3, sticky="e", padx=(10, 5))
        
        # Fetch 7-day button
        self.fetch_7day_button = tb.Button(
            controls_frame,
            text="📊 Get Latest History",
            command=self._on_fetch_7day_clicked,
            bootstyle="success-outline",
            state="disabled"
        )
        self.fetch_7day_button.grid(row=1, column=4, sticky="e", padx=(5, 5))
        
        # Clear charts button
        self.clear_charts_button = tb.Button(
            controls_frame,
            text="🗑️ Clear Charts",
            command=self._on_clear_charts_clicked,
            bootstyle="danger-outline",
            state="disabled"
        )
        self.clear_charts_button.grid(row=1, column=5, sticky="e", padx=(5, 0))
        
        # Separator
        separator = tb.Separator(main_container, orient="horizontal")
        separator.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # Fallback notification (initially hidden)
        self.fallback_notification = tb.Label(
            main_container,
            text="⚠️ Historical data is currently unavailable, but here is what conditions have been in the past.",
            foreground="orange",
            font=("Helvetica Neue", 10, "italic"),
            wraplength=600
        )
        self.fallback_notification.grid(row=2, column=0, sticky="ew", padx=20, pady=(5, 0))
        self.fallback_notification.grid_remove()  # Initially hidden
        
        # Bottom section - Chart area (2/3 of height)
        self.chart_area = tb.Frame(main_container)
        self.chart_area.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Setup 4-quadrant chart layout
        self._setup_chart_quadrants()
        
        # Bind resize event to update charts when window is resized
        self.chart_area.bind('<Configure>', self._on_chart_area_resize)
        
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
            # Show second city dropdown and label
            self.city2_label.grid()
            self.city2_dropdown.grid()
            self._update_city2_options()
        else:
            # Hide second city dropdown and label
            self.city2_label.grid_remove()
            self.city2_dropdown.grid_remove()
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
        self.fetch_7day_button.configure(state="normal" if can_analyze else "disabled")
        
        # Enable clear button when we have chart data
        has_chart_data = hasattr(self, 'chart_data') and self.chart_data
        self.clear_charts_button.configure(state="normal" if has_chart_data else "disabled")
    
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
            
            # Open the historical analysis window with selectable charts and cities
            preselected = [city1_data['display_name']]
            if city2_data:
                preselected.append(city2_data['display_name'])
            HistoricalAnalysisWindow(
                parent=self.parent,
                db=self.db,
                cities_with_data=self.cities_with_data,
                preselected_cities=preselected
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing historical data: {e}")
            self._show_error_message("Failed to analyze historical data")
    
    def _show_placeholder(self):
        """Show initial placeholder message"""
        self._clear_chart_area()
        
        # Hide fallback notification when showing placeholder
        self._hide_fallback_notification()
        
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
    
    def _show_loading_indicator(self, message: str):
        """Show loading indicator with custom message"""
        self._clear_chart_area()
        
        # Hide fallback notification during loading
        if self.fallback_notification:
            self.fallback_notification.grid_remove()
        
        loading_label = tb.Label(
            self.chart_area,
            text=f"⏳ {message}",
            font=("Helvetica Neue", 14),
            bootstyle="info"
        )
        loading_label.pack(expand=True)
        
        # Force GUI update
        self.chart_area.update_idletasks()
    
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
        
        # Hide fallback notification on error
        self._hide_fallback_notification()
        
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
    
    def _show_fallback_notification(self):
        """Show fallback notification"""
        if self.fallback_notification:
            self.fallback_notification.grid()
    
    def _hide_fallback_notification(self):
        """Hide fallback notification"""
        if self.fallback_notification:
            self.fallback_notification.grid_remove()
    
    
    def _setup_chart_quadrants(self):
        """Setup the 4-quadrant chart layout"""
        # Clear chart area first
        for widget in self.chart_area.winfo_children():
            widget.destroy()
            
        # Configure grid for quadrants
        self.chart_area.rowconfigure(0, weight=1)
        self.chart_area.rowconfigure(1, weight=1)
        self.chart_area.columnconfigure(0, weight=1)
        self.chart_area.columnconfigure(1, weight=1)
        
        # Top-left: Temperature Line Chart
        self.temp_chart_frame = tb.LabelFrame(
            self.chart_area,
            text="🌡️ Daily High Temperatures",
            bootstyle="primary"
        )
        self.temp_chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 5))
        
        # Top-right: Precipitation Bar Chart
        self.precip_chart_frame = tb.LabelFrame(
            self.chart_area,
            text="🌧️ Daily Precipitation",
            bootstyle="info"
        )
        self.precip_chart_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 5))
        
        # Bottom-left: Humidity Area Chart
        self.humidity_chart_frame = tb.LabelFrame(
            self.chart_area,
            text="💧 Average Daily Humidity",
            bootstyle="success"
        )
        self.humidity_chart_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(5, 0))
        
        # Bottom-right: Weather Type Radar Chart
        self.weather_chart_frame = tb.LabelFrame(
            self.chart_area,
            text="☁️ Weather Type Frequency",
            bootstyle="warning"
        )
        self.weather_chart_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(5, 0))
        
        # Schedule chart creation after frames are properly sized
        self.chart_area.after(100, self._create_charts_when_ready)
        
    def _create_canvas_with_proper_sizing(self, fig, frame, chart_name="chart"):
        """Helper method to create canvas with proper initial sizing"""
        try:
            if not frame or not frame.winfo_exists():
                self.logger.error(f"{chart_name} frame does not exist")
                return None
                
            # Clear existing widgets in frame
            for widget in frame.winfo_children():
                widget.destroy()
            
            # Simple canvas creation - let tkinter handle the sizing
            canvas = FigureCanvasTkAgg(fig, frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=5, pady=5)
            
            return canvas
            
        except Exception as e:
            self.logger.error(f"Error creating canvas for {chart_name}: {e}")
            return None
            
    def _create_charts_when_ready(self):
        """Create charts after ensuring frame geometry is ready"""
        try:
            # Check if chart area still exists before proceeding
            if not hasattr(self, 'chart_area') or not self.chart_area.winfo_exists():
                return
                
            # Simple check - if we have chart data, create charts
            if not hasattr(self, 'chart_data') or not self.chart_data:
                self._show_chart_placeholders()
            else:
                self._update_charts()
                
        except Exception as e:
            self.logger.error(f"Error creating charts when ready: {e}")
            # Only show placeholders if chart area still exists
            if hasattr(self, 'chart_area') and self.chart_area.winfo_exists():
                self._show_chart_placeholders()
    
    def _show_chart_placeholders(self):
        """Show placeholder messages in chart quadrants"""
        charts = [
            (self.temp_chart_frame, "Line chart will show\ntemperature trends"),
            (self.precip_chart_frame, "Bar chart will show\nrainfall amounts"),
            (self.humidity_chart_frame, "Area chart will show\nhumidity patterns"),
            (self.weather_chart_frame, "Radar chart will show\nweather type distribution")
        ]
        
        for frame, text in charts:
            # Check if frame exists and is valid before creating widgets
            if frame and frame.winfo_exists():
                placeholder = tb.Label(
                    frame,
                    text=text,
                    font=("Helvetica Neue", 10),
                    justify=CENTER,
                    bootstyle="secondary"
                )
                placeholder.pack(expand=True)
    
    @log_execution_time()
    def _on_fetch_7day_clicked(self):
        """Handle 7-day data fetch button click with OpenWeatherMap History API"""
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
            
            # Show loading indicator
            self._show_loading_indicator("Fetching recent historical data...")
            
            # Disable button during fetch
            self.fetch_7day_button.configure(state="disabled")
            
            # Import and use OpenWeatherMap History client
            from core.weather.openweather_history_client import OpenWeatherHistoryClient
            
            client = OpenWeatherHistoryClient()
            
            # Fetch data for city1
            result1 = client.get_7day_history(
                city1_data['latitude'],
                city1_data['longitude'],
                city1_data['city'],
                city1_data['state']
            )
            
            # Handle the new fallback response format
            if isinstance(result1, tuple) and len(result1) == 2:
                # Check if this is the new fallback format (data, used_fallback)
                if isinstance(result1[1], bool):
                    # This is the fallback format: (original_result, used_fallback)
                    original_result, used_fallback1 = result1
                    if isinstance(original_result, tuple) and len(original_result) == 2:
                        df1, error1 = original_result
                    else:
                        df1, error1 = original_result, None
                else:
                    # Original format (data, error)
                    df1, error1 = result1
                    used_fallback1 = False
            else:
                df1, error1 = result1
                used_fallback1 = False
            
            if error1:
                self._show_error_message(f"Error fetching data for {city1_data['display_name']}: {error1}")
                return
            
            # Save city1 data only if not using fallback
            if df1 is not None and not df1.empty:
                if used_fallback1:
                    self.logger.info(f"Using fallback data for {city1_data['display_name']} - skipping database save")
                else:
                    records1, save_error1 = client.save_to_database(df1, self.db)
                    if save_error1:
                        self.logger.warning(f"Error saving data for {city1_data['display_name']}: {save_error1}")
                    else:
                        self.logger.info(f"Saved {records1} records for {city1_data['display_name']}")
            
            # Fetch data for city2 if in comparison mode
            if city2_data:
                result2 = client.get_7day_history(
                    city2_data['latitude'],
                    city2_data['longitude'],
                    city2_data['city'],
                    city2_data['state']
                )
                
                # Handle the new fallback response format
                if isinstance(result2, tuple) and len(result2) == 2:
                    # Check if this is the new fallback format (data, used_fallback)
                    if isinstance(result2[1], bool):
                        # This is the fallback format: (original_result, used_fallback)
                        original_result, used_fallback2 = result2
                        if isinstance(original_result, tuple) and len(original_result) == 2:
                            df2, error2 = original_result
                        else:
                            df2, error2 = original_result, None
                    else:
                        # Original format (data, error)
                        df2, error2 = result2
                        used_fallback2 = False
                else:
                    df2, error2 = result2
                    used_fallback2 = False
                
                if error2:
                    self._show_error_message(f"Error fetching data for {city2_data['display_name']}: {error2}")
                    return
                
                # Save city2 data only if not using fallback
                if df2 is not None and not df2.empty:
                    if used_fallback2:
                        self.logger.info(f"Using fallback data for {city2_data['display_name']} - skipping database save")
                    else:
                        records2, save_error2 = client.save_to_database(df2, self.db)
                        if save_error2:
                            self.logger.warning(f"Error saving data for {city2_data['display_name']}: {save_error2}")
                        else:
                            self.logger.info(f"Saved {records2} records for {city2_data['display_name']}")
            
            # Show fallback notification if any fallback data was used
            if used_fallback1 or (city2_data and used_fallback2):
                self._show_fallback_notification()
            else:
                self._hide_fallback_notification()
            
            # Refresh charts with new data
            self._fetch_chart_data(city1_data, city2_data, use_recent_data=True)
            
        except Exception as e:
            self.logger.error(f"Error fetching 7-day data: {e}")
            self._show_error_message("Failed to fetch 7-day data")
        finally:
            # Re-enable button
            self.fetch_7day_button.configure(state="normal")
    
    def _fetch_chart_data(self, city1_data: Dict, city2_data: Optional[Dict] = None, use_recent_data: bool = False):
        """Fetch chart data using the chart data service"""
        try:
            self.logger.debug(f"Fetching chart data for {city1_data.get('display_name')} and {city2_data.get('display_name') if city2_data else 'None'}, use_recent_data: {use_recent_data}")
            
            # Ensure chart quadrants are properly set up
            if not hasattr(self, 'temp_chart_frame') or not self.temp_chart_frame:
                self.logger.debug("Chart frames not initialized, setting up quadrants")
                self._setup_chart_quadrants()
            
            # Use the chart service to get processed data
            chart_data, error = self.chart_service.get_chart_data(
                city1_data, 
                city2_data, 
                days_back=7,
                use_recent_data=use_recent_data
            )
            
            if error:
                self.logger.error(f"Chart service returned error: {error}")
                self._show_chart_error(error)
                return
            
            if not chart_data or not chart_data.get('chart_ready'):
                self.logger.warning(f"Chart data not ready: {chart_data}")
                self._show_chart_error("No chart data available")
                return
            
            self.logger.debug(f"Chart data loaded successfully, chart_ready: {chart_data.get('chart_ready')}")
            
            # Store processed data
            self.chart_data = chart_data
            
            # Update charts with processed data
            self._update_chart_quadrants()
            
            # Update button states (enable clear button)
            self._update_analyze_button_state()
            
        except Exception as e:
            self.logger.error(f"Error fetching chart data: {e}", exc_info=True)
            self._show_chart_error("Failed to load chart data")
    
    def _on_clear_charts_clicked(self):
        """Handle clear charts button click"""
        try:
            # Clear stored chart data
            self.chart_data = {}
            
            # Reset selections if desired (optional)
            # self.city1_var.set("")
            # self.city2_var.set("")
            # self.compare_mode.set(False)
            # self.city2_frame.grid_forget()
            
            # Show placeholder
            self._show_placeholder()
            
            # Update button states
            self._update_analyze_button_state()
            
            self.logger.info("Charts cleared successfully")
            
        except Exception as e:
            self.logger.error(f"Error clearing charts: {e}")
            self._show_error_message("Failed to clear charts")
    
    
    
    def _update_chart_quadrants(self):
        """Update all four chart quadrants with 7-day data"""
        if not _import_matplotlib():
            self._show_matplotlib_unavailable()
            return
            
        if not self.chart_data or not self.chart_data.get('chart_ready'):
            return
        
        try:
            # Ensure chart frames exist and are properly initialized
            if not all([
                self.temp_chart_frame and self.temp_chart_frame.winfo_exists(),
                self.precip_chart_frame and self.precip_chart_frame.winfo_exists(),
                self.humidity_chart_frame and self.humidity_chart_frame.winfo_exists(),
                self.weather_chart_frame and self.weather_chart_frame.winfo_exists()
            ]):
                self.logger.warning("Chart frames not properly initialized, recreating...")
                self._setup_chart_quadrants()
            
            # Clear existing charts
            for frame in [self.temp_chart_frame, self.precip_chart_frame, 
                         self.humidity_chart_frame, self.weather_chart_frame]:
                if frame and frame.winfo_exists():
                    for widget in frame.winfo_children():
                        widget.destroy()
            
            # Create the charts
            self._create_temperature_chart()
            self._create_precipitation_chart()
            self._create_humidity_chart()
            self._create_weather_type_chart()
            
        except Exception as e:
            self.logger.error(f"Error updating chart quadrants: {e}", exc_info=True)
            self._show_chart_error(f"Chart creation failed: {str(e)}")
    
    def _get_responsive_figure_size(self, frame):
        """Calculate responsive figure size based on frame dimensions"""
        # Use a consistent, reasonable size that works well in quadrants
        return (4, 3)
    
    def _on_chart_area_resize(self, event=None):
        """Handle chart area resize events to update chart sizes"""
        # Only respond to resize events on the chart_area itself, not child widgets
        if event and event.widget != self.chart_area:
            return
            
        # Debounce resize events - only update after 500ms of no resize events
        if hasattr(self, '_resize_timer'):
            self.chart_area.after_cancel(self._resize_timer)
        
        self._resize_timer = self.chart_area.after(500, self._refresh_charts_after_resize)
    
    def _refresh_charts_after_resize(self):
        """Refresh charts with new responsive sizes after window resize"""
        if hasattr(self, 'chart_data') and self.chart_data and self.chart_data.get('chart_ready'):
            try:
                self._update_chart_quadrants()
            except Exception as e:
                self.logger.error(f"Error refreshing charts after resize: {e}")
    
    def _create_temperature_chart(self):
        """Create line chart for daily temperatures"""
        if not _import_matplotlib():
            self._show_chart_error("Matplotlib not available")
            return
            
        try:
            # Get responsive figure size
            figsize = self._get_responsive_figure_size(self.temp_chart_frame)
            fig = Figure(figsize=figsize, dpi=80)
            ax = fig.add_subplot(111)
        except Exception as e:
            self.logger.error(f"Error creating temperature chart: {e}")
            self._show_chart_error("Temperature chart creation failed")
            return
        
        # Get processed data for city1
        city1_temp = self.chart_data['city1']['processed'].get('temperature', {})
        dates = city1_temp.get('dates', [])
        temps1 = city1_temp.get('max_temps', [])
        
        if dates and temps1:
            ax.plot(dates, temps1, marker='o', linewidth=2, 
                   label=self.chart_data['city1']['info']['display_name'], color='#FF6B6B')
        
        # Add city2 if comparison mode
        if self.chart_data.get('city2'):
            city2_temp = self.chart_data['city2']['processed'].get('temperature', {})
            temps2 = city2_temp.get('max_temps', [])
            if temps2:
                ax.plot(dates, temps2, marker='s', linewidth=2, 
                       label=self.chart_data['city2']['info']['display_name'], color='#4ECDC4')
                ax.legend(fontsize=8)
        
        ax.set_title('Daily High Temperatures', fontsize=10, pad=10)
        ax.set_ylabel('Temperature (°F)', fontsize=8)
        ax.tick_params(axis='x', rotation=45, labelsize=7)
        ax.tick_params(axis='y', labelsize=7)
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        # Use helper method for proper canvas creation
        canvas = self._create_canvas_with_proper_sizing(fig, self.temp_chart_frame, "Temperature")
        if not canvas:
            self._show_chart_error("Temperature chart display failed")
    
    def _create_precipitation_chart(self):
        """Create bar chart for daily precipitation"""
        if not _import_matplotlib():
            self._show_chart_error("Matplotlib not available")
            return
            
        try:
            # Get responsive figure size
            figsize = self._get_responsive_figure_size(self.precip_chart_frame)
            fig = Figure(figsize=figsize, dpi=80)
            ax = fig.add_subplot(111)
        except Exception as e:
            self.logger.error(f"Error creating precipitation chart: {e}")
            self._show_chart_error("Precipitation chart creation failed")
            return
        
        # Get processed precipitation data
        city1_precip = self.chart_data['city1']['processed'].get('precipitation', {})
        dates = city1_precip.get('dates', [])
        precip1 = city1_precip.get('precipitation', [])
        
        x = np.arange(len(dates))
        width = 0.35
        
        if dates and precip1:
            ax.bar(x - width/2, precip1, width, 
                  label=self.chart_data['city1']['info']['display_name'], 
                  color='#FF6B6B', alpha=0.8)
        
        if self.chart_data.get('city2'):
            city2_precip = self.chart_data['city2']['processed'].get('precipitation', {})
            precip2 = city2_precip.get('precipitation', [])
            if precip2:
                ax.bar(x + width/2, precip2, width, 
                      label=self.chart_data['city2']['info']['display_name'], 
                      color='#4ECDC4', alpha=0.8)
                ax.legend(fontsize=8)
        
        ax.set_title('Daily Precipitation', fontsize=10, pad=10)
        ax.set_ylabel('Precipitation (mm)', fontsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, fontsize=7)
        ax.tick_params(axis='y', labelsize=7)
        ax.grid(True, alpha=0.3, axis='y')
        
        fig.tight_layout()
        
        # Use helper method for proper canvas creation
        canvas = self._create_canvas_with_proper_sizing(fig, self.precip_chart_frame, "Precipitation")
        if not canvas:
            self._show_chart_error("Precipitation chart display failed")
    
    def _create_humidity_chart(self):
        """Create area chart for average daily humidity"""
        if not _import_matplotlib():
            self._show_chart_error("Matplotlib not available")
            return
            
        try:
            # Get responsive figure size
            figsize = self._get_responsive_figure_size(self.humidity_chart_frame)
            fig = Figure(figsize=figsize, dpi=80)
            ax = fig.add_subplot(111)
        except Exception as e:
            self.logger.error(f"Error creating humidity chart: {e}")
            self._show_chart_error("Humidity chart creation failed")
            return
        
        # Get processed humidity data
        city1_humid = self.chart_data['city1']['processed'].get('humidity', {})
        dates = city1_humid.get('dates', [])
        humidity1 = city1_humid.get('humidity', [])
        
        if dates and humidity1:
            # Use line plot with area fill for city1 (red/pink)
            ax.plot(range(len(dates)), humidity1, color='#FF6B6B', linewidth=2, marker='o', 
                   label=self.chart_data['city1']['info']['display_name'])
            ax.fill_between(range(len(dates)), humidity1, alpha=0.2, color='#FF6B6B')
        
        if self.chart_data.get('city2'):
            city2_humid = self.chart_data['city2']['processed'].get('humidity', {})
            humidity2 = city2_humid.get('humidity', [])
            if humidity2:
                # Use line plot with area fill for city2 (blue/teal)
                ax.plot(range(len(dates)), humidity2, color='#4ECDC4', linewidth=2, marker='s',
                       label=self.chart_data['city2']['info']['display_name'])
                ax.fill_between(range(len(dates)), humidity2, alpha=0.15, color='#4ECDC4')
                ax.legend(fontsize=8)
        
        ax.set_title('Average Daily Humidity', fontsize=10, pad=10)
        ax.set_ylabel('Humidity (%)', fontsize=8)
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels(dates, rotation=45, fontsize=7)
        ax.tick_params(axis='y', labelsize=7)
        ax.grid(True, alpha=0.3)
        
        fig.tight_layout()
        
        # Use helper method for proper canvas creation
        canvas = self._create_canvas_with_proper_sizing(fig, self.humidity_chart_frame, "Humidity")
        if not canvas:
            self._show_chart_error("Humidity chart display failed")
    
    def _create_weather_type_chart(self):
        """Create radar chart for weather type frequency"""
        if not _import_matplotlib():
            self._show_chart_error("Matplotlib not available")
            return
            
        try:
            # Get responsive figure size
            figsize = self._get_responsive_figure_size(self.weather_chart_frame)
            fig = Figure(figsize=figsize, dpi=80)
            ax = fig.add_subplot(111, projection='polar')
        except Exception as e:
            self.logger.error(f"Error creating polar plot: {e}")
            # Fallback to regular bar chart
            self._create_weather_type_bar_chart()
            return
        
        # Define weather categories
        categories = ['Clear', 'Cloudy', 'Rainy', 'Stormy', 'Snowy', 'Foggy']
        
        def categorize_weather(description):
            desc = description.lower()
            if any(word in desc for word in ['clear', 'sunny']):
                return 'Clear'
            elif any(word in desc for word in ['cloud', 'overcast']):
                return 'Cloudy'
            elif any(word in desc for word in ['rain', 'drizzle', 'shower']):
                return 'Rainy'
            elif any(word in desc for word in ['storm', 'thunder']):
                return 'Stormy'
            elif any(word in desc for word in ['snow', 'blizzard']):
                return 'Snowy'
            elif any(word in desc for word in ['fog', 'mist']):
                return 'Foggy'
            return 'Clear'
        
        # Get processed weather data for city1
        city1_weather = self.chart_data['city1']['processed'].get('weather_types', {})
        city1_values = [city1_weather.get('percentages', {}).get(cat, 0) for cat in categories]
        
        # Create angles for radar chart
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        city1_values += city1_values[:1]  # Complete the circle
        angles += angles[:1]
        
        if city1_values and any(v > 0 for v in city1_values):
            ax.plot(angles, city1_values, 'o-', linewidth=2, 
                   label=self.chart_data['city1']['info']['display_name'], color='#FF6B6B')
            ax.fill(angles, city1_values, alpha=0.25, color='#FF6B6B')
        
        if self.chart_data.get('city2'):
            city2_weather = self.chart_data['city2']['processed'].get('weather_types', {})
            city2_values = [city2_weather.get('percentages', {}).get(cat, 0) for cat in categories]
            
            if city2_values and any(v > 0 for v in city2_values):
                city2_values += city2_values[:1]
                ax.plot(angles, city2_values, 's-', linewidth=2, 
                       label=self.chart_data['city2']['info']['display_name'], color='#4ECDC4')
                ax.fill(angles, city2_values, alpha=0.15, color='#4ECDC4')
                ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8)
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=7)
        ax.set_ylim(0, 100)
        ax.set_title('Weather Type Frequency (%)', fontsize=10, pad=20)
        ax.grid(True)
        
        fig.tight_layout()
        
        # Use helper method for proper canvas creation
        canvas = self._create_canvas_with_proper_sizing(fig, self.weather_chart_frame, "Weather Type")
        if not canvas:
            self._show_chart_error("Weather chart display failed")
    
    def _create_weather_type_bar_chart(self):
        """Fallback bar chart for weather types when polar projection fails"""
        try:
            # Get responsive figure size
            figsize = self._get_responsive_figure_size(self.weather_chart_frame)
            fig = Figure(figsize=figsize, dpi=80)
            ax = fig.add_subplot(111)
            
            # Define weather categories
            categories = ['Clear', 'Cloudy', 'Rainy', 'Stormy', 'Snowy', 'Foggy']
            
            def categorize_weather(cloud_cover, precipitation, rain):
                """Categorize weather based on database values"""
                cloud_cover = cloud_cover or 0
                precipitation = precipitation or 0
                rain = rain or 0
                
                if precipitation > 5 or rain > 5:
                    return 'Rainy'
                elif cloud_cover > 80:
                    return 'Cloudy'
                elif cloud_cover < 20:
                    return 'Clear'
                else:
                    return 'Cloudy'
            
            # Get processed weather data for city1
            city1_weather = self.chart_data['city1']['processed'].get('weather_types', {})
            city1_values = [city1_weather.get('percentages', {}).get(cat, 0) for cat in categories]
            
            x = np.arange(len(categories))
            width = 0.35
            
            if city1_values and any(v > 0 for v in city1_values):
                ax.bar(x - width/2, city1_values, width, 
                      label=self.chart_data['city1']['info']['display_name'], 
                      color='#FF6B6B', alpha=0.8)
            
            if self.chart_data.get('city2'):
                city2_weather = self.chart_data['city2']['processed'].get('weather_types', {})
                city2_values = [city2_weather.get('percentages', {}).get(cat, 0) for cat in categories]
                
                if city2_values and any(v > 0 for v in city2_values):
                    ax.bar(x + width/2, city2_values, width, 
                          label=self.chart_data['city2']['info']['display_name'], 
                          color='#4ECDC4', alpha=0.8)
                    ax.legend(fontsize=8)
            
            ax.set_title('Weather Type Frequency (%)', fontsize=10, pad=10)
            ax.set_ylabel('Frequency (%)', fontsize=8)
            ax.set_xticks(x)
            ax.set_xticklabels(categories, rotation=45, fontsize=7)
            ax.tick_params(axis='y', labelsize=7)
            ax.grid(True, alpha=0.3, axis='y')
            
            fig.tight_layout()
            
            # Use helper method for proper canvas creation
            canvas = self._create_canvas_with_proper_sizing(fig, self.weather_chart_frame, "Weather Bar")
            if not canvas:
                self._show_chart_error("Weather chart creation failed")
            
        except Exception as e:
            self.logger.error(f"Error creating fallback weather chart: {e}")
            self._show_chart_error("Weather chart creation failed")
    
    def _show_matplotlib_unavailable(self):
        """Show message when matplotlib is not available"""
        for frame in [self.temp_chart_frame, self.precip_chart_frame, 
                     self.humidity_chart_frame, self.weather_chart_frame]:
            for widget in frame.winfo_children():
                widget.destroy()
            
            error_label = tb.Label(
                frame,
                text="📊 Charts require matplotlib\\nPlease install: pip install matplotlib",
                font=("Helvetica Neue", 10),
                justify=CENTER,
                bootstyle="warning"
            )
            error_label.pack(expand=True)
    
    def _show_chart_error(self, message: str):
        """Show error message in a chart frame"""
        try:
            # Clear chart area first
            if hasattr(self, 'chart_area') and self.chart_area:
                for widget in self.chart_area.winfo_children():
                    widget.destroy()
                
                error_label = tb.Label(
                    self.chart_area,
                    text=f"⚠️ {message}",
                    font=("Helvetica Neue", 10),
                    justify=CENTER,
                    bootstyle="danger"
                )
                error_label.pack(expand=True)
            else:
                self.logger.error(f"Chart area not available for error message: {message}")
        except Exception as e:
            self.logger.error(f"Error displaying chart error message: {e}")
    
    def refresh_cities(self):
        """Refresh the list of cities with historical data"""
        self._load_cities_with_data()
        
        # Reset selections
        self.city1_var.set("")
        self.city2_var.set("")
        self.compare_mode.set(False)
        
        # Hide city2 components (they use grid_remove, not grid_forget)
        if hasattr(self, 'city2_dropdown') and self.city2_dropdown:
            self.city2_dropdown.grid_remove()
        if hasattr(self, 'city2_label') and self.city2_label:
            self.city2_label.grid_remove()
        
        # Update UI
        self._update_analyze_button_state()
        if self.cities_with_data:
            self._show_placeholder()
        else:
            self._show_no_data_message()