from sqlalchemy.orm import Session

from sql_data.schemas.core_software import CoreSoftware
from sql_data.models.core_software import CoreSoftware as CoreSoftwareModel

def get_pin(db: Session, pin: CoreSoftware.pin):
    return db.query(CoreSoftwareModel).filter(CoreSoftware.pin == pin).first()

def update_pin (db: Session, reset_pin: CoreSoftware.reset_pin, new_pin: CoreSoftware.pin):
    bd_reset_pin = db.query(CoreSoftwareModel).filter(CoreSoftware.reset_pin == reset_pin).first
    
    if reset_pin == bd_reset_pin:
        # Update pin
        db.query(CoreSoftwareModel).filter(CoreSoftware.reset_pin == reset_pin).update(new_pin)