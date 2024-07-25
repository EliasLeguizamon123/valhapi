from pydantic import BaseModel, condecimal
from typing_extensions import Annotated

class TestEnergyBase(BaseModel):
    test_id: int
    basal_metabolic_rate: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    very_light_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    light_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    moderate_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    heavy_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    very_heavy_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  

class TestEnergyCreate(BaseModel):
    basal_metabolic_rate: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    very_light_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    light_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    moderate_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    heavy_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  
    very_heavy_activity: Annotated[float, condecimal(max_digits=6, decimal_places=2)]  

class TestEnergy(TestEnergyBase):
    class Config:
        orm_mode = True
