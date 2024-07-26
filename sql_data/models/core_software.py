from sqlalchemy import Column, String
from sql_data.config import Base

class CoreSoftwareModel(Base):
    __tablename__ = 'core_software'
    pin = Column(String(4), nullable=False)
    reset_pin = Column(String(4), nullable=False, primary_key=True)
