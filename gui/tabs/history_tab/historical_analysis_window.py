"""
Historical Analysis Window for Interactive Bulk Data Analysis
Provides advanced interactive charts for long-term weather pattern analysis
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Import matplotlib components for interactive charts
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    import seaborn as sns
    
    # For interactive features
    try:
        import mplcursors
        MPLCURSORS_AVAILABLE = True
    except ImportError:
        MPLCURSORS_AVAILABLE = False
        
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

logger = logging.getLogger(__name__)

class HistoricalAnalysisWindow:
    """Interactive window for bulk historical weather data analysis"""
    
    def __init__(self, parent, db_path, available_cities):
        self.parent = parent
        self.db_path = db_path
        self.available_cities = available_cities
        
        # Create the analysis window
        self.window = tb.Toplevel(parent)
        self.window.title("📊 Historical Weather Analysis")
        self.window.geometry("1200x800")
        self.window.minsize(1000, 600)
        
        # Chart types available
        self.chart_types = {
            "Temperature Trends": self._create_temperature_trends,
            "Extreme Weather Events": self._create_extreme_events,
            "Seasonal Patterns": self._create_seasonal_patterns,
            "City Climate Comparison": self._create_climate_comparison,
            "Weather Anomalies": self._create_anomaly_detection
        }
        
        # UI Variables
        self.selected_cities = {}  # city_name: BooleanVar
        self.chart_type_var = tb.StringVar(value="Temperature Trends")
        
        # Chart components
        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.current_chart = None
        
        self._setup_ui()
        self._load_available_cities()
        
    def _setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = tb.Frame(self.window)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for controls
        control_panel = tb.Frame(main_frame, width=300)
        control_panel.pack(side=LEFT, fill=Y, padx=(0, 10))
        control_panel.pack_propagate(False)
        
        # Right panel for charts
        chart_panel = tb.Frame(main_frame)
        chart_panel.pack(side=RIGHT, fill=BOTH, expand=True)
        
        self._setup_control_panel(control_panel)
        self._setup_chart_panel(chart_panel)
        
    def _setup_control_panel(self, parent):
        """Setup the control panel with city selection and chart options"""
        # Title
        title_label = tb.Label(
            parent, 
            text="Analysis Controls",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Chart type selection
        chart_frame = tb.LabelFrame(parent, text="Chart Type", padding=10)
        chart_frame.pack(fill=X, pady=(0, 15))
        
        self.chart_combo = tb.Combobox(
            chart_frame,
            textvariable=self.chart_type_var,
            values=list(self.chart_types.keys()),
            state="readonly",
            width=25
        )
        self.chart_combo.pack(fill=X)
        
        # City selection
        cities_frame = tb.LabelFrame(parent, text="Select Cities for Analysis", padding=10)
        cities_frame.pack(fill=BOTH, expand=True, pady=(0, 15))
        
        # Scrollable frame for cities
        self.cities_canvas = tk.Canvas(cities_frame, highlightthickness=0)
        cities_scrollbar = tb.Scrollbar(cities_frame, orient=VERTICAL, command=self.cities_canvas.yview)
        self.cities_scroll_frame = tb.Frame(self.cities_canvas)
        
        self.cities_scroll_frame.bind(
            "<Configure>",
            lambda e: self.cities_canvas.configure(scrollregion=self.cities_canvas.bbox("all"))
        )
        
        self.cities_canvas.create_window((0, 0), window=self.cities_scroll_frame, anchor="nw")
        self.cities_canvas.configure(yscrollcommand=cities_scrollbar.set)
        
        self.cities_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        cities_scrollbar.pack(side=RIGHT, fill=Y)
        
        # Control buttons
        button_frame = tb.Frame(parent)
        button_frame.pack(fill=X, pady=(0, 10))
        
        select_all_btn = tb.Button(
            button_frame,
            text="Select All",
            command=self._select_all_cities,
            bootstyle="info-outline",
            width=12
        )
        select_all_btn.pack(side=LEFT, padx=(0, 5))
        
        clear_all_btn = tb.Button(
            button_frame,
            text="Clear All", 
            command=self._clear_all_cities,
            bootstyle="secondary-outline",
            width=12
        )
        clear_all_btn.pack(side=RIGHT, padx=(5, 0))
        
        # Generate chart button
        self.generate_btn = tb.Button(
            parent,
            text="📊 Generate Chart",
            command=self._generate_chart,
            bootstyle="primary",
            width=25
        )
        self.generate_btn.pack(pady=10)
        
        # Status label
        self.status_label = tb.Label(
            parent,
            text="Please select at least one city for analysis",
            font=("Helvetica", 9),
            bootstyle="secondary"
        )
        self.status_label.pack(pady=(5, 0))
        
    def _setup_chart_panel(self, parent):
        """Setup the chart display panel"""
        # Chart title
        self.chart_title = tb.Label(
            parent,
            text="Interactive Historical Weather Analysis",
            font=("Helvetica", 16, "bold")
        )
        self.chart_title.pack(pady=(0, 10))
        
        # Chart container
        self.chart_container = tb.Frame(parent)
        self.chart_container.pack(fill=BOTH, expand=True)
        
        # Initial placeholder
        self._show_placeholder()
        
    def _load_available_cities(self):
        """Load available cities with historical data"""
        for city_info in self.available_cities:
            city_name = city_info['display_name']
            var = tb.BooleanVar()
            self.selected_cities[city_name] = var
            
            # Create checkbox for each city
            cb = tb.Checkbutton(
                self.cities_scroll_frame,
                text=city_name,
                variable=var,
                command=self._update_status
            )
            cb.pack(anchor=W, pady=2, padx=5)
            
    def _select_all_cities(self):
        """Select all available cities"""
        for var in self.selected_cities.values():
            var.set(True)
        self._update_status()
        
    def _clear_all_cities(self):
        """Clear all city selections"""
        for var in self.selected_cities.values():
            var.set(False)
        self._update_status()
        
    def _update_status(self):
        """Update the status label based on selections"""
        selected_count = sum(1 for var in self.selected_cities.values() if var.get())
        
        if selected_count == 0:
            self.status_label.config(text="Please select at least one city for analysis")
            self.generate_btn.config(state="disabled")
        elif selected_count == 1:
            self.status_label.config(text=f"1 city selected - Ready for analysis")
            self.generate_btn.config(state="normal")
        else:
            self.status_label.config(text=f"{selected_count} cities selected - Ready for comparison")
            self.generate_btn.config(state="normal")
            
    def _show_placeholder(self):
        """Show placeholder message when no chart is displayed"""
        placeholder = tb.Label(
            self.chart_container,
            text="📊 Select cities and chart type, then click 'Generate Chart'\n\n" +
                 "Interactive Features:\n" +
                 "• Hover over data points for details\n" +
                 "• Click legend items to toggle series\n" +
                 "• Use toolbar to zoom and pan\n" +
                 "• Double-click to reset view",
            font=("Helvetica", 12),
            justify=CENTER,
            bootstyle="secondary"
        )
        placeholder.pack(expand=True)
        
    def _generate_chart(self):
        """Generate the selected chart type with selected cities"""
        if not MATPLOTLIB_AVAILABLE:
            tb.messagebox.showerror("Error", "Matplotlib is required for charts")
            return
            
        selected_city_names = [name for name, var in self.selected_cities.items() if var.get()]
        
        if not selected_city_names:
            tb.messagebox.showwarning("Warning", "Please select at least one city")
            return
            
        # Clear existing chart
        for widget in self.chart_container.winfo_children():
            widget.destroy()
            
        # Show loading message
        loading_label = tb.Label(self.chart_container, text="Generating chart...", font=("Helvetica", 12))
        loading_label.pack(expand=True)
        self.window.update()
        
        try:
            # Create chart based on selected type
            chart_type = self.chart_type_var.get()
            chart_function = self.chart_types[chart_type]
            
            # Create matplotlib figure
            self.figure = Figure(figsize=(12, 8), dpi=100)
            
            # Generate the specific chart
            chart_function(selected_city_names)
            
            # Remove loading message
            loading_label.destroy()
            
            # Create canvas and toolbar
            self.canvas = FigureCanvasTkAgg(self.figure, self.chart_container)
            self.canvas.draw()
            
            # Toolbar for zoom/pan
            toolbar_frame = tb.Frame(self.chart_container)
            toolbar_frame.pack(side=TOP, fill=X)
            self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
            self.toolbar.update()
            
            # Canvas
            self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
            
            # Add interactivity if mplcursors is available
            if MPLCURSORS_AVAILABLE:
                self._add_interactivity()
                
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            loading_label.config(text=f"Error generating chart: {str(e)}")
            
    def _create_temperature_trends(self, city_names):
        """Create temperature trend analysis chart"""
        ax = self.figure.add_subplot(111)
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(city_names)))
        
        for i, city_name in enumerate(city_names):
            # Get temperature data for city
            city_data = self._get_city_data(city_name)
            if city_data.empty:
                continue
                
            # Monthly temperature trends
            monthly_data = city_data.groupby(city_data['date'].dt.to_period('M')).agg({
                'temperature_mean': 'mean',
                'temperature_max': 'mean',
                'temperature_min': 'mean'
            }).reset_index()
            monthly_data['date'] = monthly_data['date'].dt.to_timestamp()
            
            # Plot temperature trend
            ax.plot(monthly_data['date'], monthly_data['temperature_mean'], 
                   label=f'{city_name} (Avg)', color=colors[i], linewidth=2)
            ax.fill_between(monthly_data['date'], 
                           monthly_data['temperature_min'], 
                           monthly_data['temperature_max'],
                           alpha=0.2, color=colors[i])
                           
        ax.set_title('Temperature Trends Over Time', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Temperature (°F)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        self.figure.autofmt_xdate()
        
    def _create_extreme_events(self, city_names):
        """Create extreme weather events analysis"""
        ax = self.figure.add_subplot(111)
        
        # Define extreme thresholds
        thresholds = {
            'Hot Days (>100°F)': ('temperature_max', '>', 100),
            'Cold Days (<32°F)': ('temperature_min', '<', 32),
            'Heavy Rain (>1")': ('precipitation', '>', 1),
            'High Wind (>30mph)': ('wind_speed_max', '>', 30)
        }
        
        width = 0.8 / len(city_names)
        x_positions = np.arange(len(thresholds))
        
        for i, city_name in enumerate(city_names):
            city_data = self._get_city_data(city_name)
            if city_data.empty:
                continue
                
            counts = []
            for event_name, (column, operator, threshold) in thresholds.items():
                if column in city_data.columns:
                    if operator == '>':
                        count = (city_data[column] > threshold).sum()
                    else:
                        count = (city_data[column] < threshold).sum()
                    counts.append(count)
                else:
                    counts.append(0)
                    
            ax.bar(x_positions + i * width, counts, width, 
                  label=city_name, alpha=0.8)
                  
        ax.set_title('Extreme Weather Events (2010-Present)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Event Type')
        ax.set_ylabel('Number of Days')
        ax.set_xticks(x_positions + width * (len(city_names) - 1) / 2)
        ax.set_xticklabels(list(thresholds.keys()), rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
    def _create_seasonal_patterns(self, city_names):
        """Create seasonal pattern analysis"""
        fig = self.figure
        
        # Create subplots for each season
        seasons = ['Winter', 'Spring', 'Summer', 'Fall']
        season_months = {
            'Winter': [12, 1, 2],
            'Spring': [3, 4, 5], 
            'Summer': [6, 7, 8],
            'Fall': [9, 10, 11]
        }
        
        for i, season in enumerate(seasons):
            ax = fig.add_subplot(2, 2, i+1)
            
            for city_name in city_names:
                city_data = self._get_city_data(city_name)
                if city_data.empty:
                    continue
                    
                # Filter for season
                season_data = city_data[city_data['date'].dt.month.isin(season_months[season])]
                
                # Group by year
                yearly_avg = season_data.groupby(season_data['date'].dt.year)['temperature_mean'].mean()
                
                ax.plot(yearly_avg.index, yearly_avg.values, 
                       marker='o', label=city_name, linewidth=2)
                       
            ax.set_title(f'{season} Temperature Trends')
            ax.set_xlabel('Year')
            ax.set_ylabel('Avg Temperature (°F)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
        fig.suptitle('Seasonal Temperature Patterns', fontsize=16, fontweight='bold')
        fig.tight_layout()
        
    def _create_climate_comparison(self, city_names):
        """Create climate comparison radar chart"""
        if len(city_names) < 2:
            # Fallback to simple comparison chart
            ax = self.figure.add_subplot(111)
            
            metrics = ['Avg Temp', 'Max Temp', 'Min Temp', 'Precipitation', 'Humidity']
            city_metrics = []
            
            for city_name in city_names:
                city_data = self._get_city_data(city_name)
                if city_data.empty:
                    continue
                    
                city_stats = [
                    city_data['temperature_mean'].mean(),
                    city_data['temperature_max'].mean(), 
                    city_data['temperature_min'].mean(),
                    city_data['precipitation'].mean(),
                    city_data['humidity'].mean() if 'humidity' in city_data.columns else 0
                ]
                city_metrics.append((city_name, city_stats))
                
            x = np.arange(len(metrics))
            width = 0.8 / len(city_metrics)
            
            for i, (city_name, stats) in enumerate(city_metrics):
                ax.bar(x + i * width, stats, width, label=city_name, alpha=0.8)
                
            ax.set_title('Climate Comparison', fontsize=16, fontweight='bold')
            ax.set_xlabel('Climate Metrics')
            ax.set_xticks(x + width * (len(city_metrics) - 1) / 2)
            ax.set_xticklabels(metrics)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
        else:
            # Create radar chart for multiple cities
            self._create_radar_chart(city_names)
            
    def _create_radar_chart(self, city_names):
        """Create a radar chart for climate comparison"""
        ax = self.figure.add_subplot(111, projection='polar')
        
        metrics = ['Avg Temp', 'Precipitation', 'Humidity', 'Wind Speed', 'Pressure']
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(city_names)))
        
        for i, city_name in enumerate(city_names):
            city_data = self._get_city_data(city_name)
            if city_data.empty:
                continue
                
            # Normalize values for radar chart
            values = [
                (city_data['temperature_mean'].mean() - 32) / 100,  # Normalize temp
                city_data['precipitation'].mean() / 5,  # Normalize precip
                city_data['humidity'].mean() / 100 if 'humidity' in city_data.columns else 0.5,
                city_data['wind_speed_max'].mean() / 50 if 'wind_speed_max' in city_data.columns else 0.3,
                0.5  # Placeholder for pressure
            ]
            values += values[:1]  # Complete the circle
            
            ax.plot(angles, values, 'o-', linewidth=2, label=city_name, color=colors[i])
            ax.fill(angles, values, alpha=0.25, color=colors[i])
            
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 1)
        ax.set_title('Climate Comparison (Normalized)', fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
    def _create_anomaly_detection(self, city_names):
        """Create weather anomaly detection chart"""
        ax = self.figure.add_subplot(111)
        
        for city_name in city_names:
            city_data = self._get_city_data(city_name)
            if city_data.empty:
                continue
                
            # Calculate rolling mean and std for anomaly detection
            city_data['temp_rolling_mean'] = city_data['temperature_mean'].rolling(window=30).mean()
            city_data['temp_rolling_std'] = city_data['temperature_mean'].rolling(window=30).std()
            
            # Identify anomalies (beyond 2 standard deviations)
            city_data['anomaly'] = (
                np.abs(city_data['temperature_mean'] - city_data['temp_rolling_mean']) > 
                2 * city_data['temp_rolling_std']
            )
            
            # Plot temperature data
            ax.plot(city_data['date'], city_data['temperature_mean'], 
                   label=f'{city_name}', alpha=0.7, linewidth=1)
                   
            # Highlight anomalies
            anomalies = city_data[city_data['anomaly']]
            if not anomalies.empty:
                ax.scatter(anomalies['date'], anomalies['temperature_mean'], 
                          color='red', s=50, alpha=0.8, zorder=5)
                          
        ax.set_title('Weather Anomaly Detection', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Temperature (°F)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        self.figure.autofmt_xdate()
        
    def _get_city_data(self, city_display_name):
        """Get historical data for a specific city"""
        try:
            # Find city info
            city_info = next((city for city in self.available_cities 
                            if city['display_name'] == city_display_name), None)
            
            if not city_info:
                return pd.DataFrame()
                
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT date, temperature_mean, temperature_max, temperature_min,
                   precipitation, rain, wind_speed_max, humidity
            FROM historical_weather
            WHERE city = ? AND state = ?
            AND date BETWEEN '2010-01-01' AND ?
            ORDER BY date
            """
            
            current_date = datetime.now().strftime('%Y-%m-%d')
            df = pd.read_sql_query(
                query, 
                conn, 
                params=(city_info['city'], city_info['state'], current_date),
                parse_dates=['date']
            )
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting city data for {city_display_name}: {e}")
            return pd.DataFrame()
            
    def _add_interactivity(self):
        """Add interactive features to the chart"""
        if not MPLCURSORS_AVAILABLE:
            return
            
        try:
            # Add hover tooltips
            cursor = mplcursors.cursor(hover=True)
            cursor.connect("add", lambda sel: sel.annotation.set_text(
                f"Value: {sel.target[1]:.2f}\nDate: {sel.target[0]}"
            ))
            
            # Make legend interactive (click to toggle)
            self._make_legend_interactive()
            
        except Exception as e:
            logger.warning(f"Could not add interactivity: {e}")
            
    def _make_legend_interactive(self):
        """Make legend items clickable to toggle series visibility"""
        if not hasattr(self.figure, 'axes') or not self.figure.axes:
            return
            
        ax = self.figure.axes[0]
        if not hasattr(ax, 'get_legend') or not ax.get_legend():
            return
            
        legend = ax.get_legend()
        if not legend:
            return
            
        # Store original alpha values
        self.original_alphas = {}
        for line in ax.lines:
            self.original_alphas[line] = line.get_alpha() or 1.0
            
        def on_legend_click(event):
            if event.inaxes != legend.axes:
                return
                
            for i, legend_line in enumerate(legend.get_lines()):
                if legend_line.contains(event)[0]:
                    # Toggle visibility
                    orig_line = ax.lines[i]
                    if orig_line.get_alpha() == 0.1:  # Currently hidden
                        orig_line.set_alpha(self.original_alphas[orig_line])
                        legend_line.set_alpha(1.0)
                    else:  # Currently visible
                        orig_line.set_alpha(0.1)
                        legend_line.set_alpha(0.3)
                    break
                    
            self.canvas.draw()
            
        self.figure.canvas.mpl_connect('button_press_event', on_legend_click)