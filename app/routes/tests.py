from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import csv
from io import StringIO

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

@router.post("/{member_id}", response_model=TestResponse)
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

@router.get("/{member_id}/csv")
def get_tests_csv(member_id: str, db: Session = Depends(get_db)):
    tests = get_all_tests_of_member(db, member_id)
    if not tests:
        raise HTTPException(status_code=404, detail="No tests found for the specified member")

    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "Creation Date", "For", "By", "Gender", "Age", "Height", "Ohms", "Weight",
        "Body Fat", "Visceral Fat", "Muscle Mass", "Lean Mass", "Body Water", "BMI",
        "Left Arm", "Right Arm", "Left Leg", "Right Leg", "Torso",
        "Basal Metabolic Rate", "Very Light Activity", "Light Activity",
        "Moderate Activity", "Heavy Activity", "Very Heavy Activity"
    ])
    
    
    for test in tests:
        gender = "M" if test['test_primary'].gender == "1" else "F"
        formatted_date = test['test_primary'].creation_date.strftime('%Y-%m-%d')
        writer.writerow([
            formatted_date,
            test['test_primary'].from_field, 
            test['test_primary'].by_field,
            gender,
            test['test_primary'].age,
            test['test_primary'].height,
            test['test_primary'].bio_impedance,
            test['test_primary'].weight,
            test['test_primary'].body_fat,
            test['test_primary'].visceral_fat,
            test['test_primary'].muscle_mass,
            test['test_primary'].lean_mass,
            test['test_primary'].body_water,
            test['test_primary'].bmi,
            test['test_segmental'].left_arm,
            test['test_segmental'].right_arm,
            test['test_segmental'].left_leg,
            test['test_segmental'].right_leg,
            test['test_segmental'].torso,
            test['test_energy'].basal_metabolic_rate,
            test['test_energy'].very_light_activity,
            test['test_energy'].light_activity,
            test['test_energy'].moderate_activity,
            test['test_energy'].heavy_activity,
            test['test_energy'].very_heavy_activity
        ])
    
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=tests.csv"})



@router.delete("/{test_id}")
def delete_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(TestPrimaryModel).filter(TestPrimaryModel.test_id == test_id).first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    db.delete(test)
    db.commit()
    
    return {"message": "Test deleted successfully"}