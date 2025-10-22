# db_utils.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_session():
    """
    Create a database session using TiDB cloud connection.
    This ensures all parts of the application use the same cloud database.
    """
    # Use TiDB cloud database connection string
    tidb_url = os.getenv("TiDB_CONNECTION_STRING")
    
    if not tidb_url:
        raise ValueError("TiDB_CONNECTION_STRING not found in environment variables!")
    
    # Create the SQLAlchemy engine with TiDB cloud
    engine = create_engine(
        tidb_url,
        pool_pre_ping=True,      # Verify connections before using
        pool_recycle=3600,       # Recycle connections after 1 hour
        pool_size=5,             # Connection pool size
        max_overflow=10          # Maximum overflow connections
    )

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