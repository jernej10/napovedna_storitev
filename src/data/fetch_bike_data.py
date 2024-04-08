import pandas as pd
import requests
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
        raw_data_directory = "data/raw/mbajk"
        if not os.path.exists(raw_data_directory):
            os.makedirs(raw_data_directory)
        for station in data:
            filename = f"station_{station['number']}.csv"
            file_path = os.path.join(raw_data_directory, filename)
            file_exists = os.path.isfile(file_path)

            # Process 'position' column
            position = station['position']
            station['latitude'] = position['lat']
            station['longitude'] = position['lng']
            del station['position']

            df = pd.DataFrame([station])

            if file_exists:
                df.to_csv(file_path, mode='a', header=False, index=False)
            else:
                df.to_csv(file_path, index=False)

def main():
    bike_data_url = "https://api.jcdecaux.com/vls/v1/stations?contract=maribor&apiKey=5e150537116dbc1786ce5bec6975a8603286526b"
    bike_data = fetch_bike_data(bike_data_url)
    print("Bike data: ", bike_data)
    save_raw_bike_data(bike_data)

if __name__ == "__main__":
    main()