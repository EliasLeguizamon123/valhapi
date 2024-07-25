from pydantic import BaseModel, condecimal
from datetime import datetime
from typing_extensions import Annotated

class TestPrimaryBase(BaseModel):
    test_id: int
    body_fat: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    bio_impedance: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    visceral_fat: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    lean_mass: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    muscle_mass: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    body_water: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    bmi: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    weight: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    creation_date: datetime  
    updated_date: datetime  

class TestPrimaryCreate(BaseModel):
    body_fat: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    bio_impedance: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    visceral_fat: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    lean_mass: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    muscle_mass: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    body_water: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    bmi: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  
    weight: Annotated[float, condecimal(max_digits=5, decimal_places=2)]  

class TestPrimary(TestPrimaryBase):
    class Config:
        orm_mode = True
