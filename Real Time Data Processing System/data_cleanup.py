from datetime import datetime, timedelta
from database import WeatherDB

def clean_old_data():
    db = WeatherDB()
    cutoff_date = datetime.now() - timedelta(days=7)  # Keep data for the last 7 days
    db.delete_old_readings(cutoff_date)

if __name__ == "__main__":
    clean_old_data()
