import datetime
from datetime import timezone
from sqlalchemy import Column, Integer, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base

from src.serve.database import create_database_engine

Base = declarative_base()


class Prediction(Base):
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True)
    station_number = Column(Integer)
    n_future = Column(Integer)
    predictions = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Prediction {self.id}>'


Base.metadata.create_all(create_database_engine())