from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Classification
from celery_worker import process_image

classify_bp = Blueprint('classify', __name__)

Session = sessionmaker(bind=engine)
session = Session()

@classify_bp.route('/classify_image', methods=['POST'])
def classify_image():
    data = request.get_json()
    image_url = data['image_url']
    
    result = process_image.delay(image_url)
    result_data = result.get(timeout=10)

    classification = result_data['classification']
    confidence = result_data['confidence']
    
    classification_entry = Classification(image_url=image_url, classification=classification, confidence=confidence)
    session.add(classification_entry)
    session.commit()

    return jsonify({"classification": classification, "confidence": confidence})
