from sql_data.config import Base
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Member(Base):
    __tablename__ = 'members'
    
    id = Column(String(10), primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    age = Column(Integer)
    gender = Column(String(6))
    height = Column(Float)
    weight = Column(Float)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())
    update_date = Column(DateTime(timezone=True), onupdate=func.now())

    tests = relationship('TestPrimary', back_populates='member')
