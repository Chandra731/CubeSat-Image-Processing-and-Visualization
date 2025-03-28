from sqlalchemy import Column, Integer, String, Float
from database import Base

class CubeSat(Base):
    __tablename__ = 'cubesat_positions'
    id = Column(Integer, primary_key=True)
    satellite = Column(String, nullable=False)
    line1 = Column(String, nullable=False)
    line2 = Column(String, nullable=False)

    def to_dict(self):
        return {"id": self.id, "satellite": self.satellite, "line1": self.line1, "line2": self.line2}

class ImageHistory(Base):
    __tablename__ = 'image_history'
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    image_url = Column(String, nullable=False)

    def to_dict(self):
        return {"id": self.id, "latitude": self.latitude, "longitude": self.longitude, "image_url": self.image_url}

class Classification(Base):
    __tablename__ = 'classifications'
    id = Column(Integer, primary_key=True)
    image_url = Column(String, nullable=False)
    classification = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)

    def to_dict(self):
        return {"id": self.id, "image_url": self.image_url, "classification": self.classification, "confidence": self.confidence}
