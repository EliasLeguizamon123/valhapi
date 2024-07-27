from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sql_data.config import Base
from datetime import datetime

class TestEnergy(Base):
    __tablename__ = 'tests_energy'
    
    test_id = Column(Integer, ForeignKey('tests_primary.test_id'), primary_key=True)
    basal_metabolic_rate = Column(Float)
    very_light_activity = Column(Float)
    light_activity = Column(Float)
    moderate_activity = Column(Float)
    heavy_activity = Column(Float)
    very_heavy_activity = Column(Float)
    creation_date = Column(DateTime, default=datetime.utcnow)
    
    test = relationship('TestPrimary', back_populates='energy')