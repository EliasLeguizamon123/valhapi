from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MemberBase(BaseModel):
    first_name: str
    last_name: str
   
class MemberCreate(BaseModel):
    id: str
    first_name: str
    last_name: str


class Member(MemberBase):
    id: str
    creation_date: datetime
    update_date: Optional[datetime] = None

    class Config:
        from_attributes = True
