import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime

# Set initial theme
current_theme = "superhero"  # dark theme to start

app = tb.Window(themename=current_theme)
app.title("Tabbed App with Dark Mode")
app.geometry("500x400")

forecast_highs = []


# === Theme Toggle ===
def toggle_theme():
    global current_theme
    if theme_var.get():
        app.style.theme_use("flatly")  # light theme
        current_theme = "flatly"
    else:
        app.style.theme_use("superhero")  # dark theme
        current_theme = "superhero"


theme_var = tb.BooleanVar(value=False)
dark_mode_toggle = tb.Checkbutton(
    app, text="☀ Light / 🌙 Dark", variable=theme_var,
    command=toggle_theme, bootstyle="info-round-toggle"
)
dark_mode_toggle.pack(pady=10)


# === Tab Setup ===
notebook = tb.Notebook(app, bootstyle="primary")
notebook.pack(expand=True, fill="both", padx=10, pady=10)

# --- Tab 1: Greeting Form ---
tab1 = tb.Frame(notebook)
notebook.add(tab1, text="Greeting")

label = tb.Label(tab1, text="What's your name?", font=("Helvetica Neue", 14))
label.pack(pady=15)

entry = tb.Entry(tab1, width=30)
entry.pack(pady=10)

def greet():
    name = entry.get().strip()
    if name:
        Messagebox.show_info(title="Hello!", message=f"Hello, {name} 👋")
    else:
        Messagebox.show_warning(title="Oops", message="Please enter your name.")

btn = tb.Button(tab1, text="Say Hello", bootstyle="success", command=greet)
btn.pack(pady=10)


# --- Tab 2: Demo Widgets ---
tab2 = tb.Frame(notebook)
notebook.add(tab2, text="Widgets")

meter = tb.Meter(tab2, bootstyle="warning", subtext="Loading...", interactive=True)
meter.pack(pady=20)
meter.configure(amountused=60)

progress = tb.Progressbar(tab2, bootstyle="striped-info", length=200)
progress.pack(pady=10)
progress.start(10)


# --- Tab 3: About ---
tab3 = tb.Frame(notebook)
notebook.add(tab3, text="About")

about_label = tb.Label(
    tab3,
    text="This is a multi-tab GUI built with ttkbootstrap.\nToggle light/dark mode above!",
    justify="center",
    wraplength=400,
    font=("Helvetica Neue", 12)
)
about_label.pack(pady=60)

# -------------------------Additiona addon for weather data-------------------------
# === Weather Tab ===
tab4 = tb.Frame(notebook)
notebook.add(tab4, text="Weather")

unit_var = tb.StringVar(value="imperial")  # default to Fahrenheit

def toggle_units():
    if unit_var.get() == "imperial":
        unit_var.set("metric")  # Celsius
    else:
        unit_var.set("imperial")  # Fahrenheit

unit_toggle = tb.Checkbutton(
    tab4,
    text="°F / °C",
    variable=unit_var,
    onvalue="metric",
    offvalue="imperial",
    command=toggle_units,
    bootstyle="round-toggle"
)
unit_toggle.grid(row=0, column=2, padx=5, pady=5, sticky='w')


# Input Section
city_var = tb.StringVar()
state_var = tb.StringVar()

