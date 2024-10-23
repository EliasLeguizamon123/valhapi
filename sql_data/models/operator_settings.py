from sql_data.config import Base
from sqlalchemy import Column, String, Integer, Boolean

class OperatorSettings(Base):
    __tablename__ = 'operator_settings'
    
    id = Column(Integer, primary_key=True, default=1, unique=True)
    measure = Column(String(50))
    business = Column(String(50))
    collation = Column(String(50))
    company_name = Column(String(60))
    selected_printer = Column(String(50), nullable=True)
    com = Column(String(15), nullable=True)
    includes = Column(String, nullable=True)
    test2 = Column(Boolean, default=False)
    test3 = Column(Boolean, default=False)
    test4 = Column(Boolean, default=False)
    test5 = Column(Boolean, default=False)
