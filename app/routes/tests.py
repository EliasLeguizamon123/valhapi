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

@router.post("/{member_id}", response_model=TestPrimary)
def create_member_test(
    member_id: str, 
    test_primary: TestPrimaryCreate, 
    test_energy: TestEnergyCreate, 
    test_segmental: TestSegmentalCreate, 
    db: Session = Depends(get_db)
):
    try:
        # Asignar el member_id del parámetro de ruta al objeto test_primary
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
        "Test ID", "Member ID", "Body Fat", "Bio Impedance", "Visceral Fat",
        "Lean Mass", "Muscle Mass", "Body Water", "BMI", "Weight",
        "From", "By",
        "Basal Metabolic Rate", "Very Light Activity", "Light Activity",
        "Moderate Activity", "Heavy Activity", "Very Heavy Activity",
        "Right Arm", "Left Arm", "Right Leg", "Left Leg", "Torso"
    ])
    
    for test in tests:
        writer.writerow([
            test['test_primary'].test_id, test['test_primary'].member_id,
            test['test_primary'].body_fat, test['test_primary'].bio_impedance,
            test['test_primary'].visceral_fat, test['test_primary'].lean_mass,
            test['test_primary'].muscle_mass, test['test_primary'].body_water,
            test['test_primary'].bmi, test['test_primary'].weight,
            test['test_primary'].from_field,
            test['test_primary'].by_field,
            test['test_energy'].basal_metabolic_rate,
            test['test_energy'].very_light_activity,
            test['test_energy'].light_activity,
            test['test_energy'].moderate_activity,
            test['test_energy'].heavy_activity,
            test['test_energy'].very_heavy_activity,
            test['test_segmental'].right_arm, test['test_segmental'].left_arm,
            test['test_segmental'].right_leg, test['test_segmental'].left_leg,
            test['test_segmental'].torso
        ])
    
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=tests.csv"})
