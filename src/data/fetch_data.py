import pandas as pd
import requests
import csv
import os

def fetch_bike_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error fetching data:", response.status_code)
        return None

def save_raw_bike_data(data):
    if data is not None:
        raw_data_directory = "../../data/raw/mbajk"
        if not os.path.exists(raw_data_directory):
            os.makedirs(raw_data_directory)
        for station in data:
            filename = f"station_{station['number']}.csv"
            file_path = os.path.join(raw_data_directory, filename)
            # Check if the file exists
            file_exists = os.path.isfile(file_path)
            # Process 'position' column
            position = station['position']
            station['latitude'] = position['lat']
            station['longitude'] = position['lng']
            del station['position']  # Remove the original 'position' column

            # TODO probaj na tak način (pa v weather tud daj)
            df = pd.DataFrame([station])

            if file_exists:
                df.to_csv(file_path, mode='a', header=False, index=False)
            else:
                df.to_csv(file_path, index=False)

            #with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            #    writer = csv.DictWriter(file, fieldnames=station.keys())
            #    if not file_exists:  # If file doesn't exist, write header
            #        writer.writeheader()
            #    writer.writerow(station)

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
        raw_weather_directory = "../../data/raw/weather"
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

        # Check if the file exists
        #file_exists = os.path.isfile(file_path)
        #with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        #    writer = csv.DictWriter(file, fieldnames=current_data.keys())
        #    if not file_exists:  # If file doesn't exist, write header
        #        writer.writeheader()
        #    writer.writerow(current_data)

def main():
    bike_data_url = "https://api.jcdecaux.com/vls/v1/stations?contract=maribor&apiKey=5e150537116dbc1786ce5bec6975a8603286526b"
    bike_data = fetch_bike_data(bike_data_url)
    print(bike_data)
    save_raw_bike_data(bike_data)

    latitude = 46.562695
    longitude = 15.62935
    weather_data_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m,precipitation,dew_point_2m,relative_humidity_2m,apparent_temperature,surface_pressure"
    weather_data = fetch_weather_data(weather_data_url)
    print(weather_data)
    save_raw_weather_data(weather_data, "Maribor")

if __name__ == "__main__":
    main()
