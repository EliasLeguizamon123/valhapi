import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Place database in %APPDATA%/Valhalla/database.db
appdata_path = os.getenv('APPDATA')
database_path = os.path.join(appdata_path, 'Valhalla', 'database.db')
database_uri = f'sqlite:///{database_path}'

# Create directory if it doesn't exist
os.makedirs(os.path.dirname(database_path), exist_ok=True)

# Create engine without SQLCipher
engine = create_engine(
    database_uri,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base
Base = declarative_base()
