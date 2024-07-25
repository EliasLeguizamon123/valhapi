from pydantic import BaseModel, constr, conint
from typing_extensions import Annotated
from datetime import datetime

class MemberBase(BaseModel):
    id: Annotated[str, constr(max_length=10)]  
    first_name: Annotated[str, constr(max_length=50)]  
    last_name: Annotated[str, constr(max_length=50)]  
    age: Annotated[int, conint(ge=1, le=99)]  
    gender: Annotated[str, constr(max_length=6)]  
    height: Annotated[float, conint(ge=0, le=999.9)]
    weight: Annotated[float, conint(ge=0, le=999.9)]
    creation_date: datetime  
    update_date: datetime  

class MemberCreate(BaseModel):
    id: Annotated[str, constr(max_length=10)]
    first_name: Annotated[str, constr(max_length=50)]
    last_name: Annotated[str, constr(max_length=50)]
    age: Annotated[int, conint(ge=1, le=99)] 
    gender: Annotated[str, constr(max_length=6)]
    height: Annotated[float, conint(ge=0, le=999.9)]
    weight: Annotated[float, conint(ge=0, le=999.9)]

class Member(MemberBase):
    class Config:
        orm_mode = True
