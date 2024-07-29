from sqlalchemy.orm import Session

from datetime import datetime

from sql_data.schemas.tests_primary import TestPrimaryCreate
from sql_data.models.tests_primary import TestPrimary as TestPrimaryModel

from sql_data.schemas.tests_energy import TestEnergyCreate
from sql_data.models.tests_energy import TestEnergy as TestEnergyModel

from sql_data.schemas.tests_segmental import TestSegmentalCreate
from sql_data.models.tests_segmental import TestSegmental as TestSegmentalModel

from sql_data.models.members import Member

def get_all_tests_of_member(db: Session, member_id: int):
    return db.query(TestPrimaryModel).filter(TestPrimaryModel.member_id == member_id).all()

def create_test(db: Session, test_primary: TestPrimaryCreate, test_energy: TestEnergyCreate, test_segmental: TestSegmentalCreate):
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
        member_id=test_primary.member_id,
        creation_date=datetime.utcnow()
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
    
    # Confirmar los cambios
    db.commit()
    db.refresh(db_test_primary)
    
    return db_test_primary
