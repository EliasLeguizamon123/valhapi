from pydantic import BaseModel, condecimal
from typing_extensions import Annotated
from datetime import datetime

class TestSegmentalBase(BaseModel):
    right_arm: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    left_arm: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    right_leg: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    left_leg: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    torso: Annotated[float, condecimal(max_digits=6, decimal_places=2)]

class TestSegmentalCreate(TestSegmentalBase):
    pass

class TestSegmental(TestSegmentalBase):
    test_id: int
    creation_date: datetime

    class Config:
        from_attributes = True
