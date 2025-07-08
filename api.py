"""Simple API wrapper used for unit tests."""
import requests

def fetch_weather(city):
    """Fetch mock weather data for tests."""
    url = f"https://api.example.com/weather/{city}"
    resp = requests.get(url, timeout=5)
    if resp.status_code != 200:
        raise ValueError("API request failed")
    data = resp.json()
    return {
        "city": city,
        "temp_c": round(data["current"]["temp_k"] - 273.15, 1),
        "description": data["current"]["condition"]["text"],
    }
