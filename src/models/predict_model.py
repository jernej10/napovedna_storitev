import os
from glob import glob

import joblib
from keras.models import load_model

from src.models.helpers.helper_dataset import load_bike_station_dataset, write_metrics_to_file
from src.models.helpers.helper_training import prepare_model_data, evaluate_model_performance


def predict_model(station_number):
    dataset = load_bike_station_dataset(f"station_{station_number}.csv")
    dataset.sort_values(by="date", inplace=True)
    dataset.drop(columns=["date"], inplace=True)
    # available_bike_stands on first column of dataset
    dataset = dataset[["available_bike_stands"] + [col for col in dataset.columns if col != "available_bike_stands"]]

    model = load_model(f"../../models/station_{station_number}/model.keras")
    scaler = joblib.load(f"../../models/station_{station_number}/minmax_scaler.gz")

    X_train, y_train, X_test, y_test = prepare_model_data(dataset=dataset, scaler=scaler)

    mse_train, mae_train, evs_train = evaluate_model_performance(y_train, model.predict(X_train), dataset, scaler)
    mse_test, mae_test, evs_test = evaluate_model_performance(y_test, model.predict(X_test), dataset, scaler)

    write_metrics_to_file(f"../../reports/station_{station_number}/train_metrics.txt", model.name, mse_train, mae_train,
                          evs_train)
    write_metrics_to_file(f"../../reports/station_{station_number}/metrics.txt", model.name, mse_test, mae_test, evs_test)

    print(f"Train metrics for station {station_number} have been calculated!")

def main():
    station_numbers = []
    processed_files = glob(
        "../../data/processed/station_*.csv")  # Poiščemo vse datoteke s predpono "station_" in končnico ".csv"

    for file_path in processed_files:
        station_number = int(os.path.basename(file_path).split("_")[1].split(".")[0])
        station_numbers.append(station_number)

    for station_number in station_numbers:
        predict_model(station_number)

if __name__ == "__main__":
    main()