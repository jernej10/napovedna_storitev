import os
import pandas as pd

def split_data_for_station(station_directory):
    current_data_path = os.path.join(station_directory, 'current_data.csv')
    station_number = station_directory.split('_')[-1]  # Dobimo številko postaje iz imena mape

    current_data = pd.read_csv(current_data_path)

    test_size = int(0.1 * len(current_data))

    test_data = current_data.head(test_size)
    train_data = current_data.iloc[test_size:]

    test_data.to_csv(os.path.join(station_directory, 'test.csv'), index=False)
    train_data.to_csv(os.path.join(station_directory, 'train.csv'), index=False)

def main():
    validation_directory = 'data/validation'
    for station_directory in os.listdir(validation_directory):
        if station_directory.startswith('station_') and os.path.isdir(os.path.join(validation_directory, station_directory)):
            split_data_for_station(os.path.join(validation_directory, station_directory))

if __name__ == "__main__":
    main()
