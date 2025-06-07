from sqlalchemy import Column, Integer, String, Float
from database import Base
from sgp4.api import Satrec
from datetime import datetime
from math import degrees, atan2, sqrt, pi
from werkzeug.security import generate_password_hash, check_password_hash

class CubeSat(Base):
    __tablename__ = 'cubesat_positions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    satellite = Column(String, nullable=False)
    line1 = Column(String, nullable=False)
    line2 = Column(String, nullable=False)

    def compute_position(self):
        """Convert TLE to lat, lon, and alt using SGP4."""
        try:
            from sgp4.ext import jday
            satellite = Satrec.twoline2rv(self.line1, self.line2)
            now = datetime.utcnow()
            jd_full = jday(now.year, now.month, now.day, now.hour, now.minute, now.second + now.microsecond * 1e-6)
            jd = int(jd_full)
            fr = jd_full - jd
            raw_result = satellite.sgp4(jd, fr)  # Get position in ECI coordinates (km)

            if not (isinstance(raw_result, tuple) and len(raw_result) == 3):
                return None, None, None

            e, pos, vel = raw_result

            if e != 0:
                return None, None, None  # Error in calculation

            if not (isinstance(pos, (tuple, list)) and len(pos) == 3):
                return None, None, None

            # Convert ECI to lat/lon/alt
            x, y, z = pos  # ECI coordinates (km)
            earth_radius = 6371  # Earth's radius (km)

            lat = degrees(atan2(z, sqrt(x**2 + y**2)))
            lon = degrees(atan2(y, x))
            alt = sqrt(x**2 + y**2 + z**2) - earth_radius  # Altitude in km

            result = (round(lat, 6), round(lon, 6), round(alt, 2))  # Limit decimal places
            return result
        except Exception as e:
            return None, None, None

    def to_dict(self):
        lat, lon, alt = self.compute_position()
        if lat is None or lon is None or alt is None:
            return {
                "satellite": self.satellite,
                "lat": None,
                "lon": None,
                "alt": None
            }
        return {
            "satellite": self.satellite,
            "lat": lat,
            "lon": lon,
            "alt": alt
        }

class ImageHistory(Base):
    __tablename__ = 'image_history'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    image_url = Column(String, nullable=False)
    ndvi_image_url = Column(String, nullable=True)
    evi_image_url = Column(String, nullable=True)
    savi_image_url = Column(String, nullable=True)
    gci_image_url = Column(String, nullable=True)
    raw_rgb_url = Column(String, nullable=True)  # Added field for raw RGB URL

    def to_dict(self):
        return {
            "id": self.id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "image_url": self.image_url,
            "ndvi_image_url": self.ndvi_image_url,
            "evi_image_url": self.evi_image_url,
            "savi_image_url": self.savi_image_url,
            "gci_image_url": self.gci_image_url,
            "raw_rgb_url": self.raw_rgb_url
        }

class Classification(Base):
    __tablename__ = 'classifications'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    image_url = Column(String, nullable=False)
    classification = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)

    def to_dict(self):
        return {"id": self.id, "image_url": self.image_url, "classification": self.classification, "confidence": self.confidence}

from datetime import datetime
from sqlalchemy import DateTime

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UploadedImage(Base):
    __tablename__ = "uploaded_images"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    image_url = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)

