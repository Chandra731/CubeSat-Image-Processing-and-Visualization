from flask import Blueprint, request, jsonify
import ee
from sqlalchemy.orm import sessionmaker
from database import engine
from models import ImageHistory
from dotenv import load_dotenv
import os

load_dotenv()

image_bp = Blueprint('image', __name__)

# Initialize Google Earth Engine
ee.Initialize(project=os.getenv('EARTH_ENGINE_PROJECT'))

Session = sessionmaker(bind=engine)
session = Session()

@image_bp.route('/capture_image', methods=['POST'])
def capture_image():
    data = request.get_json()
    latitude = data['latitude']
    longitude = data['longitude']
    
    point = ee.Geometry.Point([longitude, latitude])
    image = ee.ImageCollection('COPERNICUS/S2').filterBounds(point).sort('CLOUDY_PIXEL_PERCENTAGE').first()
    url = image.getThumbURL({'min': 0, 'max': 0.3, 'dimensions': '1024x1024'})

    # Store in DB
    img_entry = ImageHistory(latitude=latitude, longitude=longitude, image_url=url)
    session.add(img_entry)
    session.commit()
    
    return jsonify({"image_url": url})

@image_bp.route('/image_history', methods=['GET'])
def image_history():
    results = session.query(ImageHistory).all()
    return jsonify([row.to_dict() for row in results])
