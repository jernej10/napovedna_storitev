import os

import joblib
import numpy as np
import pandas as pd
from keras import Sequential
from keras.layers import Dense, GRU, Dropout, Input
from keras.src.layers import LSTM
from sklearn.metrics import mean_squared_error, mean_absolute_error, explained_variance_score
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple
import tensorflow_model_optimization as tfmot
import tf_keras
from tensorflow_model_optimization.python.core.quantization.keras.default_8bit import default_8bit_quantize_scheme

window_size = 2

def build_model(input_shape: tuple[int, int]) -> tf_keras.Sequential:
        quantize_annotate_layer = tfmot.quantization.keras.quantize_annotate_layer

        model = tf_keras.Sequential(name="GRU")

        model.add(tf_keras.Input(shape=input_shape))
        model.add(tf_keras.layers.GRU(units=128, return_sequences=True))
        model.add(tf_keras.layers.Dropout(0.2))

        model.add(tf_keras.layers.GRU(units=64, return_sequences=True))
        model.add(tf_keras.layers.Dropout(0.2))

        model.add(tf_keras.layers.GRU(units=32))

        model.add(quantize_annotate_layer(tf_keras.layers.Dense(units=32, activation="relu")))
        model.add(quantize_annotate_layer(tf_keras.layers.Dense(units=1)))

        optimizer = tf_keras.optimizers.legacy.Adam(learning_rate=0.01)

        model = tfmot.quantization.keras.quantize_apply(
            model,
            scheme=default_8bit_quantize_scheme.Default8BitQuantizeScheme(),
            quantized_layer_name_prefix='quant_'
        )

        model.compile(optimizer=optimizer, loss="mean_squared_logarithmic_error")

        return model


def train_model(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray, scaler: MinMaxScaler or None,
                build_model_fn, epochs: int = 10, batch_size=64,
                verbose: int = 1) -> Sequential:
    model = build_model_fn((X_train.shape[1], X_train.shape[2]))
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, y_test), verbose=verbose)

    return model


def evaluate_model_performance(y_true, y_pred, dataset, scaler):
    y_true_copy = np.repeat(y_true, dataset.shape[1], axis=-1)
    y_true = scaler.inverse_transform(np.reshape(y_true_copy, (len(y_true), dataset.shape[1])))[:, 0]

    prediction_copy = np.repeat(y_pred, dataset.shape[1], axis=-1)
    prediction = scaler.inverse_transform(np.reshape(prediction_copy, (len(y_pred), dataset.shape[1])))[:, 0]

    mse = mean_squared_error(y_true, prediction)
    mae = mean_absolute_error(y_true, prediction)
    evs = explained_variance_score(y_true, prediction)

    return mse, mae, evs


def save_model(model: Sequential, scaler: MinMaxScaler, station_number: int, model_name: str, scaler_name: str, folder_name: str) -> None:
    #older_name = f"../../models/station_{station_number}"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    joblib.dump(scaler, f"{folder_name}/{scaler_name}_scaler.gz")
    model.save(f"{folder_name}/{model_name}.keras")


def prepare_model_data(dataset: pd.DataFrame, scaler: MinMaxScaler or None):
    train_data, test_data = create_test_train_split(dataset)
    #train_data, test_data = scale_data(scaler, train_data, test_data)
    X_train, y_train = create_multivariate_time_series(train_data, window_size)
    X_test, y_test = create_multivariate_time_series(test_data, window_size)

    return X_train, y_train, X_test, y_test

def prepare_validation_model_data(dataset: pd.DataFrame, scaler: MinMaxScaler):
    # Predpostavimo, da imate testne podatke ločene v dataset, zato jih ne potrebujemo deliti na učne in testne podatke
    scaled_data = scale_test_data(scaler, dataset)  # Skaliramo podatke
    X, y = create_multivariate_time_series(scaled_data, window_size)  # Ustvarimo multivariatni časovni niz

    return X, y

def scale_data(scaler: MinMaxScaler, train_data: pd.DataFrame, test_data: pd.DataFrame) \
        -> Tuple[pd.DataFrame, pd.DataFrame]:
    train_data = scaler.fit_transform(train_data)
    test_data = scaler.transform(test_data)
    return train_data, test_data

def scale_test_data(scaler: MinMaxScaler, test_data: pd.DataFrame) \
        -> Tuple[pd.DataFrame, pd.DataFrame]:
    test_data = scaler.transform(test_data)
    return test_data

def create_test_train_split(dataset: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    test_split = round(len(dataset) * 0.2)
    train_data = dataset[:-test_split]
    test_data = dataset[-test_split:]

    return train_data, test_data

def create_multivariate_time_series(data, window_size):
    X, y = [], []
    for i in range(window_size, len(data)):
            X.append(data[i - window_size:i, 0:data.shape[1]])
            y.append(data[i,0])
    return np.array(X), np.array(y)