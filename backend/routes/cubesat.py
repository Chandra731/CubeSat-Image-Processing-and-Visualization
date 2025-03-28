from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database import engine, CubeSat
from pyorbital.orbital import Orbital
from datetime import datetime, timedelta

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

@cubesat_bp.route('/cubesat_history')
def get_cubesat_history():
    satellite = request.args.get("satellite")
    if not satellite:
        return jsonify({"error": "Satellite name is required"}), 400
    
    row = session.query(CubeSat).filter_by(satellite=satellite).first()
    if not row:
        return jsonify({"error": "Satellite not found"}), 404

    line1, line2 = row.line1, row.line2
    orb = Orbital(satellite, line1=line1, line2=line2)

    history = []
    now = datetime.utcnow()
    for i in range(1, 13):  # Get past 12 hours of data
        past_time = now - timedelta(hours=i)
        lon, lat, alt = orb.get_lonlatalt(past_time)
        history.append({"time": past_time.isoformat(), "lon": lon, "lat": lat, "alt": alt})

    return jsonify(history)
