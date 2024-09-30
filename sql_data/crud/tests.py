from sqlalchemy.orm import Session

from datetime import datetime

from sql_data.schemas.tests_primary import TestPrimaryCreate
from sql_data.models.tests_primary import TestPrimary as TestPrimaryModel

from sql_data.schemas.tests_energy import TestEnergyCreate
from sql_data.models.tests_energy import TestEnergy as TestEnergyModel

from sql_data.schemas.tests_segmental import TestSegmentalCreate
from sql_data.models.tests_segmental import TestSegmental as TestSegmentalModel


def get_all_tests_of_member(db: Session, member_id: str):
    results = db.query(TestPrimaryModel).filter(TestPrimaryModel.member_id == member_id).all()
    response = []

    for test in results:
        # Obtener datos relacionados de test_energy y test_segmental
        test_energy = db.query(TestEnergyModel).filter(TestEnergyModel.test_id == test.test_id).first()
        test_segmental = db.query(TestSegmentalModel).filter(TestSegmentalModel.test_id == test.test_id).first()

        # Si no se encuentra, crear un objeto vacío por defecto
        if not test_energy:
            test_energy = TestEnergyModel(
                test_id=test.test_id,
                basal_metabolic_rate=0,
                very_light_activity=0,
                light_activity=0,
                moderate_activity=0,
                heavy_activity=0,
                very_heavy_activity=0,
                creation_date=datetime.utcnow()
            )

        if not test_segmental:
            test_segmental = TestSegmentalModel(
                test_id=test.test_id,
                right_arm=0,
                left_arm=0,
                right_leg=0,
                left_leg=0,
                torso=0,
                creation_date=datetime.utcnow()
            )

        response.append({
            "test_primary": test,
            "test_energy": test_energy,
            "test_segmental": test_segmental,
        })

    return response


def create_test(db: Session, test_primary: TestPrimaryCreate, test_energy: TestEnergyCreate, test_segmental: TestSegmentalCreate):
    
    print('creo un test nuevo', test_primary)
    
    # Crear TestPrimary
    db_test_primary = TestPrimaryModel(
        body_fat=test_primary.body_fat,
        bio_impedance=test_primary.bio_impedance,
        visceral_fat=test_primary.visceral_fat,
        lean_mass=test_primary.lean_mass,
        muscle_mass=test_primary.muscle_mass,
        body_water=test_primary.body_water,
        bmi=test_primary.bmi,
        weight=test_primary.weight,
        height=test_primary.height,
        age=test_primary.age,
        member_id=test_primary.member_id,
        creation_date=datetime.utcnow(),
        from_field=test_primary.from_field,
        by_field=test_primary.by_field,
        aiw=test_primary.aiw,
        gender=test_primary.gender,
        lean_mass_percent=test_primary.lean_mass_percent,
        body_water_percent=test_primary.body_water_percent,
        body_fat_percent=test_primary.body_fat_percent,
    )
    db.add(db_test_primary)
    db.commit()
    db.refresh(db_test_primary)
    
    # Crear TestEnergy
    db_test_energy = TestEnergyModel(
        test_id=db_test_primary.test_id,
        basal_metabolic_rate=test_energy.basal_metabolic_rate,
        very_light_activity=test_energy.very_light_activity,
        light_activity=test_energy.light_activity,
        moderate_activity=test_energy.moderate_activity,
        heavy_activity=test_energy.heavy_activity,
        very_heavy_activity=test_energy.very_heavy_activity,
        creation_date=test_primary.creation_date
    )
    db.add(db_test_energy)
    
    # Crear TestSegmental
    db_test_segmental = TestSegmentalModel(
        test_id=db_test_primary.test_id,
        right_arm=test_segmental.right_arm,
        left_arm=test_segmental.left_arm,
        right_leg=test_segmental.right_leg,
        left_leg=test_segmental.left_leg,
        torso=test_segmental.torso,
        creation_date=test_primary.creation_date
    )
    db.add(db_test_segmental)
    
    db.commit()
    
    db.refresh(db_test_primary)
    db.refresh(db_test_energy)
    db.refresh(db_test_segmental)
    
    return {
        "test_primary": db_test_primary,
        "test_energy": db_test_energy,
        "test_segmental": db_test_segmental
    }

def delete_test(db: Session, test_id: int):
    db.query(TestPrimaryModel).filter(TestPrimaryModel.test_id == test_id).delete()
    db.commit()
    return True