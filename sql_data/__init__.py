from sql_data.config import Base, engine
from sql_data.models.members import Member
from sql_data.models.tests_primary import TestPrimary
from sql_data.models.tests_energy import TestEnergy
from sql_data.models.tests_segmental import TestSegmental

# Crear todas las tablas
Base.metadata.create_all(bind=engine)