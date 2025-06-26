import matplotlib.pyplot as plt

def generate_temperature_chart(weather_data_list, city_name):
    """Generate and return a line chart of temperatures."""
    # Example placeholder using matplotlib
    dates = [entry["timestamp"] for entry in weather_data_list]
    temps = [entry["temperature"] for entry in weather_data_list]

    plt.figure(figsize=(6,4))
    plt.plot(dates, temps, marker='o')
    plt.title(f"Temperature History - {city_name}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt
