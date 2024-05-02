import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def create_database_engine(echo: bool = False):
    engine = create_engine(os.getenv('DATABASE_URI'), echo=echo)
    return engine