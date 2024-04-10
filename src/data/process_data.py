import os
import csv


def process_and_save_data(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith('.csv'):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, filename)

            # Preverjanje časovnih žigov za spremembo datoteke
            input_modification_time = os.path.getmtime(input_path)
            output_modification_time = os.path.getmtime(output_path) if os.path.exists(output_path) else 0

            # Če je datoteka izvornega CSV-ja bila spremenjena od zadnjega procesiranja
            if input_modification_time > output_modification_time:
                with open(input_path, 'r', newline='') as mbajk_file, open(output_path, 'w', newline='') as outfile:
                    reader = csv.DictReader(mbajk_file)
                    writer = csv.DictWriter(outfile, fieldnames=['available_bike_stands'])
                    writer.writeheader()

                    for row in reader:
                        processed_row = {
                            'available_bike_stands': row['available_bike_stands']
                        }
                        writer.writerow(processed_row)


            else:
                print(f"No changes detected in {filename}, skipping processing.")

def read_weather_data(weather_path):
    weather_data = []

    with open(weather_path, 'r', newline='') as weather_file:
        reader = csv.DictReader(weather_file)
        for row in reader:
            processed_row = {
                'date': row['time'],
                'temperature': row['temperature_2m'],
                'relative_humidity': row['relative_humidity_2m'],
                'dew_point': row['dew_point_2m'],
                'apparent_temperature': row['apparent_temperature'],
                'precipitation': row['precipitation'],
                'wind_speed': row['wind_speed_10m'],
                'surface_pressure': row['surface_pressure']
            }
            weather_data.append(processed_row)
    return weather_data

def merge_with_weather(csv_directory, weather_data):
    for filename in os.listdir(csv_directory):
        if filename.endswith(".csv"):
            csv_path = os.path.join(csv_directory, filename)
            #weather_timestamp = os.path.getmtime("../../data/raw/weather/maribor_weather.csv")
            #csv_timestamp = os.path.getmtime(csv_path)

            #if weather_timestamp > csv_timestamp:  # Preverimo, ali se je datoteka s podatki o vremenu spremenila
            output_rows = []
            with open(csv_path, 'r', newline='') as csv_file:
                reader = csv.DictReader(csv_file)
                for csv_row, weather_row in zip(reader, weather_data):
                    csv_row.update(weather_row)
                    output_rows.append(csv_row)

            # Zapišemo posodobljene vrstice nazaj v isto datoteko
            with open(csv_path, 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=output_rows[0].keys())
                writer.writeheader()
                writer.writerows(output_rows)
            #else:
             #   print(f"No changes detected.")

def main():
    process_and_save_data('data/raw/mbajk', 'data/processed')
    weather_data = read_weather_data('/data/raw/weather/maribor_weather.csv')
    merge_with_weather('data/processed', weather_data)

if __name__ == "__main__":
    main()