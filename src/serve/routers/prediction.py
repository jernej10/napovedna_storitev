from typing import List
import joblib
from fastapi import APIRouter, HTTPException
from keras.models import load_model
from pydantic import BaseModel
import numpy as np



window_size = 2

def create_time_series(data, window_size, feature_cols):
    sequences = []
    n_samples = len(data)

    for i in range(window_size, n_samples + 1):
        sequence = data[i - window_size:i, feature_cols]
        sequences.append(sequence)

    return np.array(sequences)


def use_model_prediction(data, model, scaler, feature_cols):
    prediction = model.predict(data)
    prediction_copies_array = np.repeat(prediction, len(feature_cols), axis=-1)
    prediction_reshaped = np.reshape(prediction_copies_array, (len(prediction), len(feature_cols)))
    prediction = scaler.inverse_transform(prediction_reshaped)[:, 0]

    return int(prediction.tolist()[0])

router = APIRouter(
    prefix="/mbajk",
    tags=["Prediction"],
    responses={404: {"description": "Not found"}},
)


class PredictionInput(BaseModel):
    available_bike_stands: int
    bike_stands: int
    temperature: float
    relative_humidity: float
    dew_point: float
    apparent_temperature: float
    precipitation: float
    wind_speed: float
    surface_pressure: float


model = load_model("../../models/station_1/model.keras")
scaler = joblib.load("../../models/station_1/minmax_scaler.gz")


@router.post("/predict")
def predict(data: List[PredictionInput]):
    print('data:', data)
    if len(data) != window_size:
        raise HTTPException(status_code=400, detail=f"Data must contain {window_size} items")

    data = [[data_slice.available_bike_stands, data_slice.bike_stands, data_slice.temperature,
             data_slice.relative_humidity, data_slice.dew_point, data_slice.apparent_temperature, data_slice.precipitation, data_slice.wind_speed, data_slice.surface_pressure] for data_slice in data]

    scaled_data = scaler.transform(data)
    feature_cols = list(range(len(data[0])))

    X = create_time_series(scaled_data, window_size, feature_cols)

    prediction = use_model_prediction(X, model, scaler, feature_cols)

    return {"prediction": prediction}