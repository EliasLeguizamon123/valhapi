from sql_data.config import Base
from sqlalchemy import Column, String

class OperatorSettings(Base):
    __tablename__ = 'operator_settings'
    
    measure = Column(String)
    business = Column(String)
    collation = Column(String)
    company_name = Column(String, max_length=50)