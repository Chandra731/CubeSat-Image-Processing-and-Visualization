from flask import Blueprint, request, jsonify
import ee
from dotenv import load_dotenv
import os

load_dotenv()

image_bp = Blueprint('image', __name__)

# Initialize Earth Engine with the specified project
ee.Initialize(project=os.getenv('EARTH_ENGINE_PROJECT'))

@image_bp.route('/capture_image', methods=['POST'])
def capture_image():
    data = request.get_json()
    latitude = data['latitude']
    longitude = data['longitude']
    
    # Use GEE to capture the image
    point = ee.Geometry.Point([longitude, latitude])
    image = ee.ImageCollection('COPERNICUS/S2').filterBounds(point).sort('CLOUDY_PIXEL_PERCENTAGE').first()
    url = image.getThumbURL({
        'min': 0,
        'max': 0.3,
        'dimensions': '1024x1024',
        'region': point.buffer(5000).bounds(),
        'format': 'jpg'
    })
    
    return jsonify({"image_url": url})