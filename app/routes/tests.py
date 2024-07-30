from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from sql_data.schemas.tests_primary import TestPrimary, TestPrimaryCreate
from sql_data.models.tests_primary import TestPrimary as TestPrimaryModel

from sql_data.schemas.tests_energy import TestEnergy, TestEnergyCreate
from sql_data.models.tests_energy import TestEnergy as TestEnergyModel

from sql_data.schemas.tests_segmental import TestSegmental, TestSegmentalCreate
from sql_data.models.tests_segmental import TestSegmental as TestSegmentalModel

from sql_data.schemas.tests_primary import TestResponse

from sql_data.crud.tests import get_all_tests_of_member, create_test 

from sql_data.config import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@router.get("/{member_id}", response_model=List[TestResponse])
def read_tests(member_id: str, db: Session = Depends(get_db)):
    tests = get_all_tests_of_member(db, member_id)
    if not tests:
        raise HTTPException(status_code=404, detail="No tests found for the specified member")
    return tests

@router.post("/{member_id}", response_model=TestPrimary)
def create_member_test(
    member_id: str, 
    test_primary: TestPrimaryCreate, 
    test_energy: TestEnergyCreate, 
    test_segmental: TestSegmentalCreate, 
    db: Session = Depends(get_db)
):
    try:
        test_primary.member_id = member_id
        test_primary.creation_date = datetime.utcnow()

        new_test = create_test(db, test_primary, test_energy, test_segmental)
        return new_test
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
