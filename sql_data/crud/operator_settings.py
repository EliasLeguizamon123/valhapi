from sqlalchemy.orm import Session
from sql_data.schemas.operator_settings import OperatorSettings, OperatorSettingsCreate
from sql_data.models.operator_settings import OperatorSettings as OperatorSettingsModel

def get_operator_settings(db: Session):
    return db.query(OperatorSettingsModel).first()

def create_or_update_operator_settings(db: Session, operator_settings: OperatorSettingsCreate):
    db_operator_settings = db.query(OperatorSettingsModel).first()
    if db_operator_settings:
        for key, value in operator_settings.dict().items():
            setattr(db_operator_settings, key, value)
        db.commit()
        db.refresh(db_operator_settings)
    else:
        db_operator_settings = OperatorSettingsModel(**operator_settings.dict(), id=1)
        db.add(db_operator_settings)
        db.commit()
        db.refresh(db_operator_settings)
    return db_operator_settings
