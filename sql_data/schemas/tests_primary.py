from pydantic import BaseModel, condecimal, constr
from datetime import datetime
from typing_extensions import Annotated
from typing import Optional

from sql_data.schemas.tests_energy import TestEnergy
from sql_data.schemas.tests_segmental import TestSegmental

class TestPrimaryBase(BaseModel):
    body_fat: Annotated[float, condecimal(max_digits=5, decimal_places=2)]
    bio_impedance: Annotated[float, condecimal(max_digits=5, decimal_places=2)]
    visceral_fat: Annotated[float, condecimal(max_digits=5, decimal_places=2)] 
    lean_mass: Annotated[float, condecimal(max_digits=5, decimal_places=2)]
    muscle_mass: Annotated[float, condecimal(max_digits=5, decimal_places=2)]
    body_water: Annotated[float, condecimal(max_digits=5, decimal_places=2)] 
    bmi: Annotated[float, condecimal(max_digits=5, decimal_places=2)]
    weight: Annotated[float, condecimal(max_digits=5, decimal_places=2)]
    height: Optional[str] = None
    age: Optional[int] = None
    ohms: Annotated[float, condecimal(max_digits=5, decimal_places=2)]
    from_field: Optional[str] = None
    by_field: Optional[str] = None
    aiw: Optional[float] = None

class TestPrimaryCreate(TestPrimaryBase):
    creation_date: Optional[datetime] = None
    member_id: Optional[str] = None 
    pass

class TestPrimary(TestPrimaryBase):
    test_id: int
    creation_date: datetime

    class Config:
        from_attributes = True


class TestResponse(BaseModel):
    test_primary: TestPrimary
    test_energy: TestEnergy
    test_segmental: TestSegmental