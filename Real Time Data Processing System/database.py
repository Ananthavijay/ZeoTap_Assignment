import sqlite3
from datetime import datetime
import json
from typing import Dict
import time

class WeatherDB:
    def __init__(self, db_name="weather_data.db"):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS weather_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temperature REAL,
            feels_like REAL,
            humidity REAL,
            wind_speed REAL,
            condition TEXT,
            timestamp INTEGER
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS daily_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            date TEXT,
            avg_temp REAL,
            max_temp REAL,
            min_temp REAL,
            avg_humidity REAL,
            avg_wind_speed REAL,
            dominant_condition TEXT,
            summary_data TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            alert_type TEXT,
            message TEXT,
            timestamp INTEGER
        )''')
        
        conn.commit()
        conn.close()

    def delete_old_readings(self, cutoff_date: datetime):
        cutoff_timestamp = int(cutoff_date.timestamp())
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM weather_readings WHERE timestamp < ?", (cutoff_timestamp,))
        conn.commit()
        conn.close()

    def save_weather_reading(self, city: str, temp: float, feels_like: float, humidity: float, wind_speed: float, condition: str):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''INSERT INTO weather_readings (city, temperature, feels_like, humidity, wind_speed, condition, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', (city, temp, feels_like, humidity, wind_speed, condition, int(time.time())))
        conn.commit()
        conn.close()

    def save_daily_summary(self, city: str, date: str, avg_temp: float, max_temp: float, min_temp: float, avg_humidity: float, avg_wind_speed: float, dominant_condition: str, summary_data: Dict):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''INSERT INTO daily_summaries (city, date, avg_temp, max_temp, min_temp, avg_humidity, avg_wind_speed, dominant_condition, summary_data)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (city, date, avg_temp, max_temp, min_temp, avg_humidity, avg_wind_speed, dominant_condition, json.dumps(summary_data)))
        conn.commit()
        conn.close()

    def save_alert(self, city: str, alert_type: str, message: str):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''INSERT INTO alerts (city, alert_type, message, timestamp)
                     VALUES (?, ?, ?, ?)''', (city, alert_type, message, int(time.time())))
        conn.commit()
        conn.close()

    def get_alerts(self, city: str):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT city, alert_type, message, timestamp FROM alerts WHERE city = ?", (city,))
        alerts = [{"city": row[0], "alert_type": row[1], "message": row[2], "timestamp": datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M')} for row in c.fetchall()]
        conn.close()
        return alerts

    def get_recent_readings(self, city: str, limit: int):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT temperature, humidity, wind_speed, condition, timestamp FROM weather_readings WHERE city = ? ORDER BY timestamp DESC LIMIT ?", (city, limit))
        readings = [{"temperature": row[0], "humidity": row[1], "wind_speed": row[2], "condition": row[3], "timestamp": row[4]} for row in c.fetchall()]
        conn.close()
        return readings

    def get_daily_summaries(self, city: str, date=None):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        if date is None:
            c.execute("SELECT date, avg_temp, max_temp, min_temp, avg_humidity, avg_wind_speed, dominant_condition FROM daily_summaries WHERE city = ?", (city,))
        else:
            c.execute("SELECT date, avg_temp, max_temp, min_temp, avg_humidity, avg_wind_speed, dominant_condition FROM daily_summaries WHERE city = ? AND date = ?", (city, date))
        summaries = [{"city": city, "date": row[0], "avg_temp": row[1], "max_temp": row[2], "min_temp": row[3], "avg_humidity": row[4], "avg_wind_speed": row[5], "dominant_condition": row[6]} for row in c.fetchall()]
        conn.close()
        return summaries
