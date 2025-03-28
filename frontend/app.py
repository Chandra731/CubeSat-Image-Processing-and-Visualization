from flask import Flask, render_template, request, jsonify
from models import db, CubeSat, Image
import os

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cubesat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

IMAGE_STORAGE_PATH = 'static/images'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cubesat_positions')
def get_cubesat_positions():
    satellites = CubeSat.query.all()
    return jsonify([
        {"satellite": sat.name, "lat": sat.latitude, "lon": sat.longitude, "alt": sat.altitude}
        for sat in satellites
    ])

@app.route('/api/capture_image', methods=['POST'])
def capture_image():
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')

    # Generate image path
    image_path = f"{IMAGE_STORAGE_PATH}/image_{latitude}_{longitude}.jpg"
    os.makedirs(IMAGE_STORAGE_PATH, exist_ok=True)

    # Store metadata in database
    new_image = Image(latitude=latitude, longitude=longitude, image_url=image_path)
    db.session.add(new_image)
    db.session.commit()

    return jsonify({"image_url": image_path})

@app.route('/api/image_history')
def image_history():
    images = Image.query.all()
    return jsonify([{"image_url": img.image_url, "timestamp": img.timestamp} for img in images])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
