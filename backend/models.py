from sqlalchemy import Column, Integer, String, Float
from database import Base
from sgp4.api import Satrec
from datetime import datetime
from math import degrees, atan2, sqrt, pi

class CubeSat(Base):
    __tablename__ = 'cubesat_positions'

    id = Column(Integer, primary_key=True)
    satellite = Column(String, nullable=False)
    line1 = Column(String, nullable=False)
    line2 = Column(String, nullable=False)

    def compute_position(self):
        """Convert TLE to lat, lon, and alt using SGP4."""
        try:
            satellite = Satrec.twoline2rv(self.line1, self.line2)
            now = datetime.utcnow()
            jd, fr = now.timetuple().tm_yday + 2451545.0, now.second / 86400.0
            e, pos, vel = satellite.sgp4(jd, fr)  # Get position in ECI coordinates (km)

            if e != 0:
                return None, None, None  # Error in calculation

            # Convert ECI to lat/lon/alt
            x, y, z = pos  # ECI coordinates (km)
            earth_radius = 6371  # Earth's radius (km)

            lat = degrees(atan2(z, sqrt(x**2 + y**2)))
            lon = degrees(atan2(y, x))
            alt = sqrt(x**2 + y**2 + z**2) - earth_radius  # Altitude in km

            return round(lat, 6), round(lon, 6), round(alt, 2)  # Limit decimal places
        except Exception as e:
            print(f"Error computing position for {self.satellite}: {e}")
            return None, None, None

    def to_dict(self):
        lat, lon, alt = self.compute_position()
        return {
            "satellite": self.satellite,
            "lat": lat if lat is not None else 0.0,
            "lon": lon if lon is not None else 0.0,
            "alt": alt if alt is not None else 0.0
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
