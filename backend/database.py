from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import registry, sessionmaker

# Database setup
engine = create_engine('sqlite:///cubesat.db', echo=True)
metadata = MetaData()

# Define cubesat_positions table
cubesat_positions = Table(
    'cubesat_positions', metadata,
    Column('id', Integer, primary_key=True),
    Column('satellite', String),
    Column('line1', String),
    Column('line2', String)
)

# Create a registry and map the CubeSat class
mapper_registry = registry()

@mapper_registry.mapped
class CubeSat:
    __table__ = cubesat_positions

metadata.create_all(engine)

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()