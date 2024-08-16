from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String
from sqlalchemy.orm import relationship
from sql_data.config import Base
from sqlalchemy.sql import func

class TestPrimary(Base):
    __tablename__ = 'tests_primary'
    
    test_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    body_fat = Column(Float)
    bio_impedance = Column(Float)
    visceral_fat = Column(Float)
    lean_mass = Column(Float)
    muscle_mass = Column(Float)
    body_water = Column(Float)
    bmi = Column(Float)
    weight = Column(Float)
    creation_date = Column(DateTime, server_default=func.now())
    member_id = Column(String, ForeignKey('members.id'), nullable=True)
    from_field = Column(String(60)) 
    by_field = Column(String(60))  
    
    member = relationship('Member', back_populates='tests')
    energy = relationship('TestEnergy', back_populates='test', uselist=False)
    segmental = relationship('TestSegmental', back_populates='test', uselist=False)
