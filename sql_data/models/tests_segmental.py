from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sql_data.config import Base
from datetime import datetime

class TestSegmental(Base):
    __tablename__ = 'tests_segmental'
    
    test_id = Column(Integer, ForeignKey('tests_primary.test_id'), primary_key=True)
    right_arm = Column(Float)
    left_arm = Column(Float)
    right_leg = Column(Float)
    left_leg = Column(Float)
    torso = Column(Float)
    creation_date = Column(DateTime, default=func.now())
    
    test = relationship('TestPrimary', back_populates='segmental')
