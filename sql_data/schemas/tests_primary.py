from pydantic import BaseModel, condecimal
from datetime import datetime
from typing_extensions import Annotated

class TestPrimaryBase(BaseModel):
    body_fat: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    bio_impedance: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    visceral_fat: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    lean_mass: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    muscle_mass: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    body_water: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    bmi: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    weight: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    creation_date: datetime
    member_id: int

class TestPrimaryCreate(TestPrimaryBase):
    pass

class TestPrimary(TestPrimaryBase):
    test_id: int

    class Config:
        orm_mode = True
