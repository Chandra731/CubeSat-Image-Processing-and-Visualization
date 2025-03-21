from flask import Blueprint, request, jsonify
from celery_worker import process_image

classify_bp = Blueprint('classify', __name__)

@classify_bp.route('/classify_image', methods=['POST'])
def classify_image():
    data = request.get_json()
    image_url = data['image_url']
    
    # Process image using Celery worker
    result = process_image.delay(image_url)
    result_data = result.get(timeout=10)  # Wait for the result with a timeout

    classification = result_data['classification']
    confidence = result_data['confidence']
    
    return jsonify({"classification": classification, "confidence": confidence})