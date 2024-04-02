import requests
import pandas as pd
from datetime import datetime, timedelta

from src.data.fetch_data import fetch_weather_data


def fetch_weather_predictions(num_of_predictions):
    latitude = 46.562695
    longitude = 15.62935
    weather_data_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,wind_speed_10m,surface_pressure&forecast_days=2"
    weather_data = fetch_weather_data(weather_data_url)

    if weather_data:
        current_time = datetime.now()
        hourly_data = weather_data['hourly']
        timestamps = hourly_data['time']
        data_for_next_7_hours = []

        for i in range(num_of_predictions):
            next_hour_time = (current_time + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M")
            # Finding the closest available timestamp
            closest_timestamp = min(timestamps, key=lambda x: abs(
            datetime.fromisoformat(x) - datetime.fromisoformat(next_hour_time)))
            time_index = timestamps.index(closest_timestamp)
            data_for_next_7_hours.append({
                'temperature': hourly_data['temperature_2m'][time_index],
                'relative_humidity': hourly_data['relative_humidity_2m'][time_index],
                'dew_point': hourly_data['dew_point_2m'][time_index],
                'apparent_temperature': hourly_data['apparent_temperature'][time_index],
                'precipitation': hourly_data['precipitation_probability'][time_index],
                'wind_speed': hourly_data['wind_speed_10m'][time_index],
                'surface_pressure': hourly_data['surface_pressure'][time_index]
            })

        df = pd.DataFrame(data_for_next_7_hours)
        print(df.head(15))
    else:
        print("Failed to fetch weather data.")

def main():
    fetch_weather_predictions(7)

if __name__ == "__main__":
    main()

