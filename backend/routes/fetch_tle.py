import requests
from flask import Blueprint, jsonify
from sqlalchemy.orm import sessionmaker
from database import engine
from models import CubeSat
import datetime
import logging
import os

tle_update_bp = Blueprint('tle_update', __name__)
Session = sessionmaker(bind=engine)

CELESTRAK_URL = "https://celestrak.com/NORAD/elements/cubesat.txt"
UPDATE_INTERVAL_HOURS = 24  # Configurable time limit for automatic updates
LAST_UPDATE_FILE = os.path.join(os.path.dirname(__file__), 'tle_last_update.txt')

def fetch_latest_tle():
    """
    Fetch latest TLE data from Celestrak Cubesat catalog.
    Returns a list of dicts with keys: satellite, line1, line2
    """
    response = requests.get(CELESTRAK_URL)
    response.raise_for_status()
    lines = response.text.strip().splitlines()
    tle_data = []
    for i in range(0, len(lines), 3):
        if i + 2 >= len(lines):
            break
        satellite = lines[i].strip()
        line1 = lines[i+1].strip()
        line2 = lines[i+2].strip()
        # Basic validation: TLE lines length and format
        if len(line1) < 69 or len(line2) < 69:
            logging.warning(f"Skipping satellite {satellite} due to invalid TLE line length")
            continue
        tle_data.append({
            "satellite": satellite,
            "line1": line1,
            "line2": line2
        })
    return tle_data

def should_update(last_update_time):
    """
    Determine if enough time has passed since last update to proceed.
    """
    if last_update_time is None:
        return True
    now = datetime.datetime.utcnow()
    elapsed = now - last_update_time
    return elapsed.total_seconds() >= UPDATE_INTERVAL_HOURS * 3600

@tle_update_bp.route('/update_tle', methods=['POST'])
def update_tle_data():
    """
    Fetch latest TLE data and update the CubeSat database.
    Adds new satellites and updates existing ones.
    Respects update interval to avoid excessive requests.
    Skips satellites with invalid TLE data.
    """
    session = Session()
    try:
        # Check last update time stored in a simple file or DB (for demo, use a file)
        try:
            with open(LAST_UPDATE_FILE, 'r') as f:
                last_update_str = f.read().strip()
                last_update_time = datetime.datetime.fromisoformat(last_update_str)
        except Exception:
            last_update_time = None

        if not should_update(last_update_time):
            return jsonify({"message": "Update skipped due to time limit"}), 200

        tle_data = fetch_latest_tle()
        updated = 0
        added = 0
        skipped = 0
        for tle in tle_data:
            sat_name = tle["satellite"]
            if not tle["line1"] or not tle["line2"]:
                logging.warning(f"Skipping satellite {sat_name} due to missing TLE lines")
                skipped += 1
                continue
            existing = session.query(CubeSat).filter(CubeSat.satellite == sat_name).first()
            if existing:
                if existing.line1 != tle["line1"] or existing.line2 != tle["line2"]:
                    existing.line1 = tle["line1"]
                    existing.line2 = tle["line2"]
                    updated += 1
            else:
                new_sat = CubeSat(
                    satellite=sat_name,
                    line1=tle["line1"],
                    line2=tle["line2"]
                )
                session.add(new_sat)
                added += 1
        session.commit()

        # Update last update time
        with open(LAST_UPDATE_FILE, 'w') as f:
            f.write(datetime.datetime.utcnow().isoformat())

        return jsonify({
            "message": "TLE data updated",
            "updated": updated,
            "added": added,
            "skipped": skipped
        })
    except Exception as e:
        session.rollback()
        logging.error(f"Error updating TLE data: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
