from flask import Flask, jsonify
from dotenv import load_dotenv
import os

from routes.cubesat import cubesat_bp
from routes.image import image_bp
from routes.classify import classify_bp

load_dotenv()

app = Flask(__name__)

app.register_blueprint(cubesat_bp)
app.register_blueprint(image_bp)
app.register_blueprint(classify_bp)

@app.route('/')
def index():
    return jsonify({"message": "Welcome to CubeSat Data Processing & Visualization API"})

if __name__ == '__main__':
    app.run(debug=True, host=os.getenv("FLASK_RUN_HOST"), port=os.getenv("FLASK_RUN_PORT"))