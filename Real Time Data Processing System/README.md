## Real-Time Data Processing System for Weather Monitoring with Rollups and Aggregates

This project is a real-time weather monitoring system that fetches weather data from OpenWeatherMap API, stores it in a database, processes daily summaries, and provides alerts based on temperature thresholds. It includes features for visualizing weather trends and displaying 5-day forecasts.

### Features
- Real-Time Data: Periodically fetches weather data for multiple cities from the OpenWeatherMap API, converts temperature from Kelvin to Celsius, and saves readings (temperature, humidity, wind speed, condition) to a SQLite database.
- Temperature Alerts: Tracks consecutive high temperature readings, issues alerts for temperatures above a threshold, and stores these alerts in the database.
- Daily Summaries: Computes daily average, max, and min temperatures, humidity, wind speed, and the most common weather condition for each city, then stores these summaries.
- Data Visualization: Generates temperature trend graphs for each city, saved as PNGs, and displays them on the UI for quick insights.
- 5-Day Forecast: Retrieves and displays a 5-day forecast with temperature, weather conditions, humidity, and wind speed.
- Database Management: Automatically deletes old data to maintain optimal database size.
- Flask Web App: Provides a UI to view weather summaries, forecasts, and alerts, and allows users to start/stop the monitoring service

### Testing Strategy
- Framework: Utilizes pytest for comprehensive testing.
- Mock Responses: Employs mocking tools to simulate API responses, ensuring consistent test conditions.
- Testing Conditions: Verifies API data fetching, rule validations, database updates, and data aggregation logic.

### Prerequisites
- OpenWeatherMap API key

### Setup Steps
- Install the required packages: Run `pip install -r requirements.txt`
- Create a .env file with your OpenWeatherMap API key: `API_KEY=your_openweather_api_key`
- Start the Flask web application : Run `python app.py`
- Access the Application: Navigate to http://127.0.0.1:5000 in your web browser

### Testing
- Run the tests by executing the following command: `pytest test_weather_service.py`

### Configuration
- You can configure cities, update intervals, and temperature thresholds in the config.py file:
  - CITIES: Specify the cities and their coordinates (latitude and longitude).
  - UPDATE_INTERVAL: Set the interval (in seconds) for fetching weather data (default is 300 seconds).
  - TEMPERATURE_THRESHOLD: Set the temperature threshold for alerts (default is 20°C).

### Project Structure
```
weather-monitoring/
│
├── app.py                   # Flask application
├── config.py                # Configuration file for cities and API key
├── database.py              # Database management for weather readings and alerts
├── weather_service.py       # Main weather service logic for fetching data and generating summaries
├── data_cleanup.py          # Script for cleaning old data from the database
├── templates/
│   └── index.html           # HTML template for the Flask app
├── static/
│   ├── styles.css           # CSS file for styling the web app
│   └── graphs/              # Directory to store temperature trend graphs
├── test_weather_service.py   # Test cases for weather service functionality
└── requirements.txt         # Python dependencies
```

### Screenshots
1. UI
![image](https://github.com/user-attachments/assets/a7eb75e6-e803-41ec-b300-bbe2fab2f879)

2. Starting the Weather Monitoring Service
![image](https://github.com/user-attachments/assets/9fee0e42-57b1-4ea9-b3ee-4e2fff6a05da)

3. Select a City and Click "Get Summary" to Retrieve the Weather Summary for that City
![image](https://github.com/user-attachments/assets/14a246bd-8143-43c4-99a7-b997dab36979)

4. The Service Will Run Every 5 Minutes. After 5 Minutes, It Will Look Like This:
![image](https://github.com/user-attachments/assets/2d43c707-c300-4c76-a7ff-107c4cac70dd)

5. Alerts Generated Due to Temperature Exceeding the Threshold
![image](https://github.com/user-attachments/assets/d9ceb2fa-073d-401c-8107-8335a1b17d6b)

6. Stopping the Weather Monitoring Service
![image](https://github.com/user-attachments/assets/cecca245-d48b-4db8-b04a-6ae5733b4d4a)

