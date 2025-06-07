import base64
import os
import uuid
import logging
import requests
from io import BytesIO
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from PIL import Image
import ee
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database import engine
from models import ImageHistory

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

imagery_bp = Blueprint('imagery', __name__)

# Whitelisted Earth Engine datasets
ALLOWED_DATASETS = [
    "COPERNICUS/S2_SR_HARMONIZED",
    "LANDSAT/LC08/C02/T1_L2",
    "LANDSAT/LC09/C02/T1_L2",
    "MODIS/006/MOD09GA",
    "USDA/NAIP/DOQQ"
]

# Initialize Earth Engine
try:
    service_account = os.getenv('EE_SERVICE_ACCOUNT')
    credentials = ee.ServiceAccountCredentials(service_account, 'credentials.json')
    ee.Initialize(credentials)
    logger.info("Earth Engine initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Earth Engine: {str(e)}")
    raise

Session = sessionmaker(bind=engine)

@imagery_bp.route('/capture_image', methods=['POST', 'OPTIONS'])
@cross_origin(origins="http://127.0.0.1:5000")
def capture_image():
    request.max_content_length = 100 * 1024 * 1024

    if request.method == 'OPTIONS':
        return '', 200

    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        dataset = data.get('dataset', 'COPERNICUS/S2_SR_HARMONIZED')

        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            return jsonify({"error": "Invalid latitude or longitude values."}), 400

        if dataset not in ALLOWED_DATASETS:
            logger.warning(f"Dataset '{dataset}' not allowed. Falling back to Sentinel-2.")
            dataset = "COPERNICUS/S2_SR_HARMONIZED"

        point = ee.Geometry.Point([longitude, latitude])
        region = point.buffer(100).bounds()

        image_collection = ee.ImageCollection(dataset) \
            .filterBounds(point) \
            .filterDate('2023-01-01', '2024-12-31')

        # Optional cloud filter for certain datasets
        if dataset.startswith("COPERNICUS") or "LANDSAT" in dataset:
            image_collection = image_collection.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10)) \
                                               .sort('CLOUDY_PIXEL_PERCENTAGE')

        image = image_collection.first()

        if image is None:
            return jsonify({"error": "No suitable image found for the selected dataset."}), 404

        scl = image.select('SCL') if 'SCL' in image.bandNames().getInfo() else None

        # Fix cloud mask logic: mask clouds and shadows (SCL 3, 8, 9, 10)
        if scl:
            cloud_mask = scl.eq(3).Or(scl.eq(8)).Or(scl.eq(9)).Or(scl.eq(10))
            masked_image = image.updateMask(cloud_mask.Not())
        else:
            masked_image = image

        # Band mapping per dataset
        BAND_MAPPING = {
            "COPERNICUS/S2_SR_HARMONIZED": ['B4', 'B3', 'B2'],
            "LANDSAT/LC08/C02/T1_L2": ['SR_B4', 'SR_B3', 'SR_B2'],
            "LANDSAT/LC09/C02/T1_L2": ['SR_B4', 'SR_B3', 'SR_B2'],
            "MODIS/006/MOD09GA": ['sur_refl_b01', 'sur_refl_b04', 'sur_refl_b03'],
            "USDA/NAIP/DOQQ": ['R', 'G', 'B']
        }
        bands = BAND_MAPPING.get(dataset, ['B4', 'B3', 'B2'])

        # Visualization parameters per dataset
        VIS_PARAMS = {
            "COPERNICUS/S2_SR_HARMONIZED": {"bands": bands, "min": 0, "max": 3000},
            "LANDSAT/LC08/C02/T1_L2": {"bands": bands, "min": 0, "max": 10000},
            "LANDSAT/LC09/C02/T1_L2": {"bands": bands, "min": 0, "max": 10000},
            "MODIS/006/MOD09GA": {"bands": bands, "min": 0, "max": 5000},
            "USDA/NAIP/DOQQ": {"bands": bands, "min": 0, "max": 255}
        }
        vis_params = VIS_PARAMS.get(dataset, {"bands": bands, "min": 0, "max": 3000})

        # NDVI, EVI, SAVI, GCI calculations adjusted for band names
        ndvi = masked_image.normalizedDifference([bands[0], bands[1]]).rename('NDVI').visualize(min=-1, max=1, palette=['blue', 'white', 'green'])
        evi = masked_image.expression(
            '2.5 * ((b1 - b2) / (b1 + 6 * b2 - 7.5 * b3 + 1))',
            {'b1': masked_image.select(bands[0]), 'b2': masked_image.select(bands[1]), 'b3': masked_image.select(bands[2])}
        ).rename('EVI').visualize(min=-1, max=1, palette=['blue', 'white', 'green'])
        savi = masked_image.expression(
            '(b1 - b2) / (b1 + b2 + 0.5) * (1 + 0.5)',
            {'b1': masked_image.select(bands[0]), 'b2': masked_image.select(bands[1])}
        ).rename('SAVI').visualize(min=-1, max=1, palette=['blue', 'white', 'yellow'])
        gci = masked_image.expression(
            'b2 / b3 - 1',
            {'b2': masked_image.select(bands[1]), 'b3': masked_image.select(bands[2])}
        ).rename('GCI').visualize(min=-1, max=3, palette=['blue', 'white', 'green'])

        # Thumbnail URLs with visualization parameters
        raw_rgb_url = image.visualize(**vis_params).getThumbURL({'format': 'png', 'dimensions': 512})
        rgb_url = masked_image.visualize(**vis_params).getThumbURL({'format': 'png', 'dimensions': 512})
        ndvi_url = ndvi.getThumbURL({'format': 'png', 'dimensions': 512})
        evi_url = evi.getThumbURL({'format': 'png', 'dimensions': 512})
        savi_url = savi.getThumbURL({'format': 'png', 'dimensions': 512})
        gci_url = gci.getThumbURL({'format': 'png', 'dimensions': 512})

        # Download the RGB image and save locally for classification
        rgb_response = requests.get(rgb_url)
        rgb_response.raise_for_status()
        rgb_image_data = rgb_response.content

        # Save RGB image locally
        image_id = str(uuid.uuid4())
        image_filename = f"{image_id}.png"
        image_path = os.path.join('static', 'images', image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        with open(image_path, 'wb') as f:
            f.write(rgb_image_data)

        # Store image record in database with correct field names
        session = Session()
        new_image = ImageHistory(
            latitude=latitude,
            longitude=longitude,
            image_url=os.path.join('images', image_filename),
            ndvi_image_url=ndvi_url,
            evi_image_url=evi_url,
            savi_image_url=savi_url,
            gci_image_url=gci_url,
            raw_rgb_url=rgb_url
        )
        session.add(new_image)
        session.commit()

        # Normalize rgb_url to use forward slashes before returning
        normalized_rgb_url = new_image.image_url.replace('\\', '/')
        return jsonify({
            "rgb_url": normalized_rgb_url,
            "raw_rgb_url": rgb_url,
            "ndvi_url": ndvi_url,
            "evi_url": evi_url,
            "savi_url": savi_url,
            "gci_url": gci_url
        })

    except Exception as e:
        logger.error(f"Error in capture_image: {str(e)}")
        return jsonify({"error": str(e)}), 500
