import json
from datetime import datetime
import os

def save_weather_data(data, filename="data/weather_history.json"):
    """Append weather data to a local JSON file."""
    if not os.path.exists("data"):
        os.makedirs("data")

    entry = {
        "timestamp": datetime.now().isoformat(),
        "city": data.get("name"),
        "temperature": data.get("main", {}).get("temp"),
        "description": data.get("weather", [{}])[0].get("description")
    }

    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                history = json.load(file)
        else:
            history = []

        history.append(entry)

        with open(filename, "w") as file:
            json.dump(history, file, indent=2)

    except Exception as e:
        print(f"Error saving data: {e}")
