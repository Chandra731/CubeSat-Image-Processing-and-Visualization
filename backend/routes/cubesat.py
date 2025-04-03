from importlib.abc import Loader
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database import engine
from models import CubeSat, ImageHistory, Classification
from datetime import datetime
import ee
import random
from sgp4.api import Satrec
from sgp4.ext import jday
from datetime import datetime, timedelta
from math import degrees
from pyproj import Geod
import traceback
import numpy as np
from skyfield.api import Loader, EarthSatellite

cubesat_bp = Blueprint('cubesat', __name__)
Session = sessionmaker(bind=engine)

# Initialize Google Earth Engine (GEE)
try:
    ee.Initialize(project='cubesat731')
    print(" Google Earth Engine initialized successfully!")
except Exception as e:
    print(" GEE Initialization Failed:", str(e))


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

            if e == 0:  # ✅ Only process valid data
                satellite_skyfield = EarthSatellite(tle1, tle2, 'Cubesat', ts)
                geocentric = satellite_skyfield.at(ts.utc(time.year, time.month, time.day, 
                                                           time.hour, time.minute, time.second))
                subpoint = geocentric.subpoint()

                orbit_data.append({
                    'timestamp': time.isoformat(),
                    'lat': subpoint.latitude.degrees,
                    'lon': subpoint.longitude.degrees,
                    'alt': subpoint.elevation.km  # ✅ Corrected altitude in km
                })
            else:
                print(f"⚠️ SGP4 Error: {e} at {time}")  # ✅ Debugging: Print error code

        return orbit_data

    except Exception as e:
        print("❌ Error in compute_orbit:", str(e))
        return []  # Return empty list on failure

@cubesat_bp.route('/cubesat_orbits', methods=['GET'])
def get_cubesat_orbits():
    session = Session()
    try:
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
    
    except Exception as e:
        print("Error:", str(e))  # Print error message
        traceback.print_exc()  # Print full error traceback
        return jsonify({"error": str(e)}), 500
    
    finally:
        session.close()


def get_satellite_image_url(latitude=None, longitude=None):
    """Fetch a satellite image URL from Google Earth Engine for given coordinates."""
    try:
        # If no coordinates are provided, generate random global coordinates
        if latitude is None or longitude is None:
            latitude = random.uniform(-90, 90)
            longitude = random.uniform(-180, 180)

        point = ee.Geometry.Point([longitude, latitude])

        # Try Sentinel-2 first
        image_collection = (ee.ImageCollection('COPERNICUS/S2')
                            .filterBounds(point)
                            .filterDate('2024-01-01', '2025-01-01')
                            .sort('CLOUDY_PIXEL_PERCENTAGE', True))

        image = image_collection.first()

        # Fallback to Landsat 8 if Sentinel-2 fails
        if image.getInfo() is None:
            print(f" No Sentinel-2 image found for ({latitude}, {longitude}), trying Landsat 8...")
            image_collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA')
                                .filterBounds(point)
                                .filterDate('2024-01-01', '2025-01-01')
                                .sort('CLOUD_COVER', True))
            image = image_collection.first()

        # If both sources fail
        if image.getInfo() is None:
            print(f" No satellite image found for ({latitude}, {longitude})")
            return None

        # Generate image thumbnail URL
        url = image.getThumbURL({
            'region': point,
            'dimensions': 512,
            'format': 'png'
        })

        print(f"📸 Captured Image URL: {url}")
        return url

    except Exception as e:
        print("❌ Error fetching satellite image:", str(e))
        return None

@cubesat_bp.route('/image_history', methods=['GET'])
def get_image_history():
    """Fetch all captured images from the database."""
    session = Session()
    try:
        results = session.query(ImageHistory).all()
        data = [{'latitude': row.latitude, 'longitude': row.longitude, 'image_url': row.image_url, 'timestamp': row.timestamp} for row in results]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@cubesat_bp.route('/store_image', methods=['POST'])
def store_image():
    """Store a captured image in the database."""
    data = request.get_json()
    image_url = data.get('imageUrl')
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    if not image_url:
        return jsonify({"error": "Image URL is required"}), 400

    session = Session()
    try:
        new_image = ImageHistory(latitude=latitude, longitude=longitude, image_url=image_url, timestamp=datetime.utcnow())
        session.add(new_image)
        session.commit()
        return jsonify({"message": "Image stored successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@cubesat_bp.route('/capture_image', methods=['POST'])
def capture_image():
    """Simulate capturing an image from a satellite and store it in the database."""
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # If no coordinates are provided, use random ones
    image_url = get_satellite_image_url(latitude, longitude)

    if not image_url:
        return jsonify({"error": "No satellite image available for this location."}), 500

    session = Session()
    try:
        new_image = ImageHistory(
            latitude=latitude,
            longitude=longitude,
            image_url=image_url,
            timestamp=datetime.utcnow()
        )
        session.add(new_image)
        session.commit()
        return jsonify({'image_url': image_url, 'latitude': latitude, 'longitude': longitude})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@cubesat_bp.route('/cubesat_positions', methods=['GET'])
def get_cubesat_positions():
    """Fetch CubeSat positions from the database and return as JSON."""
    session = Session()
    try:
        results = session.query(CubeSat).all()
        data = [row.to_dict() for row in results]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Error fetching CubeSat positions: {str(e)}"}), 500
    finally:
        session.close()


@cubesat_bp.route('/classify_image', methods=['POST'])
def classify_image():
    """Classify an image and store the result in the database."""
    data = request.get_json()
    image_url = data.get('image_url')

    if not image_url:
        return jsonify({"error": "Image URL is required"}), 400

    classification = "example_classification"  # Replace with actual classification logic
    confidence = 0.95  # Replace with actual confidence value

    session = Session()
    try:
        new_classification = Classification(image_url=image_url, classification=classification, confidence=confidence)
        session.add(new_classification)
        session.commit()
        return jsonify({'image_url': image_url, 'classification': classification, 'confidence': confidence})
    except Exception as e:
        return jsonify({"error": f"Error classifying image: {str(e)}"}), 500
    finally:
        session.close()


@cubesat_bp.route('/cubesat_chart_data', methods=['GET'])
def get_cubesat_chart_data():
    """Fetch CubeSat altitude data for chart visualization."""
    session = Session()
    try:
        results = session.query(CubeSat).all()
        labels, data = [], []

        for row in results:
            lat, lon, alt = row.compute_position()
            if alt is not None:
                labels.append(row.satellite)
                data.append(alt)

        return jsonify({'labels': labels, 'data': data})
    except Exception as e:
        return jsonify({"error": f"Error fetching CubeSat chart data: {str(e)}"}), 500
    finally:
        session.close()


@cubesat_bp.route('/cubesat_heatmap_data', methods=['GET'])
def get_cubesat_heatmap_data():
    """Fetch CubeSat positional data formatted for heatmap visualization."""
    session = Session()
    try:
        results = session.query(CubeSat).all()
        heatmap_data = {'max': 100, 'data': []}

        for row in results:
            lat, lon, _ = row.compute_position()
            if lat is not None and lon is not None:
                heatmap_data['data'].append({"x": lon, "y": lat, "value": 1})

        return jsonify(heatmap_data)
    except Exception as e:
        return jsonify({"error": f"Error fetching CubeSat heatmap data: {str(e)}"}), 500
    finally:
        session.close()
