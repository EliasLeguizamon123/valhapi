from pydantic import BaseModel, constr
from typing_extensions import Annotated

class OperatorSettingsBase(BaseModel):
    measure: Annotated[str, constr(max_length=255)]  # Suponiendo longitud máxima arbitraria
    business: Annotated[str, constr(max_length=255)]  # Suponiendo longitud máxima arbitraria
    collation: Annotated[str, constr(max_length=255)]  # Suponiendo longitud máxima arbitraria
    company_name: Annotated[str, constr(max_length=50)]  

class OperatorSettingsCreate(OperatorSettingsBase):
    pass

class OperatorSettings(OperatorSettingsBase):
    class Config:
        orm_mode = True
