from flask import Flask, request, jsonify
from infer import classify_image
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

@app.route('/classify_image', methods=['POST'])
def classify_image_endpoint():
    file = request.files['file']
    file_location = f"dataset/{file.filename}"
    file.save(file_location)

    classification, confidence = classify_image(file_location)
    return jsonify({"classification": classification, "confidence": confidence})

if __name__ == '__main__':
    app.run(debug=True, host=os.getenv("FLASK_RUN_HOST"), port=os.getenv("FLASK_RUN_PORT"))