"""
Reusable function to create a forecast card (Tkinter/Ttkbootstrap).
Call from both forecast and saved cities components for deduplication.
"""
def create_forecast_card_tk(parent, day_data, index, icon_manager, style='main', unit_label="°F"):
    """
    Create a forecast card frame for a given day's data.
    Args:
        parent: parent frame
        day_data: dict with weather info
        index: int, day index (0=Tomorrow, 1=Day after tomorrow, etc.)
        icon_manager: instance for weather icons
        style: 'main' (large) or 'mini' (compact)
        unit_label: str, e.g. '°F'
    Returns:
        card_frame: the created Frame
    """
    # import tkinter as tk
    # try:
    #     import ttkbootstrap as tb
    #     Frame = tb.Frame
    #     Label = tb.Label
    # except ImportError:
    #     Frame = tk.Frame
    #     Label = tk.Label
    import tkinter as tk
    try:
        import ttkbootstrap as tb
        Frame = tb.Frame
        Label = tb.Label
        
        # Use forecast-specific styles (applied by theme system)
        frame_style = 'ForecastCard.TFrame'
        day_label_style = 'ForecastDay.TLabel'
        icon_label_style = 'ForecastIcon.TLabel'
        temp_high_style = 'ForecastTempHigh.TLabel'
        temp_low_style = 'ForecastTempLow.TLabel'
        desc_label_style = 'ForecastDesc.TLabel'
        precip_label_style = 'ForecastPrecip.TLabel'
        
    except ImportError:
        Frame = tk.Frame
        Label = tk.Label
        # No styling for plain tkinter
        frame_style = day_label_style = icon_label_style = temp_high_style = temp_low_style = desc_label_style = precip_label_style = None
    
    from datetime import datetime

    # Card frame with uniform sizing
    if style == 'main':
        card_frame = Frame(parent, relief="raised", borderwidth=2, style=frame_style)
        # Set uniform width and height for all cards
        card_frame.configure(width=130, height=180)
        card_frame.pack_propagate(False)  # Prevent internal widgets from changing size
        card_frame.grid_propagate(False)  # Prevent grid from changing size
    else:
        card_frame = Frame(parent, style=frame_style)

    # Day label
    try:
        dt = datetime.fromtimestamp(day_data.get('dt', 0))
        if index == 0:
            day_text = "Tomorrow"  # First forecast day is tomorrow (today is excluded)
        elif index == 1:
            day_text = dt.strftime("%a")  # Day after tomorrow shows day name
        else:
            day_text = dt.strftime("%a")
    except:
        day_text = f"Day {index + 1}"

    # Day label with specific style
    font_main = ("Helvetica Neue", 12, "bold") if style == 'main' else ("Helvetica Neue", 9, "bold")
    day_label = Label(card_frame, text=day_text, anchor="center", style=day_label_style)
    if not day_label_style:  # Apply font only if no custom style
        day_label.configure(font=font_main)
    day_label.pack(pady=(5, 5) if style=='main' else 0)

    # Weather icon with specific style
    weather_description = day_data.get('description', 'Clear')
    weather_icon = icon_manager.get_weather_icon(weather_description)
    font_icon = ("Helvetica Neue", 28) if style == 'main' else ("Helvetica Neue", 16)
    icon_label = Label(card_frame, text=weather_icon, anchor="center", style=icon_label_style)
    if not icon_label_style:  # Apply font only if no custom style
        icon_label.configure(font=font_icon)
    icon_label.pack(pady=5 if style=='main' else 0)

    # Temperature with validation and specific styles
    temp_min = day_data.get('temp_min', 0)
    temp_max = day_data.get('temp_max', 0)
    
    # Validate temperature values
    try:
        temp_min_float = float(temp_min) if temp_min is not None else 0
        temp_max_float = float(temp_max) if temp_max is not None else 0
        
        # Basic sanity check for temperature values
        if temp_min_float < -200 or temp_min_float > 200:
            print(f"Warning: Suspicious temp_min value {temp_min_float} detected in forecast card")
            temp_min_float = 0
        if temp_max_float < -200 or temp_max_float > 200:
            print(f"Warning: Suspicious temp_max value {temp_max_float} detected in forecast card")
            temp_max_float = 0
        
        temp_min = temp_min_float
        temp_max = temp_max_float
    except (ValueError, TypeError):
        print(f"Warning: Non-numeric temperature values detected: min={temp_min}, max={temp_max}. Using defaults.")
        temp_min = 0
        temp_max = 0
    if style == 'main':
        # High temperature
        temp_high_label = Label(card_frame, text=f"{int(temp_max)}{unit_label}", style=temp_high_style)
        if not temp_high_style:
            temp_high_label.configure(font=("Helvetica Neue", 14, "bold"))
        temp_high_label.pack()
        
        # Low temperature  
        temp_low_label = Label(card_frame, text=f"{int(temp_min)}{unit_label}", style=temp_low_style)
        if not temp_low_style:
            temp_low_label.configure(font=("Helvetica Neue", 12))
        temp_low_label.pack()
    else:
        temp_combined_label = Label(card_frame, text=f"{int(temp_max)}{unit_label}/{int(temp_min)}{unit_label}", anchor="center", style=temp_high_style)
        if not temp_high_style:
            temp_combined_label.configure(font=("Helvetica Neue", 9))
        temp_combined_label.pack()

    # Description with specific style
    desc_text = day_data.get('description', '')
    if style == 'main':
        desc_label = Label(card_frame, text=desc_text, wraplength=120, justify="center", style=desc_label_style)
        if not desc_label_style:
            desc_label.configure(font=("Helvetica Neue", 9))
        desc_label.pack(pady=(5, 0))

    # Precipitation probability with validation and specific style
    pop = day_data.get('pop')
    if pop is not None:
        # Validate POP before displaying
        try:
            pop_float = float(pop)
            # Check if POP is in valid range (0-1)
            if 0 <= pop_float <= 1:
                if (style == 'main' and pop_float > 0) or (style == 'mini' and pop_float > 0.2):
                    pop_text = f"\U0001F4A7 {int(pop_float * 100)}%"  # 💧
                    if style == 'main':
                        precip_label = Label(card_frame, text=pop_text, style=precip_label_style)
                        if not precip_label_style:
                            precip_label.configure(font=("Helvetica Neue", 8))
                        precip_label.pack(pady=(5, 5))
                    else:
                        precip_label = Label(card_frame, text=pop_text, anchor="center", style=precip_label_style)
                        if not precip_label_style:
                            precip_label.configure(font=("Helvetica Neue", 8))
                        precip_label.pack()
            else:
                # Invalid POP value (like the 7.6 bug) - log warning but don't crash
                print(f"Warning: Invalid POP value {pop_float} detected in forecast card (should be 0-1, got {pop_float*100:.1f}%). Skipping precipitation display.")
        except (ValueError, TypeError):
            # Non-numeric POP value - log warning but don't crash
            print(f"Warning: Non-numeric POP value '{pop}' detected in forecast card. Skipping precipitation display.")

    # Return the card frame without packing it
    # Let the parent component handle the layout
    return card_frame
