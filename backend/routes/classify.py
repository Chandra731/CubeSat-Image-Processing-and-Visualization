import sys
import os
import requests
import uuid
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import sessionmaker
from database import engine
from models import Classification, ImageHistory, UploadedImage
from ai_model.infer import classify_image
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

classify_bp = Blueprint('classify', __name__)
Session = sessionmaker(bind=engine)

@classify_bp.route('/classify_image', methods=['POST'])
def classify_image_route():
    data = request.get_json()
    image_url = data.get('image_url')
    print(f"Received classify request for image_url: {image_url}")  # Debug log
    if not image_url:
        return jsonify({"error": "No image_url provided"}), 400

    session = Session()
    try:
        # Check if image_url is remote URL
        if image_url.startswith('http://') or image_url.startswith('https://'):
            # Download image and save to backend/static/images
            response = requests.get(image_url)
            if response.status_code != 200:
                return jsonify({"error": "Failed to download image from URL"}), 400

            image_id = str(uuid.uuid4())
            image_filename = f"{image_id}.png"
            image_path = os.path.join('static', 'images', image_filename)
            full_image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', image_path))
            os.makedirs(os.path.dirname(full_image_path), exist_ok=True)
            with open(full_image_path, 'wb') as f:
                f.write(response.content)

            # Update image_url to relative path for DB and classification
            image_url = image_path

        # Construct local file path from image_url
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # Normalize path separators to handle mixed slashes
        normalized_image_url = image_url.replace('/', os.sep).replace('\\', os.sep)
        image_path_static = os.path.join(base_dir, 'static', normalized_image_url)
        image_path_uploads = os.path.join(base_dir, 'static', 'uploads', os.path.basename(normalized_image_url))

        print(f"Checking image file path in static: {image_path_static}")  # Debug log
        print(f"Checking image file path in uploads: {image_path_uploads}")  # Debug log
        file_exists_static = os.path.exists(image_path_static)
        file_exists_uploads = os.path.exists(image_path_uploads)
        print(f"Image file exists in static: {file_exists_static}")  # Debug log
        print(f"Image file exists in uploads: {file_exists_uploads}")  # Debug log

        if file_exists_static:
            image_path = image_path_static
        elif file_exists_uploads:
            image_path = image_path_uploads
        else:
            return jsonify({"error": "Image file not found on server"}), 404

        # Call the AI model inference function
        classification_percentages = classify_image(image_path)
        print(f"Classification percentages from model: {classification_percentages}")

        # Store classification result in DB
        confidence = max(classification_percentages.values())
        classification_entry = Classification(
        image_url=image_url,
        classification=str(classification_percentages),
        confidence=confidence
        )

        session.add(classification_entry)
        session.commit()
        

        return jsonify({
            "classification_percentages": classification_percentages
        })
    except Exception as e:
        session.rollback()
        print(f"Error during classification: {e}")  # Debug log
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
