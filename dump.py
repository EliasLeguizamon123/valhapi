from sqlalchemy.orm import Session
from sql_data.config import SessionLocal
from sql_data.models.core_software import CoreSoftwareModel

def init_db(db: Session):
    if db.query(CoreSoftwareModel).first() is None:
        default_pin = 8888
        default_reset_pin = 1235
        core_software = CoreSoftwareModel(pin=default_pin, reset_pin=default_reset_pin)
        db.add(core_software)
        db.commit()
        db.refresh(core_software)
        
def initialize_data():
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()