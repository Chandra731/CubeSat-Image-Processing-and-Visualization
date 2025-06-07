from flask import Blueprint, jsonify
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Classification

classification_history_bp = Blueprint('classification_history', __name__)

@classification_history_bp.route('/classification_history', methods=['GET'])
def get_classification_history():
    db = SessionLocal()
    try:
        classifications = db.query(Classification).order_by(Classification.id.desc()).all()
        result = [
            {
                "id": c.id,
                "image_url": c.image_url,
                "classification": c.classification,
                "confidence": c.confidence
            }
            for c in classifications
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
