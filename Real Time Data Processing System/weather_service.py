import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from collections import Counter
import time
import threading
import matplotlib.pyplot as plt
from database import WeatherDB
from config import CITIES, OPENWEATHER_API_KEY, UPDATE_INTERVAL, TEMPERATURE_THRESHOLD, CONSECUTIVE_ALERTS 
import os

class WeatherService:
    def __init__(self):
        self.db = WeatherDB()
        self.consecutive_alerts = {city: 0 for city in CITIES}
        self.running = False

    def kelvin_to_celsius(self, kelvin: float) -> float:
        return kelvin - 273.15

    def fetch_weather_data(self, city: str, coords: Dict[str, float]) -> Optional[Dict]:
        try:
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": OPENWEATHER_API_KEY
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                "temperature": self.kelvin_to_celsius(data["main"]["temp"]),
                "feels_like": self.kelvin_to_celsius(data["main"]["feels_like"]),
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "condition": data["weather"][0]["main"],
                "dt": data["dt"]
            }
        except Exception as e:
            print(f"Error fetching weather data for {city}: {str(e)}")
            return None

    def check_temperature_threshold(self, city: str, temperature: float):
        if temperature > TEMPERATURE_THRESHOLD:
            self.consecutive_alerts[city] += 1
            if self.consecutive_alerts[city] >= CONSECUTIVE_ALERTS:
                alert_msg = f"High temperature alert for {city}: {temperature:.1f}°C"
                self.db.save_alert(city, "temperature", alert_msg)
        else:
            self.consecutive_alerts[city] = 0

    def calculate_daily_summary(self, city: str):
        readings = self.db.get_recent_readings(city, 288)  # Last 24 hours (5-minute intervals)
        if not readings:
            return
        
        temperatures = [r["temperature"] for r in readings]
        humidities = [r["humidity"] for r in readings]
        wind_speeds = [r["wind_speed"] for r in readings]
        conditions = [r["condition"] for r in readings]
        
        summary = {
            "avg_temp": sum(temperatures) / len(temperatures),
            "max_temp": max(temperatures),
            "min_temp": min(temperatures),
            "avg_humidity": sum(humidities) / len(humidities),
            "avg_wind_speed": sum(wind_speeds) / len(wind_speeds),
            "dominant_condition": Counter(conditions).most_common(1)[0][0]
        }
        
        self.db.save_daily_summary(
            city=city,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            avg_temp=summary["avg_temp"],
            max_temp=summary["max_temp"],
            min_temp=summary["min_temp"],
            avg_humidity=summary["avg_humidity"],
            avg_wind_speed=summary["avg_wind_speed"],
            dominant_condition=summary["dominant_condition"],
            summary_data={
                "readings_count": len(readings),
                "condition_distribution": dict(Counter(conditions))
            }
        )

        self.generate_temperature_graph(city, readings)

    def generate_temperature_graph(self, city: str, readings: List[Dict]):
        if not readings:
            print(f"No readings available for {city}.")
            return

        dates = [datetime.fromtimestamp(reading['timestamp']).strftime('%Y-%m-%d %H:%M') for reading in readings]
        temps = [reading['temperature'] for reading in readings]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, temps, marker='o', label='Temperature (°C)', color='b')
        plt.title(f'Temperature Trend for {city}')
        plt.xlabel('Time')
        plt.ylabel('Temperature (°C)')
        plt.xticks(rotation=45)
        plt.grid()
        plt.tight_layout()
        plt.legend()

        graph_path = f'static/graphs/{city}_temperature_graph.png'
        plt.savefig(graph_path)
        plt.close()

    def save_weather_reading(self, city: str, weather_data: Dict):
        self.db.save_weather_reading(
            city=city,
            temp=weather_data["temperature"],
            feels_like=weather_data["feels_like"],
            humidity=weather_data["humidity"],
            wind_speed=weather_data["wind_speed"],
            condition=weather_data["condition"]
        )

    def update_weather_data(self):
        self.running = True
        while self.running:
            for city, coords in CITIES.items():
                weather_data = self.fetch_weather_data(city, coords)
                if weather_data:
                    self.save_weather_reading(city, weather_data)
                    self.check_temperature_threshold(city, weather_data["temperature"])
                    self.calculate_daily_summary(city)
            
            time.sleep(UPDATE_INTERVAL)

    def get_alerts(self, city: str):
        return self.db.get_alerts(city)

    def start_service(self):
        threading.Thread(target=self.update_weather_data).start()

    def fetch_weather_forecast(self, city: str, coords: Dict[str, float]) -> Optional[Dict]:
        try:
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "lat": coords["lat"],
                "lon": coords["lon"],
                "appid": OPENWEATHER_API_KEY
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            forecasts = []
            for forecast in data['list']:
                forecasts.append({
                    "datetime": datetime.fromtimestamp(forecast["dt"]),
                    "temperature": self.kelvin_to_celsius(forecast["main"]["temp"]),
                    "condition": forecast["weather"][0]["main"],
                    "humidity": forecast["main"]["humidity"],
                    "wind_speed": forecast["wind"]["speed"]
                })

            return forecasts
        except Exception as e:
            print(f"Error fetching weather forecast for {city}: {str(e)}")
            return None
