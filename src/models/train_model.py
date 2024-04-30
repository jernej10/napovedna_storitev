import os
from glob import glob

from sklearn.preprocessing import MinMaxScaler

from src.models.helpers.helper_dataset import load_bike_station_dataset
from src.models.helpers.helper_training import train_model, save_model, build_model

def prepare_and_train_model(station_number: int) -> None:
    #dataset = load_bike_station_dataset(f"../../data/processed/mbajk_processed.csv")
    dataset = load_bike_station_dataset(f"../../data/processed/station_{station_number}.csv")
    dataset.sort_values(by="date", inplace=True)
    dataset.drop(columns=["date"], inplace=True)
    # available_bike_stands on first column of dataset
    dataset = dataset[["available_bike_stands"] + [col for col in dataset.columns if col != "available_bike_stands"]]

    scaler = MinMaxScaler()
    model = train_model(dataset=dataset, scaler=scaler, build_model_fn=build_model, epochs=50, batch_size=7, verbose=0)
    save_model(model, scaler, station_number, "model", "minmax", f"models/station_{station_number}")
    print(f"Model for station {station_number} has been trained and saved!")

def main():
    processed_files = glob("data/processed/station_*.csv")  # Poiščemo vse datoteke s predpono "station_" in končnico ".csv"

    for file_path in processed_files:
        station_number = int(os.path.basename(file_path).split("_")[1].split(".")[0])
        prepare_and_train_model(station_number)
if __name__ == "__main__":
    main()