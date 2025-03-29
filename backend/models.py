from sqlalchemy import Column, Integer, String, Float
from database import Base
from sgp4.api import Satrec
from datetime import datetime
from math import degrees

class CubeSat(Base):
    __tablename__ = 'cubesat_positions'
    
    id = Column(Integer, primary_key=True)
    satellite = Column(String, nullable=False)
    line1 = Column(String, nullable=False)
    line2 = Column(String, nullable=False)

    def compute_position(self):
        """Calculate satellite position (lat, lon, alt) from TLE data."""
        try:
            satellite = Satrec.twoline2rv(self.line1, self.line2)
            now = datetime.utcnow()
            jd, fr = now.timetuple().tm_yday + 2451545.0, now.second / 86400.0
            e, position, velocity = satellite.sgp4(jd, fr)

            if e == 0:  # Success
                lat = degrees(position[0])  # Convert to degrees
                lon = degrees(position[1])
                alt = position[2] / 1000  # Convert meters to kilometers
                return lat, lon, alt
            else:
                return None, None, None
        except Exception as e:
            print(f"Error computing position for {self.satellite}: {e}")
            return None, None, None

    def to_dict(self):
        lat, lon, alt = self.compute_position()
        return {
            "satellite": self.satellite,
            "lat": lat,
            "lon": lon,
            "alt": alt
        }

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
