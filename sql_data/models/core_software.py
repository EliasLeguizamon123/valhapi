from sql_data.config import Base
from sqlalchemy import Column, String

class CoreSoftware(Base):
    pin = Column(String, nullable=False, max_length=4)
    reset_pin = Column(String, nullable=False, max_length=4)