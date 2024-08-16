from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from sql_data.schemas.core_software import CoreSoftware, CoreSoftwareCreate
from sql_data.models.core_software import CoreSoftwareModel
from sql_data.config import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/pin", response_model=CoreSoftware)
def get_pin(db: Session = Depends(get_db)):
    try:
        core_software = db.query(CoreSoftwareModel).first()
        if core_software is None:
            raise HTTPException(status_code=404, detail="PIN not found")
        return core_software
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/reset_pin", response_model=CoreSoftware)
def reset_pin(new_pin: CoreSoftwareCreate, db: Session = Depends(get_db)):
    try:
        core_software = db.query(CoreSoftwareModel).first()
        if core_software is None:
            raise HTTPException(status_code=404, detail="Reset PIN not found")
        if core_software.reset_pin != new_pin.reset_pin:
            raise HTTPException(status_code=400, detail="Incorrect reset PIN")
        
        core_software.pin = new_pin.pin
        db.commit()
        db.refresh(core_software)
        return core_software
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
