"""Saved cities component for managing favorite locations"""

import logging
import ttkbootstrap as tb
from ttkbootstrap.scrolled import ScrolledFrame
from core.data_handler import WeatherDataHandler
from core.weather_predictor import WeatherPredictor
from utils.state_utils import normalize_state_abbreviation

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

        # Get History Button
        def get_history():
            from core.historical_coordinator import HistoricalDataCoordinator
            
            try:
                coordinator = HistoricalDataCoordinator()
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
                self.logger.info(f"Fetching historical data for {city_data.get('city')}")
                loading_label = tb.Label(
                    card,
                    text="Loading historical data...",
                    font=("Helvetica Neue", 10, "italic")
                )
                loading_label.pack(side="right", padx=5)
                card.update()
                
                # Fetch and store historical data
                success, error = coordinator.fetch_and_store_historical_data(
                    city=city_data.get('city'),
                    state=state,
                    latitude=lat,
                    longitude=lon
                )
                
                # Remove loading message
                loading_label.destroy()
                
                if success:
                    tb.dialogs.Messagebox.show_info(
                        title="Success", 
                        message=f"Historical data for {city_data.get('city')} has been processed.\n\nNew data has been saved (duplicates were skipped automatically)."
                    )
                else:
                    tb.dialogs.Messagebox.show_error(
                        title="Error",
                        message=f"Failed to fetch historical data: {error}"
                    )
                    
            except Exception as e:
                self.logger.error(f"Error getting historical data: {e}")
                tb.dialogs.Messagebox.show_error(
                    title="Error",
                    message=f"An error occurred while fetching historical data: {str(e)}"
                )

        history_btn = tb.Button(
            card,
            text="📊 History",
            command=get_history,
            width=10,
            bootstyle="info-outline"
        )
        history_btn.pack(side="right", padx=10, pady=5)

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
        
        # Store reference to prediction frame for toggling
        setattr(container, 'prediction_frame', prediction_frame)

    def _generate_ml_predictions(self, prediction_frame, city_data):
        """Generate and display ML-based weather predictions"""
        try:
            city = city_data.get('city')
            state = normalize_state_abbreviation(city_data.get('state', ''))
            
            # Check if we have sufficient historical data
            if not self.weather_predictor.has_sufficient_data(city, state):
                # Show alert for missing historical data
                alert_frame = tb.Frame(prediction_frame)
                alert_frame.pack(fill="x", pady=10)
                
                alert_label = tb.Label(
                    alert_frame,
                    text="⚠️ Please get history first",
                    font=("Helvetica Neue", 14, "bold"),
                    bootstyle="warning"
                )
                alert_label.pack(pady=5)
                
                info_label = tb.Label(
                    alert_frame,
                    text="Need at least 60 days of historical data to generate reliable predictions.\nClick '📊 History' button first to fetch historical weather data.",
                    font=("Helvetica Neue", 11),
                    justify="center"
                )
                info_label.pack(pady=5)
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
            
            confidence = predictions.get('confidence', 0)
            confidence_color = "success" if confidence > 0.7 else "warning" if confidence > 0.5 else "danger"
            
            tb.Label(
                header_frame,
                text=f"🔮 3-Day ML Forecast (Confidence: {confidence:.0%})",
                font=("Helvetica Neue", 14, "bold"),
                bootstyle=confidence_color
            ).pack()
            
            # Display trend information
            trend_data = predictions.get('trend', {})
            if 'temperature' in trend_data:
                temp_trend = trend_data['temperature']
                trend_text = f"📈 {temp_trend.get('description', 'No trend data')}"
                
                tb.Label(
                    header_frame,
                    text=trend_text,
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
    
    def _create_prediction_card(self, parent, day_prediction):
        """Create a prediction card for a single day"""
        card = tb.Frame(parent, relief="solid", borderwidth=1)
        card.pack(side="left", fill="both", expand=True, padx=3, pady=5)
        
        # Day header
        day_name = day_prediction.get('day_name', 'Unknown')
        date = day_prediction.get('date', '')
        
        tb.Label(
            card,
            text=f"{day_name}",
            font=("Helvetica Neue", 11, "bold")
        ).pack(pady=2)
        
        tb.Label(
            card,
            text=date,
            font=("Helvetica Neue", 9)
        ).pack()
        
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
        tb.Label(
            card,
            text=condition_text,
            font=("Helvetica Neue", 9)
        ).pack(pady=2)
        
        # Temperature
        temp_max = day_prediction.get('temperature_max')
        temp_min = day_prediction.get('temperature_min')
        if temp_max is not None and temp_min is not None:
            temp_text = f"🌡️ {temp_max:.0f}°/{temp_min:.0f}°F"
            tb.Label(
                card,
                text=temp_text,
                font=("Helvetica Neue", 9, "bold")
            ).pack()
        
        # Precipitation and humidity
        precip = day_prediction.get('precipitation', 0)
        humidity = day_prediction.get('humidity', 0)
        
        if precip > 0:
            tb.Label(
                card,
                text=f"🌧️ {precip:.1f}\"",
                font=("Helvetica Neue", 8)
            ).pack()
        
        if humidity:
            tb.Label(
                card,
                text=f"💧 {humidity:.0f}%",
                font=("Helvetica Neue", 8)
            ).pack()
    
    def restyle(self):
        """Force a style refresh for saved cities widgets."""
        try:
            if hasattr(self, "cities_frame"):
                self.cities_frame.update_idletasks()

                for widget in self.cities_frame.winfo_children():
                    try:
                        widget.configure()  # Re-apply styles
                    except Exception:
                        pass  # Ignore widgets that don't support configure()

            self.logger.info("SavedCitiesComponent restyled.")
        except Exception as e:
            self.logger.error(f"Error during restyle in SavedCitiesComponent: {e}")
