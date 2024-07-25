from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sql_data.config import Base

class TestSegmental(Base):
    __tablename__ = 'tests_segmental'
    
    test_id = Column(Integer, ForeignKey('tests_primary.test_id'), primary_key=True)
    right_arm = Column(Float)
    left_arm = Column(Float)
    right_leg = Column(Float)
    left_leg = Column(Float)
    torso = Column(Float)
    
    test = relationship('TestPrimary', back_populates='segmental')
