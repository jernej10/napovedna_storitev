from glob import glob

import dagshub
from dagshub.data_engine.datasources import mlflow
import dagshub.auth as dh_auth
from mlflow import MlflowClient
import onnxruntime as ort

from src.models.helpers.helper_dataset import load_bike_station_dataset, write_metrics_to_file
from src.models.helpers.helper_training import prepare_model_data, evaluate_model_performance, \
    prepare_validation_model_data

from dotenv import load_dotenv
import os

from src.models.helpers.model_registry import download_model, ModelType

load_dotenv()

def update_production_model(station_number: int) -> None:
    client = MlflowClient()

    new_model_version = client.get_latest_versions("mbajk_station_" + str(station_number), stages=["staging"])[
        0].version
    new_scaler_version = \
        client.get_latest_versions("mbajk_station_" + str(station_number) + "_scaler", stages=["staging"])[0].version

    client.transition_model_version_stage("mbajk_station_" + str(station_number), new_model_version, "production")
    client.transition_model_version_stage("mbajk_station_" + str(station_number) + "_scaler", new_scaler_version,
                                          "production")
    print(f"[Update Model] - New model for station {station_number} has been set to production")

def predict_model(station_number):
    test_dataset = load_bike_station_dataset(f"data/validation/station_{station_number}/test.csv")
    test_dataset.sort_values(by="date", inplace=True)
    test_dataset.drop(columns=["date"], inplace=True)
    # available_bike_stands on first column of dataset
    test_dataset = test_dataset[["available_bike_stands"] + [col for col in test_dataset.columns if col != "available_bike_stands"]]

    #model = load_model(f"models/validation/station_{station_number}/model.keras")
    #scaler = joblib.load(f"models/validation/station_{station_number}/minmax_scaler.gz")

    production_model_path, production_scaler = download_model(station_number, ModelType.PRODUCTION)
    latest_model_path, scaler = download_model(station_number, ModelType.LATEST)

    if latest_model_path is None and scaler is None:
        # we don't have a staging model because previous staging model was set to production
        # this could happen when running locally
        return

    if production_model_path is None and production_scaler is None:
        update_production_model(station_number)
        return

    latest_model = ort.InferenceSession(latest_model_path)
    production_model = ort.InferenceSession(production_model_path)

    X_test, y_test = prepare_validation_model_data(test_dataset, scaler)
    latest_model_predictions = latest_model.run(["output"], {"input": X_test})[0]

    mse_test, mae_test, evs_test = evaluate_model_performance(y_test, latest_model_predictions, test_dataset, scaler)

    mlflow.start_run(run_name=f"MBAJK station {station_number}", nested=True)
    mlflow.log_metric("mse_test", mse_test)
    mlflow.log_metric("mae_test", mae_test)
    mlflow.log_metric("evs_test", evs_test)

    production_model_predictions = production_model.run(["output"], {"input": X_test})[0]
    mse_production, mae_production, evs_production = evaluate_model_performance(y_test,
                                                                                production_model_predictions,
                                                                                test_dataset, production_scaler)

    # set model to production if it performs better
    if mse_test < mse_production:
        update_production_model(station_number)

    write_metrics_to_file(f"reports/{station_number}/metrics.txt", "GRU", mse_test, mae_test, evs_test)

    print(f"Test metrics for station {station_number} have been calculated!")

    mlflow.end_run()


def main():
    test_files = glob("data/validation/station_*/test.csv")

    dh_auth.add_app_token(token=os.getenv("DAGSHUB_TOKEN"))
    dagshub.init('napovedna_storitev', 'jernej10', mlflow=True)
    mlflow.set_tracking_uri('https://dagshub.com/jernej10/napovedna_storitev.mlflow')

    if mlflow.active_run():
        mlflow.end_run()

    for test_csv_path in test_files:
        station_number = int(os.path.basename(os.path.dirname(test_csv_path)).split("_")[1])  # Izvlečemo številko postaje iz poti
        predict_model(station_number)

if __name__ == "__main__":
    main()
