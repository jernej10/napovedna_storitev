from datetime import datetime, timedelta
from typing import List
import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from keras.models import load_model
from pydantic import BaseModel
import numpy as np
import requests


window_size = 2

def fetch_weather_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error fetching weather data:", response.status_code)
        return None
def fetch_weather_predictions(num_of_predictions):
    latitude = 46.562695
    longitude = 15.62935
    weather_data_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relative_humidity_2m,dew_point_2m,apparent_temperature,precipitation_probability,wind_speed_10m,surface_pressure&forecast_days=2"
    weather_data = fetch_weather_data(weather_data_url)

    if weather_data:
        current_time = datetime.now()
        hourly_data = weather_data['hourly']
        timestamps = hourly_data['time']
        data_for_next_7_hours = []

        for i in range(num_of_predictions):
            next_hour_time = (current_time + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M")
            # Finding the closest available timestamp
            closest_timestamp = min(timestamps, key=lambda x: abs(
            datetime.fromisoformat(x) - datetime.fromisoformat(next_hour_time)))
            time_index = timestamps.index(closest_timestamp)
            data_for_next_7_hours.append({
                'temperature': hourly_data['temperature_2m'][time_index],
                'relative_humidity': hourly_data['relative_humidity_2m'][time_index],
                'dew_point': hourly_data['dew_point_2m'][time_index],
                'apparent_temperature': hourly_data['apparent_temperature'][time_index],
                'precipitation': hourly_data['precipitation_probability'][time_index],
                'wind_speed': hourly_data['wind_speed_10m'][time_index],
                'surface_pressure': hourly_data['surface_pressure'][time_index]
            })

        df = pd.DataFrame(data_for_next_7_hours)
        print(df.head(15))
        return df
    else:
        print("Failed to fetch weather data.")

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


#model = load_model("../../models/station_1/model.keras")
#scaler = joblib.load("../../models/station_1/minmax_scaler.gz")


@router.post("/predict/{station_name}")
def predict(station_name: str, data: List[PredictionInput]):
    if len(data) != window_size:
        raise HTTPException(status_code=400, detail=f"Data must contain {window_size} items")

    print(f"Predicting for station {station_name}")
    model_path = f"../../models/{station_name}/model.keras"
    scaler_path = f"../../models/{station_name}/minmax_scaler.gz"

    try:
        model = load_model(model_path)
        scaler = joblib.load(scaler_path)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to load model or scaler: {e}")

    data = [[data_slice.available_bike_stands, data_slice.bike_stands, data_slice.temperature,
             data_slice.relative_humidity, data_slice.dew_point, data_slice.apparent_temperature, data_slice.precipitation, data_slice.wind_speed, data_slice.surface_pressure] for data_slice in data]

    scaled_data = scaler.transform(data)
    feature_cols = list(range(len(data[0])))

    X = create_time_series(scaled_data, window_size, feature_cols)

    prediction = use_model_prediction(X, model, scaler, feature_cols)

    return {"prediction": prediction}

@router.post("/predict/{station_name}/{hours}")
def predict_7_hours(station_name: str, hours: int):
    # Preberi CSV in izberi zadnje window_size*2 vrstic
    try:
        df = pd.read_csv(f"../../data/processed/{station_name}.csv")
        last_rows = df.tail(window_size)
        data = [
            PredictionInput(
                available_bike_stands=row.available_bike_stands,
                bike_stands=row.bike_stands,
                temperature=row.temperature,
                relative_humidity=row.relative_humidity,
                dew_point=row.dew_point,
                apparent_temperature=row.apparent_temperature,
                precipitation=row.precipitation,
                wind_speed=row.wind_speed,
                surface_pressure=row.surface_pressure
            )
            for _, row in last_rows.iterrows()
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read CSV: {e}")

    predictions = []

    for _ in range(hours):
        # Pridobi podatke o vremenu za trenutno uro
        weather_data = fetch_weather_predictions(hours)  # Pridobi vse podatke za vseh 7 ur
        current_weather_data = weather_data.iloc[_]  # Izberi podatke za trenutno uro
        # Napoved za trenutno uro
        prediction = predict(station_name, data[-window_size:])  # Uporabi zadnja dva elementa
        predictions.append(prediction['prediction'])

        # Dodaj podatke o vremenu in napoved v 'data' za naslednjo napoved
        data.append(
            PredictionInput(
                available_bike_stands=prediction['prediction'],  # Uporabi napoved iz prejšnje iteracije
                bike_stands=data[-1].bike_stands,  # Podatki o številu koles
                temperature=current_weather_data.temperature,
                relative_humidity=current_weather_data.relative_humidity,
                dew_point=current_weather_data.dew_point,
                apparent_temperature=current_weather_data.apparent_temperature,
                precipitation=current_weather_data.precipitation,
                wind_speed=current_weather_data.wind_speed,
                surface_pressure=current_weather_data.surface_pressure
            )
        )

    return {"predictions": predictions}
