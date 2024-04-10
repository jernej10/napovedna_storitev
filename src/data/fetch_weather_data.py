import pandas as pd
import requests
import os


def fetch_weather_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error fetching weather data:", response.status_code)
        return None

def save_raw_weather_data(data, location):
    if data is not None:
        raw_weather_directory = "data/raw/weather"
        if not os.path.exists(raw_weather_directory):
            os.makedirs(raw_weather_directory)
        filename = f"{location}_weather.csv"
        file_path = os.path.join(raw_weather_directory, filename)

        # Extract the current data
        current_data = data['current']

        # Convert current data to DataFrame
        df = pd.DataFrame([current_data])

        if os.path.exists(file_path):
            df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            df.to_csv(file_path, index=False)

def main():
    latitude = 46.562695
    longitude = 15.62935
    weather_data_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m,precipitation,dew_point_2m,relative_humidity_2m,apparent_temperature,surface_pressure"
    weather_data = fetch_weather_data(weather_data_url)
    print("Weather data: ", weather_data)
    save_raw_weather_data(weather_data, "maribor")

if __name__ == "__main__":
    main()