import os
from glob import glob

import joblib
from keras.models import load_model
import dagshub
from dagshub.data_engine.datasources import mlflow
import dagshub.auth as dh_auth

from src.models.helpers.helper_dataset import load_bike_station_dataset, write_metrics_to_file
from src.models.helpers.helper_training import prepare_model_data, evaluate_model_performance, \
    prepare_validation_model_data

from dotenv import load_dotenv
import os

load_dotenv()

def predict_model(station_number):
    test_dataset = load_bike_station_dataset(f"data/validation/station_{station_number}/test.csv")
    test_dataset.sort_values(by="date", inplace=True)
    test_dataset.drop(columns=["date"], inplace=True)
    # available_bike_stands on first column of dataset
    test_dataset = test_dataset[["available_bike_stands"] + [col for col in test_dataset.columns if col != "available_bike_stands"]]

    model = load_model(f"models/validation/station_{station_number}/model.keras")
    scaler = joblib.load(f"models/validation/station_{station_number}/minmax_scaler.gz")

    X_test, y_test = prepare_validation_model_data(test_dataset, scaler)

    mse_test, mae_test, evs_test = evaluate_model_performance(y_test, model.predict(X_test), test_dataset, scaler)

    print(f"mse_test: {mse_test}")
    print(f"mae_test: {mae_test}")
    print(f"evs_test: {evs_test}")

    #write_metrics_to_file(f"../../reports/station_{station_number}/test_metrics.txt", model.name, mse_test, mae_test, evs_test)

    mlflow.start_run(run_name=f"MBAJK station {station_number}", nested=True)
    mlflow.log_metric("mse_test", mse_test)
    mlflow.log_metric("mae_test", mae_test)
    mlflow.log_metric("evs_test", evs_test)

    mlflow.end_run()

    print(f"Test metrics for station {station_number} have been calculated!")

def main():
    test_files = glob("data/validation/station_*/test.csv")

    dh_auth.add_app_token(token="2ea1892ddf473f9f3b467201b8497b5e7c6eade0")
    dagshub.init('napovedna_storitev', 'jernej10', mlflow=True)
    mlflow.set_tracking_uri('https://dagshub.com/jernej10/napovedna_storitev.mlflow')

    if mlflow.active_run():
        mlflow.end_run()

    for test_csv_path in test_files:
        station_number = int(os.path.basename(os.path.dirname(test_csv_path)).split("_")[1])  # Izvlečemo številko postaje iz poti
        predict_model(station_number)

if __name__ == "__main__":
    main()
