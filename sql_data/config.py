import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Place database in %APPDATA%/Valhalla/database.db
appdata_path = os.getenv('APPDATA')
database_path = os.path.join(appdata_path, 'Valhalla', 'database.db')
database_uri = f'sqlcipher:///{database_path}'

# Create directory if it doesn't exist
os.makedirs(os.path.dirname(database_path), exist_ok=True)

# Encryption key
encryption_key = 'valhapi2024.'

# Create engine with SQLCipher
engine = create_engine(
    database_uri,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool
)

# Set the encryption key for SQLCipher
@event.listens_for(engine, 'connect')
def set_sqlcipher_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute(f"PRAGMA key='{encryption_key}'")
    cursor.close()

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base
Base = declarative_base()
