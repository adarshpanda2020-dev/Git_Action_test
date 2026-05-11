import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

print('Hello World - v3 for testing cicd')


def get_london_weather():
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

    descriptions = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
        55: "Heavy drizzle", 61: "Slight rain", 63: "Rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
        95: "Thunderstorm",
    }
    description = descriptions.get(code, f"Weather code {code}")
    return {"description": description, "temperature_c": temp, "wind_kmh": wind}


@app.route("/")
def health():
    return jsonify({"status": "ok"})


@app.route("/weather")
def weather():
    data = get_london_weather()
    return jsonify({"city": "London", **data})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
