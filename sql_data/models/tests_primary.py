from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship
from sql_data.config import Base
from datetime import datetime

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
    creation_date = Column(DateTime, default=func.now())
    member_id = Column(Integer, ForeignKey('members.id'), unique=True, nullable=True)
    
    member = relationship('Member', back_populates='tests')
    energy = relationship('TestEnergy', back_populates='test', uselist=False)
    segmental = relationship('TestSegmental', back_populates='test', uselist=False)
