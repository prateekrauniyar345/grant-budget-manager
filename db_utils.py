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


# def get_db_session():
#     # Path to your SQLite file (in the project root)
#     # db_file = os.getenv("SQLITE_FILE", "demo.db")
#     db_file = "/Volumes/ORICO/classess/cs360/cs360-project/instance/grant_management.db"

#     # Use a SQLite URL; check_same_thread=False is needed if you’re re-using the session across threads
#     engine = create_engine(
#         f"sqlite:///{db_file}",
#         connect_args={"check_same_thread": False}
#     )

#     # Create a session factory
#     Session = sessionmaker(bind=engine)
#     return Session()