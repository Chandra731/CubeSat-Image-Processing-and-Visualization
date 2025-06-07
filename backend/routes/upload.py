import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from sqlalchemy.orm import sessionmaker
from database import engine
from models import UploadedImage

upload_bp = Blueprint('upload', __name__)
Session = sessionmaker(bind=engine)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image_file' not in request.files:
        return jsonify({"error": "No image_file part in the request"}), 400

    file = request.files['image_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{unique_id}.{ext}"
        save_path = os.path.join('static', 'images', unique_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)

        session = Session()
        try:
            new_image = UploadedImage(image_url=os.path.join('images', unique_filename))
            session.add(new_image)
            session.commit()
            return jsonify({"image_url": new_image.image_url})
        except Exception as e:
            session.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            session.close()
    else:
        return jsonify({"error": "File type not allowed"}), 400
