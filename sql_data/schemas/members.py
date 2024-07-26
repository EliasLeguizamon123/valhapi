from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MemberBase(BaseModel):
    first_name: str
    last_name: str
    age: int
    gender: str
    height: float
    weight: float
class MemberCreate(BaseModel):
    id: str
    first_name: str
    last_name: str
    age: int
    gender: str
    height: float
    weight: float


class Member(MemberBase):
    id: str
    creation_date: datetime
    update_date: Optional[datetime] = None

    class Config:
        orm_mode = True
