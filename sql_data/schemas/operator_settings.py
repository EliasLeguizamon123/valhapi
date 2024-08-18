# sql_data/schemas/operator_settings.py
from pydantic import BaseModel, constr
from typing_extensions import Annotated

class OperatorSettingsBase(BaseModel):
    measure: Annotated[str, constr(max_length=50)]
    business: Annotated[str, constr(max_length=50)]
    collation: Annotated[str, constr(max_length=50)]
    company_name: Annotated[str, constr(max_length=60)]
    selected_printer: Annotated[str, constr(max_length=50)] = None

class OperatorSettingsCreate(OperatorSettingsBase):
    pass

class OperatorSettings(OperatorSettingsBase):
    id: int  

    class Config:
        from_attributes = True
