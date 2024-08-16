# sql_data/models/operator_settings.py
from sql_data.config import Base
from sqlalchemy import Column, String, Integer

class OperatorSettings(Base):
    __tablename__ = 'operator_settings'
    
    id = Column(Integer, primary_key=True, default=1, unique=True)
    measure = Column(String(50))
    business = Column(String(50))
    collation = Column(String(50))
    company_name = Column(String(60))
