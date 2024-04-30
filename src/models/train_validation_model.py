import os
from glob import glob

from sklearn.preprocessing import MinMaxScaler

from src.models.helpers.helper_dataset import load_bike_station_dataset
from src.models.helpers.helper_training import train_model, save_model, build_model

def prepare_and_train_model(train_csv_path: str, station_number: int) -> None:
    dataset = load_bike_station_dataset(train_csv_path)
    dataset.sort_values(by="date", inplace=True)
    dataset.drop(columns=["date"], inplace=True)
    # available_bike_stands on first column of dataset
    dataset = dataset[["available_bike_stands"] + [col for col in dataset.columns if col != "available_bike_stands"]]

    scaler = MinMaxScaler()
    model = train_model(dataset=dataset, scaler=scaler, build_model_fn=build_model, epochs=50, batch_size=7, verbose=0)
    save_model(model, scaler, station_number, "model", "minmax", f"models/validation/station_{station_number}")
    print(f"Model for station {station_number} has been trained and saved!")

def main():
    train_files = glob("data/validation/station_*/train.csv")  # Poiščemo vse datoteke train.csv v mapi vsake postaje

    for train_csv_path in train_files:
        station_number = int(train_csv_path.split("/")[3].split("_")[1])  # Izvlečemo številko postaje iz poti
        prepare_and_train_model(train_csv_path, station_number)

if __name__ == "__main__":
    main()
