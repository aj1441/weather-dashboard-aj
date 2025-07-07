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
    import tkinter as tk
    try:
        import ttkbootstrap as tb
        Frame = tb.Frame
        Label = tb.Label
    except ImportError:
        Frame = tk.Frame
        Label = tk.Label
    from datetime import datetime

    # Card frame with uniform sizing
    if style == 'main':
        card_frame = Frame(parent, relief="raised", borderwidth=2)
        # Set uniform width and height for all cards
        card_frame.configure(width=130, height=180)
        card_frame.pack_propagate(False)  # Prevent internal widgets from changing size
        card_frame.grid_propagate(False)  # Prevent grid from changing size
    else:
        card_frame = Frame(parent)

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

    font_main = ("Helvetica Neue", 12, "bold") if style == 'main' else ("Helvetica Neue", 9, "bold")
    Label(card_frame, text=day_text, font=font_main, anchor="center").pack(pady=(5, 5) if style=='main' else 0)

    # Weather icon
    weather_description = day_data.get('description', 'Clear')
    weather_icon = icon_manager.get_weather_icon(weather_description)
    font_icon = ("Helvetica Neue", 28) if style == 'main' else ("Helvetica Neue", 16)
    Label(card_frame, text=weather_icon, font=font_icon, anchor="center").pack(pady=5 if style=='main' else 0)

    # Temperature
    temp_min = day_data.get('temp_min', 0)
    temp_max = day_data.get('temp_max', 0)
    if style == 'main':
        Label(card_frame, text=f"{int(temp_max)}{unit_label}", font=("Helvetica Neue", 14, "bold")).pack()
        Label(card_frame, text=f"{int(temp_min)}{unit_label}", font=("Helvetica Neue", 12)).pack()
    else:
        Label(card_frame, text=f"{int(temp_max)}{unit_label}/{int(temp_min)}{unit_label}", font=("Helvetica Neue", 9), anchor="center").pack()

    # Description
    desc_label = day_data.get('description', '')
    if style == 'main':
        Label(card_frame, text=desc_label, font=("Helvetica Neue", 9), wraplength=120, justify="center").pack(pady=(5, 0))

    # Precipitation probability
    pop = day_data.get('pop')
    if pop is not None:
        if (style == 'main' and pop > 0) or (style == 'mini' and pop > 0.2):
            pop_text = f"\U0001F4A7 {int(pop * 100)}%"  # 💧
            if style == 'main':
                Label(card_frame, text=pop_text, font=("Helvetica Neue", 8)).pack(pady=(5, 5))
            else:
                Label(card_frame, text=pop_text, font=("Helvetica Neue", 8), anchor="center").pack()

    # Return the card frame without packing it
    # Let the parent component handle the layout
    return card_frame
