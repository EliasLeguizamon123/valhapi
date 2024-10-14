from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from datetime import datetime
import serial
import re

from sql_data.schemas.tests_primary import TestPrimaryCreate, TestPrimary
from sql_data.schemas.tests_energy import TestEnergyCreate
from sql_data.schemas.tests_segmental import TestSegmentalCreate
from sql_data.models.tests_primary import TestPrimary as TestPrimaryModel
from sql_data.models.tests_energy import TestEnergy as TestEnergyModel
from sql_data.models.tests_segmental import TestSegmental as TestSegmentalModel
from sql_data.crud.tests import create_test
from sql_data.crud.members import get_member
from sql_data.config import SessionLocal



router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/get_results")
def get_results(com: str, db: Session = Depends(get_db)):
    try:
        serial_port = serial.Serial(com, 115200, timeout=40)
        serial_data = ""

        while True:
            line = serial_port.readline().decode('utf-8').strip()
            if line.startswith("#START"):
                serial_data = ""
                continue
            elif line.startswith("#END"):
                break
            serial_data += line + "\n"

        serial_port.close()
        
        print(serial_data)

        data = process_serial_data(serial_data)
        
        if not data:
            return {"error": "Failed to parse serial data"}

        test_primary = TestPrimaryCreate(
            body_fat=data['body_fat'],
            body_fat_percent=data['body_fat_percent'],
            bio_impedance=data['bio_impedance'],
            visceral_fat=data['visceral_fat'],
            lean_mass=data['lean_mass'],
            lean_mass_percent=data['lean_mass_percent'],
            muscle_mass=data['muscle_mass'],
            body_water=data['body_water'],
            body_water_percent=data['body_water_percent'],
            bmi=data['bmi'],
            weight=data['weight'],
            height=data['height'],
            aiw=data['aiw'],
            age=data['age'],
            gender=int(data['gender']),
            from_field=data['from_field'],
            by_field=data['by_field'],
            member_id=data['from_field'] or None,
            creation_date=datetime.utcnow()
        )
        
        test_energy = TestEnergyCreate(
            basal_metabolic_rate=data['basal_metabolic_rate'],
            very_light_activity=data['very_light_activity'],
            light_activity=data['light_activity'],
            moderate_activity=data['moderate_activity'],
            heavy_activity=data['heavy_activity'],
            very_heavy_activity=data['very_heavy_activity']
        )

        test_segmental = TestSegmentalCreate(
            right_arm=data['right_arm'],
            left_arm=data['left_arm'],
            right_leg=data['right_leg'],
            left_leg=data['left_leg'],
            torso=data['torso']
        )

        new_test = create_test(db, test_primary, test_energy, test_segmental)
        
        print('Test created', new_test)
        return new_test
    except serial.SerialException as e:
        raise HTTPException(status_code=404, detail="serial port COM3 not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

def process_serial_data(data: str) -> Dict:
    values = {}
    feet, inches, cm = None, None, None

    for line in data.split('\n'):
        if line.startswith("#START"):
            continue
        if ',' in line:
            key, value = line.split(',', 1)
            key = key.strip()
            value = value.strip()
            
            clean_value = re.sub(r'[^\d.]+', '', value)
            
            try:
                if key == "Weight(lb)":
                    values['weight'] = float(clean_value)
                elif key == "Weight(kg)":
                    values['weight_kg'] = float(clean_value)
                elif key == "Hgt Ft":
                    feet = clean_value
                elif key == "Hgt In":
                    inches = clean_value
                elif key == "Hgt(cm)":
                    cm = clean_value
                elif key == "BF(kg)":
                    values['body_fat'] = float(clean_value)
                elif key == "BF(%)":
                    values['body_fat_percent'] = float(clean_value)
                elif key == "Ohms":
                    values['bio_impedance'] = float(clean_value)
                elif key == "VF(#)":
                    values['visceral_fat'] = float(clean_value)
                elif key == "FFM(kg)":
                    values['lean_mass'] = float(clean_value)
                elif key == "FFM(%)":
                    values['lean_mass_percent'] = float(clean_value)
                elif key == "TBW(kg)":
                    values['body_water'] = float(clean_value)
                elif key == "TBW(%)":
                    values['body_water_percent'] = float(clean_value)
                elif key == "BMI":
                    values['bmi'] = float(clean_value)
                elif key == "MM(lb)":
                    values['muscle_mass'] = float(clean_value)
                elif key == "TR(lb)":
                    values['torso'] = float(clean_value)
                elif key == "TR(%)":
                    values['torso_percent'] = float(clean_value)
                elif key == "LL(lb)":
                    values['left_leg'] = float(clean_value)
                elif key == "LL(%)":
                    values['left_leg_percent'] = float(clean_value)
                elif key == "RL(lb)":
                    values['right_leg'] = float(clean_value)
                elif key == "RL(%)":
                    values['right_leg_percent'] = float(clean_value)
                elif key == "LA(lb)":
                    values['left_arm'] = float(clean_value)
                elif key == "LA(%)":
                    values['left_arm_percent'] = float(clean_value)
                elif key == "RA(lb)":
                    values['right_arm'] = float(clean_value)
                elif key == "RA(%)":
                    values['right_arm_percent'] = float(clean_value)
                elif key == "BMR" or key == "REE":
                    values['basal_metabolic_rate'] = float(clean_value)
                elif key == "DCN(VL)":
                    values['very_light_activity'] = float(clean_value)
                elif key == "DCN(L)":
                    values['light_activity'] = float(clean_value)
                elif key == "DCN(M)":
                    values['moderate_activity'] = float(clean_value)
                elif key == "DCN(H)":
                    values['heavy_activity'] = float(clean_value)
                elif key == "DCN(VH)":
                    values['very_heavy_activity'] = float(clean_value)
                elif key == "AIW(%)":
                    values['aiw'] = float(clean_value)
                elif key == "Provider ID":
                    values['from_field'] = clean_value
                elif key == "Patient ID":
                    values['by_field'] = clean_value
                elif key == "Gender":
                    values['gender'] = int(clean_value)
                elif key == "Age":
                    values['age'] = int(clean_value)
            except ValueError:
                values[key] = value

    if feet is not None and inches is not None and cm is not None:
        values['height'] = f"{feet}' {inches}\" {cm}cm"
    
    return values