tb.Label(tab4, text="City:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
city_entry = tb.Entry(tab4, textvariable=city_var, width=20)
city_entry.grid(row=0, column=1, padx=5, pady=5)

tb.Label(tab4, text="State Code (e.g., AZ):").grid(row=1, column=0, padx=5, pady=5, sticky='e')
state_entry = tb.Entry(tab4, textvariable=state_var, width=10)
state_entry.grid(row=1, column=1, padx=5, pady=5)

# Output Display
weather_icon_label = tb.Label(tab4, text="", font=("Helvetica Neue", 40))
weather_icon_label.grid(row=2, column=0, columnspan=2, pady=10)

weather_desc_label = tb.Label(tab4, text="", font=("Helvetica Neue", 14))
weather_desc_label.grid(row=3, column=0, columnspan=2)

# === Function to Fetch Weather ===
def get_weather():
    city = city_var.get().strip()
    state = state_var.get().strip()
    api_key = "a78a26aa78577b7b2d234f2d1efee5a7"  # Replace with your actual key
    units = unit_var.get()
    unit_label = "°C" if units == "metric" else "°F"


    if not city or not state:
        Messagebox.show_warning("Input Error", "Please enter both city and state.")
        return

    try:
        # Get lat/lon from current weather
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{state},US&appid={api_key}&units=imperial&units={units}"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            Messagebox.show_error("API Error", data.get("message", "Unknown error"))
            return

        description = data["weather"][0]["description"]
        temp = round(data["main"]["temp"])
        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        emoji = map_weather_to_emoji(description)
        weather_icon_label.config(text=emoji)
        weather_desc_label.config(text=f"{description.title()} | {temp}{unit_label}")


        # Get 7-day forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=hourly,minutely,alerts&appid={api_key}&units=imperial&units={units}"
        forecast_resp = requests.get(forecast_url)
        forecast_data = forecast_resp.json()

        # Clear old forecast
        for widget in forecast_frame.winfo_children():
            widget.destroy()

        daily = forecast_data["daily"][:7]
        for i, day in enumerate(daily):
            day_name = datetime.fromtimestamp(day["dt"]).strftime("%a")
            day_temp = round(day["temp"]["day"])
            day_desc = day["weather"][0]["description"]
            day_emoji = map_weather_to_emoji(day_desc)

            label = tb.Label(
                forecast_frame,
                text=f"{day_name}\n{day_emoji}\n{round(day_temp)}{unit_label}",
                font=("Helvetica Neue", 12),
                anchor="center",
                width=10,
                relief="ridge",
                padding=5
            )
            label.grid(row=0, column=i, padx=3)

        # Store temps for chart
        global forecast_highs
        forecast_highs = [(datetime.fromtimestamp(day["dt"]).strftime("%a"), day["temp"]["day"]) for day in daily]

    except Exception as e:
        Messagebox.show_error("Error", str(e))


# === Emoji Mapper ===
def map_weather_to_emoji(description):
    d = description.lower()
    if "sun" in d or "clear" in d:
        return "☀️"
    elif "partly" in d:
        return "🌤️"
    elif "cloud" in d:
        return "☁️"
    elif "wind" in d:
        return "🌬️"
    elif "rain" in d:
        return "🌧️"
    elif "thunder" in d:
        return "⛈️"
    elif "snow" in d:
        return "❄️"
    else:
        return "🌡️"

# === Chart Popup Function ===
def open_chart_popup():
    if not forecast_highs:
        Messagebox.show_info("No Data", "Please fetch the forecast first.")
        return

    popup = tb.Toplevel()
    popup.title("7-Day Temperature Chart")
    popup.geometry("500x400")

    days = [d[0] for d in forecast_highs]
    temps = [d[1] for d in forecast_highs]
    unit_label = "°C" if unit_var.get() == "metric" else "°F"

    fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
    ax.plot(days, temps, marker='o', color='royalblue')
    ax.set_title("7-Day Temperature Forecast")
    ax.set_ylabel(f"Temp ({unit_label})")
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=popup)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

    def save_chart():
        fig.savefig("temperature_chart.png")
        Messagebox.show_info("Saved", "Chart saved as temperature_chart.png")

    save_btn = tb.Button(popup, text="💾 Save Chart", bootstyle="success", command=save_chart)
    save_btn.pack(pady=5)

# Button
fetch_btn = tb.Button(tab4, text="Get Weather", bootstyle="primary", command=get_weather)
fetch_btn.grid(row=4, column=0, columnspan=2, pady=10)

chart_btn = tb.Button(tab4, text="📈 View Temperature Chart", bootstyle="info", command=open_chart_popup)
chart_btn.grid(row=6, column=0, columnspan=2, pady=10)

forecast_frame = tb.Frame(tab4)
forecast_frame.grid(row=5, column=0, columnspan=2, pady=10)
# Run it!
app.mainloop()
