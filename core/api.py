import requests
from config import API_KEY, UNITS, BASE_URL

def fetch_weather_data(city, state, units=UNITS):
    try:
        url = f"{BASE_URL}?q={city},{state},US&appid={API_KEY}&units={units}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
