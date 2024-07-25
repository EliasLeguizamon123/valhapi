from sql_data.config import Base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

class Member(Base):
    __tablename__ = 'members'
    
    id = Column(String, primary_key=True, index=True, max_length=10)
    first_name = Column(String, max_length=50)
    last_name = Column(String, max_length=50)
    age = Column(Integer, max_length=2, min_length=1, min=1)
    gender = Column(String, max_length=6)
    height = Column(Float, min_length=1, min=1, max_length=4)
    weight = Column(Float, min_length=1, min=1, max_length=4)
    
    tests = relationship('TestPrimary', back_populates='member')