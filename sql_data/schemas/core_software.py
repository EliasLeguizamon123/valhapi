from pydantic import BaseModel, constr
from typing_extensions import Annotated

class CoreSoftwareBase(BaseModel):
    pin: Annotated[str, constr(max_length=4)]  
    reset_pin: Annotated[str, constr(max_length=4)]  

class CoreSoftwareCreate(CoreSoftwareBase):
    pass

class CoreSoftware(CoreSoftwareBase):
    class Config:
        from_attributes = True
