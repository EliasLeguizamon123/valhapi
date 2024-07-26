from sqlalchemy.orm import Session
from sql_data.schemas.operator_settings import OperatorSettings
from sql_data.models.operator_settings import OperatorSettings as OperatorSettingsModel

def get_operator_settings(db: Session): 
    db_operator_settings = db.query(OperatorSettingsModel).first()
    return db_operator_settings

def update_operator_settings(db: Session, operator_settings: OperatorSettings):
    db.add(operator_settings)
    db.commit()
    db.refresh(operator_settings)
    return operator_settings