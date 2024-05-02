import json
import os
import dagshub
import dagshub.auth as dh_auth

import numpy as np
from sqlalchemy.orm import sessionmaker

from src.serve.database import create_database_engine
from src.serve.models.predicition import Prediction
from dagshub.data_engine.datasources import mlflow
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


def main():
    dh_auth.add_app_token(token=os.getenv("DAGSHUB_TOKEN"))
    dagshub.init('napovedna_storitev', 'jernej10', mlflow=True)
    mlflow.set_tracking_uri('https://dagshub.com/jernej10/napovedna_storitev.mlflow')

    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    all_predictions = session.query(Prediction).all()

    #dm = DataManager(data_path="data/processed")

    numbers = [f for f in os.listdir("data/processed") if os.path.isdir(f"data/processed/{f}")]

    for n in numbers:
        mlflow.start_run(run_name=f"validate_productions_mbajk_station_{n}", experiment_id="1")

        print(f"Station: {n}")
        #station = dm.get_dataframe(folder=n, file_name=f"mbajk_station_{n}")
        station = pd.read_csv(f"data/processed/{n}/mbajk_station_{n}.csv")

        errors = []
        for pred in all_predictions:
            prediction_list = json.loads(pred.predictions)
            for p in prediction_list:
                prediction = p["prediction"]
                date = p["date"].replace("T", " ")

                row = station.loc[station["date"] == date]
                if row.empty:
                    print(f"Prediction for date {date} not found")
                    continue

                actual = row["available_bike_stands"].values[0]
                error = actual - prediction
                errors.append(error)

                print(f"Prediction: {prediction}, Actual: {actual}, Error: {error}")

        mean_error = np.mean(errors)
        print(f"Mean Error: {mean_error}")
        mean_squared_error = np.mean(np.square(errors))
        print(f"Mean Squared Error: {mean_squared_error}")

        mlflow.log_metric("Mean Error", mean_error)
        mlflow.log_metric("Mean Squared Error", mean_squared_error)

        mlflow.end_run()


if __name__ == '__main__':
    main()