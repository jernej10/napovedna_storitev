import os
from glob import glob

import tensorflow as tf
from mlflow import MlflowClient
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
import tf2onnx
from mlflow.onnx import log_model as log_onnx_model
from mlflow.models import infer_signature
from mlflow.sklearn import log_model as log_sklearn_model

from src.models.helpers.helper_dataset import load_bike_station_dataset
from src.models.helpers.helper_training import train_model, save_model, build_model, prepare_model_data
import dagshub
from dagshub.data_engine.datasources import mlflow
import dagshub.auth as dh_auth

from dotenv import load_dotenv
import os

load_dotenv()

def prepare_and_train_model(station_number: int) -> None:
    client = MlflowClient()


    dataset = load_bike_station_dataset(f"data/validation/station_{station_number}/train.csv")
    dataset.sort_values(by="date", inplace=True)
    dataset.drop(columns=["date"], inplace=True)
    # available_bike_stands on first column of dataset
    dataset = dataset[["available_bike_stands"] + [col for col in dataset.columns if col != "available_bike_stands"]]

    # Sklearn pipeline
    pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),  # Impute missing values with mean
        ('scaler', MinMaxScaler())  # Scale features to [0, 1] range
    ])

    transformer = ColumnTransformer(
        transformers=[
            ('pipeline', pipeline, dataset.columns)  # Apply transformer to all columns
        ],
        remainder='drop',
        n_jobs=-1)

    # Run the pipeline
    dataset = transformer.fit_transform(dataset)

    epochs = 50
    batch_size = 7
    window_size = 2
    top_features = 9

    # Get the scaler from the pipeline
    scaler = transformer.named_transformers_['pipeline'].named_steps['scaler']
    X_train, y_train, X_test, y_test = prepare_model_data(dataset=dataset, scaler=None)

    #scaler = MinMaxScaler()
    model = train_model(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, scaler=None, build_model_fn=build_model, epochs=epochs, batch_size=batch_size, verbose=0)

    model.output_names = ["output"]
    input_signature = [
        tf.TensorSpec(shape=(None, window_size, top_features), dtype=tf.double, name="input")
    ]

    onnx_model, _ = tf2onnx.convert.from_keras(model=model, input_signature=input_signature, opset=13)

    model_ = log_onnx_model(onnx_model=onnx_model,
                            artifact_path=f"models/station_{station_number}",
                            signature=infer_signature(X_test, model.predict(X_test)),
                            registered_model_name="mbajk_station_" + str(station_number))

    mv = client.create_model_version(name="mbajk_station_" + str(station_number), source=model_.model_uri,
                                     run_id=model_.run_id)
    client.transition_model_version_stage("mbajk_station_" + str(station_number), mv.version, "staging")

    # save scaler
    scaler_meta = {"feature_range": scaler.feature_range}
    scaler = log_sklearn_model(
        sk_model=scaler,
        artifact_path=f"scalers/station_{station_number}",
        registered_model_name="mbajk_station_" + str(station_number) + "_scaler",
        metadata=scaler_meta
    )

    sv = client.create_model_version(name="mbajk_station_" + str(station_number) + "_scaler", source=scaler.model_uri,
                                     run_id=scaler.run_id)
    # set stage
    client.transition_model_version_stage("mbajk_station_" + str(station_number) + "_scaler", sv.version, "staging")

    #save_model(model, scaler, station_number, "model", "minmax", f"models/validation/station_{station_number}")

    mlflow.start_run(run_name=f"MBAJK station {station_number}", nested=True)
    mlflow.log_param("epochs", epochs)
    mlflow.log_param("batch_size", batch_size)

    print(f"Model for station {station_number} has been trained and saved!")

    mlflow.end_run()

def main():
    train_files = glob("data/validation/station_*/train.csv")  # Poiščemo vse datoteke train.csv v mapi vsake postaje
    dh_auth.add_app_token(token=os.getenv("DAGSHUB_TOKEN"))
    dagshub.init('napovedna_storitev', 'jernej10', mlflow=True)
    mlflow.set_tracking_uri('https://dagshub.com/jernej10/napovedna_storitev.mlflow')

    if mlflow.active_run():
        mlflow.end_run()

    for train_csv_path in train_files:
        station_number = int(os.path.basename(os.path.dirname(train_csv_path)).split("_")[1])  # Izvlečemo številko postaje iz poti
        prepare_and_train_model(station_number)

if __name__ == "__main__":
    main()
