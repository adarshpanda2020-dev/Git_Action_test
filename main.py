# Author: Claude Developer Agent
# Description: Flask weather service exposing London weather via Open-Meteo API.
# Endpoints: / (health), /weather (current conditions), /health/detail (service info), /forecast (3-day)
# Change: temperatures now returned in both Celsius and Fahrenheit

import os
import platform
import sys
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Service metadata — bumped on each deployment
SERVICE_VERSION = "1.3.0"
SERVICE_START_TIME = datetime.now(timezone.utc).isoformat()

print('Hello World - v5 — adding 3-day forecast endpoint')


def get_london_weather():
    # Fetches current weather for London from the free Open-Meteo API (no key required).
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 51.5074,
        "longitude": -0.1278,
        "current": "temperature_2m,weathercode,windspeed_10m",
        "timezone": "Europe/London",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    current = response.json()["current"]

    code = current["weathercode"]
    temp = current["temperature_2m"]
    wind = current["windspeed_10m"]

    # WMO weather code descriptions (subset of the full WMO 4677 table)
    descriptions = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
        55: "Heavy drizzle", 61: "Slight rain", 63: "Rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
        95: "Thunderstorm",
    }
    description = descriptions.get(code, f"Weather code {code}")
    temp_f = round(temp * 9 / 5 + 32, 1)
    return {"description": description, "temperature_c": temp, "temperature_f": temp_f, "wind_kmh": wind}


@app.route("/")
def health():
    # Simple liveness probe used by Cloud Run health checks.
    return jsonify({"status": "ok"})


@app.route("/health/detail")
def health_detail():
    # Returns detailed service metadata — useful for confirming which version is deployed.
    return jsonify({
        "status": "ok",
        "version": SERVICE_VERSION,
        "started_at": SERVICE_START_TIME,
        "python_version": sys.version,
        "platform": platform.system(),
    })


def get_london_forecast():
    # Fetches the next 3 days of daily max/min temperature and weather code for London.
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 51.5074,
        "longitude": -0.1278,
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
        "timezone": "Europe/London",
        "forecast_days": 3,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    daily = response.json()["daily"]
    descriptions = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
        55: "Heavy drizzle", 61: "Slight rain", 63: "Rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
        95: "Thunderstorm",
    }
    return [
        {
            "date": daily["time"][i],
            "max_temp_c": daily["temperature_2m_max"][i],
            "max_temp_f": round(daily["temperature_2m_max"][i] * 9 / 5 + 32, 1),
            "min_temp_c": daily["temperature_2m_min"][i],
            "min_temp_f": round(daily["temperature_2m_min"][i] * 9 / 5 + 32, 1),
            "description": descriptions.get(daily["weathercode"][i], f"Code {daily['weathercode'][i]}"),
        }
        for i in range(3)
    ]


@app.route("/weather")
def weather():
    # Returns current London weather conditions as JSON.
    data = get_london_weather()
    return jsonify({"city": "London", **data})


@app.route("/forecast")
def forecast():
    # Returns a 3-day daily forecast for London.
    days = get_london_forecast()
    return jsonify({"city": "London", "forecast": days})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
