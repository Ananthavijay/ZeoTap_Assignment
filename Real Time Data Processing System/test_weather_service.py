import pytest
from unittest.mock import patch, MagicMock
from weather_service import WeatherService
from database import WeatherDB
from config import CITIES

# Test cases for WeatherService

@pytest.fixture
def weather_service():
    """Fixture to create a WeatherService instance."""
    service = WeatherService()
    return service

def test_api_connection(weather_service):
    """Test if the service initializes correctly."""
    assert weather_service is not None
    assert weather_service.db is not None

@patch('weather_service.requests.get')
def test_fetch_weather_data(mock_get, weather_service):
    """Test fetching weather data from the API."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "main": {
            "temp": 300,
            "feels_like": 298,
            "humidity": 50
        },
        "weather": [{"main": "Clear"}],
        "wind": {"speed": 5},
        "dt": 1609459200  # Example timestamp
    }
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    coords = CITIES['Delhi']
    data = weather_service.fetch_weather_data("Delhi", coords)

    assert data is not None
    assert data["temperature"] == pytest.approx(26.85, rel=1e-2)  # Convert 300K to Celsius
    assert data["feels_like"] == pytest.approx(24.85, rel=1e-2)  # Convert 298K to Celsius
    assert data["condition"] == "Clear"

def test_temperature_conversion(weather_service):
    """Test temperature conversion from Kelvin to Celsius."""
    kelvin_temp = 300
    celsius_temp = weather_service.kelvin_to_celsius(kelvin_temp)
    assert celsius_temp == pytest.approx(26.85, rel=1e-2)

@patch.object(WeatherDB, 'save_weather_reading')
@patch.object(WeatherDB, 'get_recent_readings')
@patch.object(WeatherDB, 'save_daily_summary')
def test_daily_summary_calculation(mock_save_daily_summary, mock_get_recent_readings, mock_save_weather_reading, weather_service):
    """Test calculation of daily summaries."""
    mock_get_recent_readings.return_value = [
        {"temperature": 30 + i, "humidity": 50, "wind_speed": 5, "condition": "Clear", "timestamp": 1609459200 + i * 300}
        for i in range(5)
    ]

    weather_service.calculate_daily_summary("Delhi")
    
    assert mock_save_daily_summary.called
    assert mock_save_daily_summary.call_count == 1
    call_args = mock_save_daily_summary.call_args[1]
    
    assert call_args['avg_temp'] == 32.0
    assert call_args['max_temp'] == 34.0
    assert call_args['min_temp'] == 30.0
    assert call_args['dominant_condition'] == "Clear"

@patch.object(WeatherDB, 'save_alert')
def test_alert_threshold(mock_save_alert, weather_service):
    """Test alert triggering based on temperature thresholds."""
    weather_service.consecutive_alerts["Delhi"] = 2 
    weather_service.check_temperature_threshold("Delhi", 36)
    assert mock_save_alert.called

def test_consecutive_alerts(weather_service):
    """Test tracking of consecutive alerts."""
    weather_service.check_temperature_threshold("Delhi", 36)  # First alert
    weather_service.check_temperature_threshold("Delhi", 37)  # Second alert

    assert weather_service.consecutive_alerts["Delhi"] == 2  # Should have 2 consecutive alerts

    weather_service.check_temperature_threshold("Delhi", 34)  # Below threshold reset
    assert weather_service.consecutive_alerts["Delhi"] == 0  # Should reset to 0
