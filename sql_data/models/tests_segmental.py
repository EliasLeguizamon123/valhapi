from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sql_data.config import Base
from sqlalchemy.sql import func

class TestSegmental(Base):
    __tablename__ = 'tests_segmental'
    
    test_id = Column(Integer, ForeignKey('tests_primary.test_id', ondelete='CASCADE'), primary_key=True)
    right_arm = Column(Float)
    left_arm = Column(Float)
    right_leg = Column(Float)
    left_leg = Column(Float)
    torso = Column(Float)
    right_arm_percent = Column(Float, nullable=True)
    left_arm_percent = Column(Float, nullable=True)
    right_leg_percent = Column(Float, nullable=True)
    left_leg_percent = Column(Float, nullable=True)
    torso_percent = Column(Float, nullable=True)
    creation_date = Column(DateTime, server_default=func.now())
    
    test = relationship('TestPrimary', back_populates='segmental')
