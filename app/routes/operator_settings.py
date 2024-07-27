from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_data.schemas.operator_settings import OperatorSettings, OperatorSettingsCreate
from sql_data.models.operator_settings import OperatorSettings as OperatorSettingsModel
from sql_data.config import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/", response_model=OperatorSettings)
def get_operator_settings(db: Session = Depends(get_db)):
    operator_settings = db.query(OperatorSettingsModel).first()
    if operator_settings is None:
        raise HTTPException(status_code=404, detail="Operator settings not found")
    return operator_settings
    
@router.post("/", response_model=OperatorSettings)
def create_or_update_operator_settings(operator_settings: OperatorSettingsCreate, db: Session = Depends(get_db)):
    db_operator_settings = db.query(OperatorSettingsModel).first()
    if db_operator_settings:
        for key, value in operator_settings.dict().items():
            setattr(db_operator_settings, key, value)
        db.commit()
        db.refresh(db_operator_settings)
        return db_operator_settings
    else:
        new_operator_settings = OperatorSettingsModel(**operator_settings.dict())
        db.add(new_operator_settings)
        db.commit()
        db.refresh(new_operator_settings)
        return new_operator_settings