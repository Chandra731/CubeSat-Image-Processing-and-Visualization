from flask import Blueprint, jsonify
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ImageRequest

history_bp = Blueprint('history', __name__)

@history_bp.route('/image_history', methods=['GET'])
def get_image_history():
    db = SessionLocal()
    try:
        history = db.query(ImageRequest).order_by(ImageRequest.timestamp.desc()).all()
        history_data = [
            {
                "id": request.id,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "image_url": request.image_url,
                "timestamp": request.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for request in history
        ]
        return jsonify(history_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
