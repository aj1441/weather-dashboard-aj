"""Saved cities component for managing favorite locations"""

import logging
import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledFrame
from core.database.data_handler import WeatherDataHandler
from core.weather.weather_predictor import WeatherPredictor
from utils.data.state_utils import normalize_state_abbreviation

class SavedCitiesComponent:
    """Handles displaying and managing saved cities using ttkbootstrap widgets."""

    def __init__(self, parent, data_directory=None):
        self.parent = parent
        self.logger = logging.getLogger(__name__)
        self.weather_callback = None
        
        # Use the same data directory as the main app if provided
        self.data_handler = WeatherDataHandler(data_directory=data_directory or "data")
        self.weather_predictor = WeatherPredictor()
        self.forecast_items = {}  # Store forecast widgets by city

    def setup_component(self):
        """Create the saved cities section."""
        self.cities_frame = tb.Frame(self.parent)

        # Title
        title_label = tb.Label(
            self.cities_frame,
            text="💾 Saved Cities",
            font=("Helvetica Neue", 20, "bold")
        )
        title_label.pack(pady=10)

        # Create scrollable frame for cities list
        self.scrollable_frame = ScrolledFrame(self.cities_frame, autohide=True)
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # The actual frame where cities will be added
        self.cities_list_frame = self.scrollable_frame

        # No cities message (initially shown)
        self.no_cities_label = tb.Label(
            self.cities_list_frame,
            text="No saved cities yet.\nGet weather for a city and click '💾 Save City' to add it here!",
            font=("Helvetica Neue", 14),
            justify="center"
        )
        self.no_cities_label.pack(pady=40)


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
            self.no_cities_label = tb.Label(
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
        # Create main container for city and predictions
        container = tb.Frame(self.cities_list_frame)
        container.pack(fill="x", padx=10, pady=5)
        
        # Create card frame for city info and buttons
        card = tb.Frame(container)
        card.pack(fill="x")

        # City info
        city_name = f"{city_data.get('city')}"
        if city_data.get('state'):
            city_name += f", {city_data.get('state')}"
        if city_data.get('country') and city_data.get('country') != 'US':
            city_name += f", {city_data.get('country')}"

        city_label = tb.Label(
            card,
            text=city_name,
            font=("Helvetica Neue", 14, "bold")
        )
        city_label.pack(side="left", padx=10, pady=5)

        # Predicted Weather button
        def show_predictions():
            # Toggle prediction display
            if prediction_frame.winfo_viewable():
                # Hide predictions
                prediction_frame.pack_forget()
                weather_btn.configure(text="🔮 Predicted Weather")
            else:
                # Show predictions
                prediction_frame.pack(fill="x", padx=20, pady=(10, 0))
                weather_btn.configure(text="🔮 Hide Predictions")
                
                # Clear existing predictions
                for widget in prediction_frame.winfo_children():
                    widget.destroy()
                
                # Generate ML predictions
                self._generate_ml_predictions(prediction_frame, city_data)

        weather_btn = tb.Button(
            card,
            text="🔮 Predicted Weather",
            command=show_predictions,
            width=15,
            bootstyle="secondary-outline"
        )
        weather_btn.pack(side="right", padx=10, pady=5)

        # Get History Button (Hybrid Approach)
        def get_history():
            from core.weather.hybrid_data_coordinator import HybridWeatherDataCoordinator
            
            try:
                coordinator = HybridWeatherDataCoordinator()
                state = normalize_state_abbreviation(city_data.get('state', ''))
                
                # Get latitude and longitude from city data
                lat = float(city_data.get('latitude', 0))
                lon = float(city_data.get('longitude', 0))
                
                if lat == 0 or lon == 0:
                    tb.dialogs.Messagebox.show_error(
                        title="Location Error",
                        message="Missing location coordinates for historical data"
                    )
                    return
                
                # Show loading message
                self.logger.info(f"Fetching HYBRID historical data for {city_data.get('city')}")
                loading_label = tb.Label(
                    card,
                    text="Loading hybrid data (bulk + recent)...",
                    font=("Helvetica Neue", 10, "italic")
                )
                loading_label.pack(side="right", padx=5)
                card.update()
                
                # Fetch and store HYBRID historical data (both Open-Meteo + OpenWeather)
                success, error = coordinator.fetch_combined_historical_data(
                    city=city_data.get('city'),
                    state=state,
                    latitude=lat,
                    longitude=lon
                )
                
                # Remove loading message
                loading_label.destroy()
                
                if success:
                    # Show success with data details
                    coverage = coordinator._analyze_existing_data_coverage(city_data.get('city'), state)
                    total_records = coverage.get('total_records', 0)
                    
                    tb.dialogs.Messagebox.show_info(
                        title="Hybrid Data Success ✅", 
                        message=f"Hybrid historical data for {city_data.get('city')} has been processed!\n\n"
                                f"📊 Total data points: {total_records}\n"
                                f"🏗️ Bulk historical: {coverage.get('bulk_records', 0)} records (Open-Meteo)\n"
                                f"⚡ Recent historical: {coverage.get('recent_records', 0)} records (OpenWeather)\n\n"
                                f"Your predictions will now be much more accurate!"
                    )
                else:
                    # Show partial success or error
                    if ";" in str(error):  # Partial success
                        tb.dialogs.Messagebox.show_warning(
                            title="Partial Success ⚠️",
                            message=f"Some data was fetched successfully, but there were issues:\n\n{error}\n\nPredictions may still work with available data."
                        )
                    else:
                        tb.dialogs.Messagebox.show_error(
                            title="Error",
                            message=f"Failed to fetch hybrid historical data: {error}"
                        )
                    
            except Exception as e:
                self.logger.error(f"Error getting hybrid historical data: {e}")
                tb.dialogs.Messagebox.show_error(
                    title="Error",
                    message=f"An error occurred while fetching hybrid historical data: {str(e)}"
                )

        history_btn = tb.Button(
            card,
            text="📊 History",
            command=get_history,
            width=12,
            bootstyle="info-outline"
        )
        history_btn.pack(side="right", padx=10, pady=5)

        # Get Current Weather Button 
        def get_current_weather():
            # Toggle current weather display
            if current_weather_frame.winfo_viewable():
                # Hide current weather
                current_weather_frame.pack_forget()
                current_weather_btn.configure(text="🌤️ Current Weather")
            else:
                # Show current weather
                current_weather_frame.pack(fill="x", padx=20, pady=(10, 0))
                current_weather_btn.configure(text="🌤️ Hide Weather")
                
                # Clear existing weather display
                for widget in current_weather_frame.winfo_children():
                    widget.destroy()
                
                # Show loading message
                loading_label = tb.Label(
                    current_weather_frame,
                    text="🌤️ Fetching current weather...",
                    font=("Helvetica Neue", 12, "italic"),
                    bootstyle="info"
                )
                loading_label.pack(pady=10)
                current_weather_frame.update()
                
                try:
                    # Import and use WeatherAPI directly
                    from core.weather.api import WeatherAPI
                    
                    weather_api = WeatherAPI()
                    state = normalize_state_abbreviation(city_data.get('state', ''))
                    
                    # Fetch comprehensive weather data
                    weather_data = weather_api.fetch_comprehensive_weather(
                        city_data.get('city'),
                        state,
                        'imperial'  # Default to Fahrenheit
                    )
                    
                    # Remove loading message
                    loading_label.destroy()
                    
                    if weather_data and 'error' not in weather_data:
                        # Display current weather data
                        self._display_current_weather(current_weather_frame, weather_data)
                    else:
                        error_msg = weather_data.get('error', 'Unknown error') if weather_data else 'No data received'
                        error_label = tb.Label(
                            current_weather_frame,
                            text=f"❌ Error: {error_msg}",
                            font=("Helvetica Neue", 12),
                            bootstyle="danger"
                        )
                        error_label.pack(pady=10)
                        
                except Exception as e:
                    # Remove loading message if it exists
                    try:
                        loading_label.destroy()
                    except:
                        pass
                        
                    self.logger.error(f"Error getting current weather: {e}")
                    error_label = tb.Label(
                        current_weather_frame,
                        text=f"❌ Error: {str(e)}",
                        font=("Helvetica Neue", 12),
                        bootstyle="danger"
                    )
                    error_label.pack(pady=10)

        current_weather_btn = tb.Button(
            card,
            text="🌤️ Current Weather",
            command=get_current_weather,
            width=15,
            bootstyle="primary-outline"
        )
        current_weather_btn.pack(side="right", padx=10, pady=5)

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

        delete_btn = tb.Button(
            card,
            text="🗑️ Delete",
            command=delete_city,
            width=8,
            bootstyle="danger-outline"
        )
        delete_btn.pack(side="right", padx=5, pady=5)

        # Create prediction display frame (initially hidden)
        prediction_frame = tb.Frame(container)
        prediction_frame.pack(fill="x", padx=20, pady=(10, 0))
        prediction_frame.pack_forget()  # Hide initially
        
        # Create current weather display frame (initially hidden)
        current_weather_frame = tb.Frame(container)
        current_weather_frame.pack(fill="x", padx=20, pady=(10, 0))
        current_weather_frame.pack_forget()  # Hide initially
        
        # Store reference to frames for toggling
        setattr(container, 'prediction_frame', prediction_frame)
        setattr(container, 'current_weather_frame', current_weather_frame)

    def _generate_ml_predictions(self, prediction_frame, city_data):
        """Generate and display ML-based weather predictions"""
        try:
            city = city_data.get('city')
            state = normalize_state_abbreviation(city_data.get('state', ''))
            
            # Check if we have sufficient historical data
            if not self.weather_predictor.has_sufficient_data(city, state):
                # Show option to fetch historical data automatically
                alert_frame = tb.Frame(prediction_frame)
                alert_frame.pack(fill="x", pady=10)
                
                alert_label = tb.Label(
                    alert_frame,
                    text="⚠️ Insufficient historical data",
                    font=("Helvetica Neue", 14, "bold"),
                    bootstyle="warning"
                )
                alert_label.pack(pady=5)
                
                info_label = tb.Label(
                    alert_frame,
                    text="Need at least 60 days of historical data to generate reliable predictions.",
                    font=("Helvetica Neue", 11),
                    justify="center"
                )
                info_label.pack(pady=5)
                
                # Add buttons for manual or automatic data fetch
                button_frame = tb.Frame(alert_frame)
                button_frame.pack(pady=10)
                
                def fetch_data_for_predictions():
                    """Fetch historical data automatically for predictions"""
                    # Clear the alert frame
                    for widget in alert_frame.winfo_children():
                        widget.destroy()
                    
                    # Show loading message
                    loading_label = tb.Label(
                        alert_frame,
                        text="📊 Fetching historical data...",
                        font=("Helvetica Neue", 12, "italic"),
                        bootstyle="info"
                    )
                    loading_label.pack(pady=10)
                    alert_frame.update()
                    
                    try:
                        # Import here to avoid issues during app startup
                        from core.weather.hybrid_data_coordinator import HybridWeatherDataCoordinator
                        
                        coordinator = HybridWeatherDataCoordinator()
                        success, error = coordinator.fetch_combined_historical_data(
                            city, state, 
                            city_data.get('latitude'), 
                            city_data.get('longitude')
                        )
                        
                        # Remove loading message
                        loading_label.destroy()
                        
                        if success:
                            # Data fetched successfully, regenerate predictions
                            for widget in prediction_frame.winfo_children():
                                widget.destroy()
                            self._generate_ml_predictions(prediction_frame, city_data)
                        else:
                            # Show error
                            error_label = tb.Label(
                                alert_frame,
                                text=f"❌ Error fetching data: {error}",
                                font=("Helvetica Neue", 10),
                                bootstyle="danger"
                            )
                            error_label.pack(pady=5)
                            
                    except Exception as e:
                        loading_label.destroy()
                        error_label = tb.Label(
                            alert_frame,
                            text=f"❌ Error: {str(e)}",
                            font=("Helvetica Neue", 10),
                            bootstyle="danger"
                        )
                        error_label.pack(pady=5)
                
                # Auto-fetch button
                auto_btn = tb.Button(
                    button_frame,
                    text="🚀 Auto-Fetch Data",
                    command=fetch_data_for_predictions,
                    bootstyle="success"
                )
                auto_btn.pack(side="left", padx=5)
                
                # Manual button
                manual_btn = tb.Button(
                    button_frame,
                    text="📊 Use History Button",
                    command=lambda: tb.dialogs.Messagebox.show_info(
                        title="Manual Data Fetch",
                        message="Click the '📊 History' button above to manually fetch historical weather data."
                    ),
                    bootstyle="secondary"
                )
                manual_btn.pack(side="left", padx=5)
                
                return
            
            # Show loading message
            loading_label = tb.Label(
                prediction_frame,
                text="🤖 Generating ML predictions...",
                font=("Helvetica Neue", 12, "italic"),
                bootstyle="info"
            )
            loading_label.pack(pady=10)
            prediction_frame.update()
            
            # Generate predictions
            success, predictions = self.weather_predictor.predict_weather(city, state)
            
            # Remove loading message
            loading_label.destroy()
            
            if not success:
                # Show error message
                error_label = tb.Label(
                    prediction_frame,
                    text=f"❌ Error: {predictions.get('error', 'Unknown error')}",
                    font=("Helvetica Neue", 12),
                    bootstyle="danger"
                )
                error_label.pack(pady=10)
                return
            
            # Display prediction header with confidence and trends  
            header_frame = tb.Frame(prediction_frame)
            header_frame.pack(fill="x", pady=(0, 10))
            
            # Get confidence levels (new format with fallback to old format)
            confidence_levels = predictions.get('confidence_levels', {})
            overall_confidence = confidence_levels.get('overall', predictions.get('confidence', 0))
            temp_confidence = confidence_levels.get('temperature', overall_confidence)
            precip_confidence = confidence_levels.get('precipitation', overall_confidence)
            
            confidence_color = "success" if overall_confidence > 0.7 else "warning" if overall_confidence > 0.5 else "danger"
            
            # Main forecast header
            tb.Label(
                header_frame,
                text=f"🔮 3-Day ML Predictions",
                font=("Helvetica Neue", 14, "bold"),
                bootstyle=confidence_color
            ).pack()
            
            # Confidence levels section - inline format
            confidence_section_frame = tb.Frame(header_frame)
            confidence_section_frame.pack(fill="x", pady=(8, 0))
            
            tb.Label(
                confidence_section_frame,
                text=f"📊 Confidence Levels: 🌡️ Temperature: {temp_confidence:.0%}  |  🌧️ Precipitation: {precip_confidence:.0%}  |  📊 Overall: {overall_confidence:.0%}",
                font=("Helvetica Neue", 10, "bold"),
                bootstyle="info"
            ).pack()
            
            # Trend analysis section - inline format
            trend_data = predictions.get('trend', {})
            if 'temperature' in trend_data:
                trend_section_frame = tb.Frame(header_frame)
                trend_section_frame.pack(fill="x", pady=(5, 0))
                
                temp_trend = trend_data['temperature']
                trend_text = temp_trend.get('description', 'No trend data')
                
                tb.Label(
                    trend_section_frame,
                    text=f"📈 Trend Analysis: {trend_text}",
                    font=("Helvetica Neue", 10),
                    bootstyle="info"
                ).pack()
            
            # Create forecast cards
            cards_frame = tb.Frame(prediction_frame)
            cards_frame.pack(fill="x", pady=5)
            
            forecast = predictions.get('forecast', [])
            for day_pred in forecast:
                self._create_prediction_card(cards_frame, day_pred)
            
            # Display model performance info
            performance_frame = tb.Frame(prediction_frame)
            performance_frame.pack(fill="x", pady=(10, 0))
            
            data_points = predictions.get('data_points_used', 0)
            info_text = f"📊 Based on {data_points} days of historical data"
            
            tb.Label(
                performance_frame,
                text=info_text,
                font=("Helvetica Neue", 9),
                bootstyle="secondary"
            ).pack()
            
        except Exception as e:
            self.logger.error(f"Error generating ML predictions: {e}")
            error_label = tb.Label(
                prediction_frame,
                text=f"❌ Error generating predictions: {str(e)}",
                font=("Helvetica Neue", 12),
                bootstyle="danger"
            )
            error_label.pack(pady=10)
    
    def _display_current_weather(self, weather_frame, weather_data):
        """Display current weather data in a compact card matching prediction style"""
        try:
            current_data = weather_data.get('current', {})
            location_data = weather_data.get('location', {})
            
            # Use forecast-specific styles (applied by theme system) - same as forecast_card.py
            try:
                import ttkbootstrap as tb
                frame_style = 'ForecastCard.TFrame'
                day_label_style = 'ForecastDay.TLabel'
                temp_high_style = 'ForecastTempHigh.TLabel'
                desc_label_style = 'ForecastDesc.TLabel'
                precip_label_style = 'ForecastPrecip.TLabel'
            except ImportError:
                frame_style = day_label_style = temp_high_style = desc_label_style = precip_label_style = None
            
            # Create a compact card with custom theme styling
            card = tb.Frame(weather_frame, relief="solid", borderwidth=1, style=frame_style)
            card.pack(pady=5)
            card.pack_propagate(False)  # Maintain fixed size
            card.configure(width=250, height=160)  # Slightly taller for grid layout
            
            # Configure grid weights for centering
            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=1)
            
            # Row 0: Header - "Current Weather" (spans both columns, centered)
            header_label = tb.Label(
                card,
                text="Current Weather",
                style=day_label_style
            )
            if not day_label_style:  # Apply font only if no custom style
                header_label.configure(font=("Helvetica Neue", 11, "bold"))
            header_label.grid(row=0, column=0, columnspan=2, pady=5, sticky="")
            
            # Row 1: Weather condition and current time
            description = current_data.get('description', 'N/A').title()
            main_condition = current_data.get('main', 'N/A')
            
            weather_emoji = {
                'Clear': '☀️',
                'Clouds': '☁️',
                'Rain': '🌧️',
                'Drizzle': '🌦️',
                'Thunderstorm': '⛈️',
                'Snow': '❄️',
                'Mist': '🌫️',
                'Fog': '🌫️',
                'Haze': '🌫️'
            }
            
            emoji = weather_emoji.get(main_condition, '🌤️')
            condition_text = f"{emoji} {description}"
            
            condition_label = tb.Label(
                card,
                text=condition_text,
                style=desc_label_style
            )
            if not desc_label_style:
                condition_label.configure(font=("Helvetica Neue", 9))
            condition_label.grid(row=1, column=0, pady=3, padx=5, sticky="")
            
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            time_label = tb.Label(
                card,
                text=current_time,
                style=desc_label_style
            )
            if not desc_label_style:
                time_label.configure(font=("Helvetica Neue", 9))
            time_label.grid(row=1, column=1, pady=3, padx=5, sticky="")
            
            # Row 2: Temperature and feels like (spans both columns)
            temp = current_data.get('temp', 0)
            feels_like = current_data.get('feels_like', 0)
            temp_text = f"🌡️ {temp:.0f}°F (feels {feels_like:.0f}°F)"
            
            temp_label = tb.Label(
                card,
                text=temp_text,
                style=temp_high_style
            )
            if not temp_high_style:
                temp_label.configure(font=("Helvetica Neue", 9, "bold"))
            temp_label.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky="")
            
            # Row 3: Humidity and Wind
            humidity = current_data.get('humidity', 0)
            humidity_label = tb.Label(
                card,
                text=f"💧 Humidity: {humidity}%",
                style=precip_label_style
            )
            if not precip_label_style:
                humidity_label.configure(font=("Helvetica Neue", 8))
            humidity_label.grid(row=3, column=0, pady=2, padx=5, sticky="")
            
            wind_speed = current_data.get('wind_speed', 0)
            wind_label = tb.Label(
                card,
                text=f"🌪️ Wind: {wind_speed:.0f} mph",
                style=precip_label_style
            )
            if not precip_label_style:
                wind_label.configure(font=("Helvetica Neue", 8))
            wind_label.grid(row=3, column=1, pady=2, padx=5, sticky="")
            
            # Row 4: Additional info if available (pressure and clouds)
            pressure = current_data.get('pressure', 0)
            clouds = current_data.get('clouds', 0)
            
            if pressure > 0:
                pressure_label = tb.Label(
                    card,
                    text=f"🌡️ Pressure: {pressure:.0f} hPa",
                    style=precip_label_style
                )
                if not precip_label_style:
                    pressure_label.configure(font=("Helvetica Neue", 8))
                pressure_label.grid(row=4, column=0, pady=(2, 8), padx=5, sticky="")
            
            if clouds > 0:
                clouds_label = tb.Label(
                    card,
                    text=f"☁️ Clouds: {clouds}%",
                    style=precip_label_style
                )
                if not precip_label_style:
                    clouds_label.configure(font=("Helvetica Neue", 8))
                clouds_label.grid(row=4, column=1, pady=(2, 8), padx=5, sticky="")
                
        except Exception as e:
            self.logger.error(f"Error displaying current weather: {e}")
            error_label = tb.Label(
                weather_frame,
                text=f"❌ Error displaying weather data: {str(e)}",
                font=("Helvetica Neue", 10),
                bootstyle="danger"
            )
            error_label.pack(pady=5)
    
    def _create_prediction_card(self, parent, day_prediction):
        """Create a prediction card for a single day"""
        # Use forecast-specific styles (applied by theme system) - same as forecast_card.py
        try:
            import ttkbootstrap as tb
            frame_style = 'ForecastCard.TFrame'
            day_label_style = 'ForecastDay.TLabel'
            temp_high_style = 'ForecastTempHigh.TLabel'
            desc_label_style = 'ForecastDesc.TLabel'
            precip_label_style = 'ForecastPrecip.TLabel'
        except ImportError:
            frame_style = day_label_style = temp_high_style = desc_label_style = precip_label_style = None
        
        card = tb.Frame(parent, relief="solid", borderwidth=1, style=frame_style)
        card.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Add internal padding to the card
        card.configure(padding=8)
        
        # Day header
        day_name = day_prediction.get('day_name', 'Unknown')
        date = day_prediction.get('date', '')
        
        day_header_label = tb.Label(
            card,
            text=f"{day_name}",
            style=day_label_style
        )
        if not day_label_style:
            day_header_label.configure(font=("Helvetica Neue", 11, "bold"))
        day_header_label.pack(pady=(2, 1), padx=2)
        
        date_label = tb.Label(
            card,
            text=date,
            style=desc_label_style
        )
        if not desc_label_style:
            date_label.configure(font=("Helvetica Neue", 9))
        date_label.pack(padx=2)
        
        # Weather conditions
        conditions = day_prediction.get('conditions', 'Unknown')
        conditions_emoji = {
            'Sunny': '☀️',
            'Partly Cloudy': '⛅',
            'Cloudy': '☁️',
            'Light Rain': '🌦️',
            'Rainy': '🌧️'
        }
        
        condition_text = f"{conditions_emoji.get(conditions, '🌤️')} {conditions}"
        condition_label = tb.Label(
            card,
            text=condition_text,
            style=desc_label_style
        )
        if not desc_label_style:
            condition_label.configure(font=("Helvetica Neue", 9))
        condition_label.pack(pady=2, padx=2)
        
        # Temperature
        temp_max = day_prediction.get('temperature_max')
        temp_min = day_prediction.get('temperature_min')
        if temp_max is not None and temp_min is not None:
            temp_text = f"🌡️ {temp_max:.0f}°/{temp_min:.0f}°F"
            temp_label = tb.Label(
                card,
                text=temp_text,
                style=temp_high_style
            )
            if not temp_high_style:
                temp_label.configure(font=("Helvetica Neue", 9, "bold"))
            temp_label.pack(padx=2)
        
        # Precipitation and humidity
        precip = day_prediction.get('precipitation', 0)
        humidity = day_prediction.get('humidity', 0)
        
        if precip > 0:
            precip_label = tb.Label(
                card,
                text=f"🌧️ Precip: {precip:.1f}\"",
                style=precip_label_style
            )
            if not precip_label_style:
                precip_label.configure(font=("Helvetica Neue", 8))
            precip_label.pack(padx=2)
        
        if humidity:
            humidity_label = tb.Label(
                card,
                text=f"💧 Humidity: {humidity:.0f}%",
                style=precip_label_style
            )
            if not precip_label_style:
                humidity_label.configure(font=("Helvetica Neue", 8))
            humidity_label.pack(padx=2)
    
