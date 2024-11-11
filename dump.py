from sqlalchemy.orm import Session
from sql_data.config import SessionLocal
from sql_data.models.core_software import CoreSoftwareModel
from sql_data.models.operator_settings import OperatorSettings

def init_db(db: Session):
    if db.query(CoreSoftwareModel).first() is None:
        default_pin = 8888
        default_reset_pin = 1235
        core_software = CoreSoftwareModel(pin=default_pin, reset_pin=default_reset_pin)
        db.add(core_software)
        db.commit()
        db.refresh(core_software)
    
    if db.query(OperatorSettings).first() is None:
        operator_settings = OperatorSettings(
            measure='Imperial',
            business='Medical',
            collation='Tray',
            company_name='',
            selected_printer='',
            includes = """{"body_fat": true,"weight": true,"basal_metabolic_rate": true,"bio_impedance": true,"visceral_fat": true,"muscle_mass": true,"lean_mass": true,"body_water": true,"bmi": true,"activity_section": true,"segmental_section": true}""",
            com='COM3',
            test2=False,
            test3=False,
            test4=False,
            test5=False
        )
        db.add(operator_settings)
        db.commit()
        db.refresh(operator_settings)
        
        
def initialize_data():
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()