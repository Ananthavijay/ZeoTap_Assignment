from flask import Flask, render_template, request, flash, redirect, url_for
from weather_service import WeatherService
import os
from config import CITIES

app = Flask(__name__)
app.secret_key = 'MyL(Q.()(=7%86-5509i'
weather_service = WeatherService()

@app.route("/")
def index():
    city_name = request.args.get('city', 'Delhi')
    cities = weather_service.db.get_daily_summaries(city_name)
    alerts = weather_service.get_alerts(city_name)
    forecast = weather_service.fetch_weather_forecast(city_name, CITIES[city_name])
    return render_template("index.html", cities=CITIES.keys(), summaries=cities, alerts=alerts, forecasts=forecast)

@app.route("/start")
def start():
    weather_service.start_service()
    flash("Weather monitoring service has started.", "success")
    return redirect(url_for('index'))

@app.route("/stop")
def stop():
    weather_service.running = False
    flash("Weather monitoring has stopped.", "error")
    return redirect(url_for('index'))

if __name__ == "__main__":
    if not os.path.exists('static/graphs'):
        os.makedirs('static/graphs')
    
    app.run(debug=True)
