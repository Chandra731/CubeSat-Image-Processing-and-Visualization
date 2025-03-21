from flask import Blueprint, jsonify
from sqlalchemy.orm import sessionmaker
from database import engine, CubeSat
from pyorbital.orbital import Orbital
from datetime import datetime

cubesat_bp = Blueprint('cubesat', __name__)

Session = sessionmaker(bind=engine)
session = Session()

@cubesat_bp.route('/cubesat_positions')
def get_cubesat_positions():
    results = session.query(CubeSat).all()
    positions = []

    for row in results:
        satellite = row.satellite
        line1 = row.line1
        line2 = row.line2
        orb = Orbital(satellite, line1=line1, line2=line2)
        now = datetime.utcnow()
        lon, lat, alt = orb.get_lonlatalt(now)
        positions.append({
            "satellite": satellite,
            "lon": lon,
            "lat": lat,
            "alt": alt
        })
    
    return jsonify(positions)