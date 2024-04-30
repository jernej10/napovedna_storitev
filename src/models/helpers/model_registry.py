import os
import dagshub.auth
import joblib
import onnx
from enum import Enum, auto
from mlflow.onnx import load_model as load_onnx
from mlflow.sklearn import load_model as load_scaler
from dagshub.data_engine.datasources import mlflow
from mlflow import MlflowClient
from sklearn.preprocessing import MinMaxScaler
import dagshub.auth as dh_auth


def get_latest_model_version(station_number: int):
    try:
        client = MlflowClient()
        model_version = client.get_latest_versions("mbajk_station_" + str(station_number), stages=["staging"])[0]
        model_url = model_version.source
        model = load_onnx(model_url)
        return model
    except IndexError:
        print(f"Model for station {station_number} not found.")
        return None


def get_latest_scaler_version(station_number: int):
    try:
        client = MlflowClient()
        model_version = \
            client.get_latest_versions("mbajk_station_" + str(station_number) + "_scaler", stages=["staging"])[0]
        model_url = model_version.source
        scaler = load_scaler(model_url)
        return scaler
    except IndexError:
        print(f"Scaler for station {station_number} not found.")
        return None


def get_production_model(station_number: int):
    try:
        client = MlflowClient()
        model_version = client.get_latest_versions("mbajk_station_" + str(station_number), stages=["production"])[0]
        model_url = model_version.source
        production_model = load_onnx(model_url)
        return production_model
    except IndexError:
        print(f"Production model for station {station_number} not found.")
        return None


def get_production_scaler(station_number: int):
    try:
        client = MlflowClient()
        model_version = \
            client.get_latest_versions("mbajk_station_" + str(station_number) + "_scaler", stages=["production"])[0]
        model_url = model_version.source
        production_scaler = load_scaler(model_url)
        return production_scaler
    except IndexError:
        print(f"Production scaler for station {station_number} not found.")
        return None


class ModelType(Enum):
    LATEST = auto()
    PRODUCTION = auto()


def download_model(number: int, model_type: ModelType) -> tuple[str | None, MinMaxScaler | None]:
    dh_auth.add_app_token(token=os.getenv("DAGSHUB_TOKEN"))
    dagshub.init('napovedna_storitev', 'jernej10', mlflow=True)
    mlflow.set_tracking_uri('https://dagshub.com/jernej10/napovedna_storitev.mlflow')

    folder_name = f"models/{number}"
    model_type_str = model_type.name.lower()

    model_func = get_latest_model_version if model_type == ModelType.LATEST else get_production_model
    scaler_func = get_latest_scaler_version if model_type == ModelType.LATEST else get_production_scaler

    model = model_func(number)
    scaler = scaler_func(number)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    if model is None or scaler is None:
        return None, None

    joblib.dump(scaler, f"{folder_name}/minmax_scaler_{model_type_str}.gz")
    onnx.save_model(model, f"{folder_name}/model_{model_type_str}.onnx")
    print(f"{model_type_str.capitalize()} model for station {number} has been downloaded.")

    # Return model path and scaler
    model_path = f"models/{number}/model_{model_type_str}.onnx"
    return model_path, scaler


def download_model_registry():
    dh_auth.add_app_token(token=os.getenv("DAGSHUB_TOKEN"))
    dagshub.init('napovedna_storitev', 'jernej10', mlflow=True)
    mlflow.set_tracking_uri('https://dagshub.com/jernej10/napovedna_storitev.mlflow')

    for i in range(1, 30):
        model_path = f"models/{i}/model_production.onnx"
        scaler_path = f"models/{i}/minmax_scaler_production.gz"

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            print(f"Model for station {i} already exists.")
            continue

        model = get_production_model(i)
        scaler = get_production_scaler(i)

        if not os.path.exists(f"models/{i}"):
            os.makedirs(f"models/{i}")

        joblib.dump(scaler, f"models/{i}/minmax_scaler_production.gz")
        onnx.save_model(model, f"models/{i}/model_production.onnx")
        print(f"Model for station {i} has been downloaded.")


def empty_model_registry():
    dh_auth.add_app_token(token=os.getenv("DAGSHUB_TOKEN"))
    dagshub.init('napovedna_storitev', 'jernej10', mlflow=True)
    mlflow.set_tracking_uri('https://dagshub.com/jernej10/napovedna_storitev.mlflow')

    client = MlflowClient()
    for i in range(1, 30):
        client.delete_registered_model(f"mbajk_station_{i}")
        client.delete_registered_model(f"mbajk_station_{i}_scaler")