import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_weather(city, api_key):
    """Get current weather for a city"""
    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return {
            "city": data["name"],
            "temp": data["main"]["temp"],
            "condition": data["weather"][0]["description"]
        }
    except Exception as e:
        return {"error": str(e)}


def get_exchange_rate(from_currency, to_currency):
    """Get exchange rate between two currencies"""
    try:
        response = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/{from_currency}",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        rate = data["rates"].get(to_currency)
        return {"rate": rate, "from": from_currency, "to": to_currency}
    except Exception as e:
        return {"error": str(e)}


def generate_report():
    """Generate a combined daily briefing"""
    api_key = os.environ.get("WEATHER_API_KEY")
    weather = get_weather("London", api_key)
    rate = get_exchange_rate("GBP", "USD")

    print("=" * 40)
    print(f"Daily Briefing - {datetime.now().strftime('%d %B %Y')}")
    print("=" * 40)

    if "error" not in weather:
        print(f"Weather: {weather['city']} — {weather['temp']}°C, {weather['condition']}")
    else:
        print(f"Weather unavailable: {weather['error']}")

    if "error" not in rate:
        print(f"GBP/USD: {rate['rate']}")
    else:
        print(f"Exchange rate unavailable: {rate['error']}")

    print("=" * 40)
    print("Report complete.")


if __name__ == "__main__":
    generate_report()
