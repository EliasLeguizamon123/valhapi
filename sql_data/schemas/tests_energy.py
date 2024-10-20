from pydantic import BaseModel, condecimal
from typing_extensions import Annotated
from datetime import datetime

class TestEnergyBase(BaseModel):
    basal_metabolic_rate: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    very_light_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    light_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    moderate_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    heavy_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    very_heavy_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]

class TestEnergyCreate(TestEnergyBase):
    pass

class TestEnergy(TestEnergyBase):
    test_id: int
    creation_date: datetime

    class Config:
        from_attributes = True
