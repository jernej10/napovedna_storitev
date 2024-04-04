import csv
from collections import defaultdict

import requests
from pydantic import BaseModel

import requests
import os
import json
from datetime import datetime

''' 
def fetch_bike_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return None


def filter_station_data(data, station_name):
    filtered_data = [station for station in data if station['name'] == station_name]
    return filtered_data


def save_raw_data(data, directory):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = os.path.join(directory, f"raw_data_{timestamp}.csv")
    fieldnames = list(data[0].keys())

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print("Raw data saved successfully as CSV.")

def process_data(data):
    aggregated_data = defaultdict(lambda: {'total_available_bike_stands': 0, 'total_available_bikes': 0, 'count': 0})
    for station in data:
        timestamp = datetime.fromtimestamp(station['last_update'] / 1000)
        hour_key = timestamp.strftime("%Y-%m-%d %H")
        aggregated_data[hour_key]['total_available_bike_stands'] += station['available_bike_stands']
        aggregated_data[hour_key]['total_available_bikes'] += station['available_bikes']
        aggregated_data[hour_key]['count'] += 1

    processed_data = []
    for hour_key, values in aggregated_data.items():
        average_available_bike_stands = values['total_available_bike_stands'] / values['count']
        average_available_bikes = values['total_available_bikes'] / values['count']
        processed_data.append({
            'timestamp': hour_key,
            'average_available_bike_stands': average_available_bike_stands,
            'average_available_bikes': average_available_bikes
        })
    return processed_data

def save_processed_data(data, directory):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = os.path.join(directory, f"processed_data_{timestamp}.csv")
    fieldnames = ['timestamp', 'average_available_bike_stands', 'average_available_bikes']

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print("Processed data saved successfully as CSV.")


def main():
    url = "https://api.jcdecaux.com/vls/v1/stations?contract=maribor&apiKey=5e150537116dbc1786ce5bec6975a8603286526b"
    raw_data = fetch_bike_data(url)
    if raw_data:
        station_name = "GOSPOSVETSKA C. - TURNERJEVA UL."
        filtered_data = filter_station_data(raw_data, station_name)
        if filtered_data:
            raw_data_directory = "../../data/raw"
            processed_data_directory = "../../data/processed"

            if not os.path.exists(raw_data_directory):
                os.makedirs(raw_data_directory)
            if not os.path.exists(processed_data_directory):
                os.makedirs(processed_data_directory)

            save_raw_data(filtered_data, raw_data_directory)

            processed_data = process_data(filtered_data)
            save_processed_data(processed_data, processed_data_directory)


if __name__ == "__main__":
    main()
'''

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
            latitude = position['lat']
            longitude = position['lng']
            station['latitude'] = latitude
            station['longitude'] = longitude
            del station['position']  # Remove the original 'position' column

            with open(file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=station.keys())
                if not file_exists:  # If file doesn't exist, write header
                    writer.writeheader()
                writer.writerow(station)

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

        # Check if the file exists
        file_exists = os.path.isfile(file_path)
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=current_data.keys())
            if not file_exists:  # If file doesn't exist, write header
                writer.writeheader()
            writer.writerow(current_data)

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
