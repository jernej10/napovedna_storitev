import os
from glob import glob

from sklearn.preprocessing import MinMaxScaler

from src.models.helpers.helper_dataset import load_bike_station_dataset
from src.models.helpers.helper_training import train_model, save_model, build_model
import dagshub
from dagshub.data_engine.datasources import mlflow
import dagshub.auth as dh_auth

from dotenv import load_dotenv
import os

load_dotenv()

def prepare_and_train_model(station_number: int) -> None:
    dataset = load_bike_station_dataset(f"data/validation/station_{station_number}/train.csv")
    dataset.sort_values(by="date", inplace=True)
    dataset.drop(columns=["date"], inplace=True)
    # available_bike_stands on first column of dataset
    dataset = dataset[["available_bike_stands"] + [col for col in dataset.columns if col != "available_bike_stands"]]

    epochs = 50
    batch_size = 7

    scaler = MinMaxScaler()
    model = train_model(dataset=dataset, scaler=scaler, build_model_fn=build_model, epochs=epochs, batch_size=batch_size, verbose=0)
    save_model(model, scaler, station_number, "model", "minmax", f"models/validation/station_{station_number}")

    mlflow.start_run(run_name=f"MBAJK station {station_number}", nested=True)
    mlflow.log_param("epochs", epochs)
    mlflow.log_param("batch_size", batch_size)

    print(f"Model for station {station_number} has been trained and saved!")

def main():
    train_files = glob("data/validation/station_*/train.csv")  # Poiščemo vse datoteke train.csv v mapi vsake postaje

    dh_auth.add_app_token(token="2ea1892ddf473f9f3b467201b8497b5e7c6eade0")
    dagshub.init('napovedna_storitev', 'jernej10', mlflow=True)
    mlflow.set_tracking_uri('https://dagshub.com/jernej10/napovedna_storitev.mlflow')

    if mlflow.active_run():
        mlflow.end_run()

    for train_csv_path in train_files:
        station_number = int(os.path.basename(os.path.dirname(train_csv_path)).split("_")[1])  # Izvlečemo številko postaje iz poti
        prepare_and_train_model(station_number)

if __name__ == "__main__":
    main()
