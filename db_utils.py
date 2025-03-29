# db_utils.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_session():
    # Database connection details
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    database = os.getenv("DB_NAME")

    # Create the SQLAlchemy engine
    engine = create_engine(f"mysql+mysqlconnector://{username}:{password}@{host}/{database}")

    # Create a session factory
    Session = sessionmaker(bind=engine)
    return Session()