from importlib.abc import Loader
from flask import Blueprint, request, jsonify
from models import CubeSat
from datetime import datetime, timedelta
from sgp4.api import Satrec
from sgp4.ext import jday
import numpy as np
from skyfield.api import Loader, EarthSatellite
from backend.utils import get_db_session, handle_errors

cubesat_bp = Blueprint('cubesat', __name__)

load = Loader('skyfield_data')  # Required for Earth model

def compute_orbit(tle1, tle2, duration_days=1, interval_minutes=10):
    try:
        satellite = Satrec.twoline2rv(tle1, tle2)
        now = datetime.utcnow()
        orbit_data = []

        ts = load.timescale()
        earth = load('de421.bsp')['earth']

        for minute in range(0, duration_days * 24 * 60, interval_minutes):
            time = now + timedelta(minutes=minute)
            jd_full = jday(time.year, time.month, time.day, time.hour, time.minute, time.second)
            jd, fr = np.divmod(jd_full, 1)

            e, r, v = satellite.sgp4(jd, fr)

            if e == 0:  # Only process valid data
                satellite_skyfield = EarthSatellite(tle1, tle2, 'Cubesat', ts)
                geocentric = satellite_skyfield.at(ts.utc(time.year, time.month, time.day, 
                                                           time.hour, time.minute, time.second))
                subpoint = geocentric.subpoint()

                orbit_data.append({
                    'timestamp': time.isoformat(),
                    'lat': subpoint.latitude.degrees,
                    'lon': subpoint.longitude.degrees,
                    'alt': subpoint.elevation.km  # Corrected altitude in km
                })
            else:
                print(f" SGP4 Error: {e} at {time}")  # Debugging: Print error code

        return orbit_data

    except Exception as e:
        print(" Error in compute_orbit:", str(e))
        return []  # Return empty list on failure

@cubesat_bp.route('/cubesat_orbits', methods=['GET'])
@handle_errors
def get_cubesat_orbits():
    with get_db_session() as session:
        results = session.query(CubeSat).all()
        orbits = []
        for row in results:
            orbit = compute_orbit(row.line1, row.line2)
            orbits.append({
                'satellite': row.satellite,
                'orbit': orbit
            })

        print("Orbits data:", orbits)  # Debugging: Print the orbits data
        return jsonify(orbits)

@cubesat_bp.route('/cubesat_positions', methods=['GET'])
@handle_errors
def get_cubesat_positions():
    """Fetch CubeSat positions from the database and return as JSON."""
    with get_db_session() as session:
        results = session.query(CubeSat).all()
        data = []
        for row in results:
            d = row.to_dict()
            # Convert numpy float64 to native float, handle None safely
            d['lat'] = float(d['lat']) if d['lat'] is not None else None
            d['lon'] = float(d['lon']) if d['lon'] is not None else None
            d['alt'] = float(d['alt']) if d['alt'] is not None else None
            data.append(d)
        return jsonify(data)

@cubesat_bp.route('/cubesat_chart_data', methods=['GET'])
@handle_errors
def get_cubesat_chart_data():
    """Fetch CubeSat altitude data for chart visualization."""
    with get_db_session() as session:
        results = session.query(CubeSat).all()
        labels, data = [], []

        for row in results:
            position = row.compute_position()
            if position is None or len(position) != 3:
                print(f"Invalid position data for satellite {row.satellite}: {position}")
                continue
            lat, lon, alt = position
            if alt is not None:
                labels.append(row.satellite)
                data.append(float(alt))  # Convert numpy float64 to float

        print(f"Labels: {labels}, Data: {data}")  # Debugging statement
        return jsonify({'labels': labels, 'data': data})

@cubesat_bp.route('/cubesat_heatmap_data', methods=['GET'])
@handle_errors
def get_cubesat_heatmap_data():
    """Fetch CubeSat positional data formatted for heatmap visualization."""
    with get_db_session() as session:
        results = session.query(CubeSat).all()
        heatmap_data = {'max': 100, 'data': []}

        for row in results:
            position = row.compute_position()
            if position is None or len(position) != 3:
                print(f"Invalid position data for satellite {row.satellite}: {position}")
                continue
            lat, lon, _ = position
            if lat is not None and lon is not None:
                heatmap_data['data'].append({"x": float(lon), "y": float(lat), "value": 1})  # Convert numpy float64 to float

        return jsonify(heatmap_data)
