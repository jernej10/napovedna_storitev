import json
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from src.serve.database import create_database_engine
from src.serve.models.predicition import Prediction


class PredictionService:

    @staticmethod
    def save(station_number: int, n_future: int, predictions):

        predictions_dict = [prediction.dict() for prediction in predictions]
        predictions_json = json.dumps(predictions_dict)

        prediction = Prediction(
            station_number=station_number,
            n_future=n_future,
            predictions=predictions_json,
            created_at=datetime.now(timezone.utc)
        )

        Session = sessionmaker(bind=create_database_engine())
        session = Session()

        try:
            session.add(prediction)
            session.commit()
            return True
        except Exception as e:
            print(f"Error saving prediction: {e}")
            session.rollback()
            return False
        finally:
            session.close()