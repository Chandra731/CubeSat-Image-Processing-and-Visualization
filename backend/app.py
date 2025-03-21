from flask import Flask, request, jsonify
from database import session, CubeSat
from celery_worker import process_image
import os
from models import Image, Classification

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cubesat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/cubesat_positions', methods=['GET'])
def get_cubesat_positions():
    cubesats = session.query(CubeSat).all()
    return jsonify([cubesat.to_dict() for cubesat in cubesats])

@app.route('/capture_image', methods=['POST'])
def capture_image():
    data = request.get_json()
    latitude = data['latitude']
    longitude = data['longitude']
    # Simulate image capture from Earth Engine API
    image_url = f"https://earthengine.googleapis.com/v1alpha/projects/earthengine-legacy/thumbnails/{latitude},{longitude}.png"
    
    # Store the image in the database
    new_image = Image(url=image_url)
    session.add(new_image)
    session.commit()
    
    return jsonify({"image_url": image_url})

@app.route('/classify_image', methods=['POST'])
def classify_image():
    data = request.get_json()
    image_url = data['image_url']
    result = process_image.delay(image_url)
    result_data = result.get(timeout=10)
    classification = result_data['classification']
    confidence = result_data['confidence']
    new_classification = Classification(image_url=image_url, classification=classification, confidence=confidence)
    session.add(new_classification)
    session.commit()
    return jsonify({"classification": classification, "confidence": confidence})

@app.route('/image_history', methods=['GET'])
def image_history():
    images = session.query(Image).all()
    return jsonify([image.to_dict() for image in images])

if __name__ == "__main__":
    app.run(debug=True)