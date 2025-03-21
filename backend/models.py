from sqlalchemy import Column, Integer, String, Float, create_engine, MetaData
from sqlalchemy.orm import registry, sessionmaker

engine = create_engine('sqlite:///cubesat.db', echo=True)
metadata = MetaData()
mapper_registry = registry()

@mapper_registry.mapped
class CubeSat:
    __tablename__ = 'cubesat_positions'
    id = Column(Integer, primary_key=True)
    satellite = Column(String, nullable=False)
    line1 = Column(String, nullable=False)
    line2 = Column(String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "satellite": self.satellite,
            "line1": self.line1,
            "line2": self.line2
        }

@mapper_registry.mapped
class Image:
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url
        }

@mapper_registry.mapped
class Classification:
    __tablename__ = 'classifications'
    id = Column(Integer, primary_key=True)
    image_url = Column(String, nullable=False)
    classification = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)

metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()