from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from database import SessionLocal
from models import ImageHistory, UploadedImage
import os

history_bp = Blueprint('history', __name__)

@history_bp.route('/image_history', methods=['GET'])
def get_image_history():
    db = SessionLocal()
    try:
        # Query both ImageHistory and UploadedImage tables
        history = db.query(ImageHistory).all()
        uploads = db.query(UploadedImage).all()

        # Combine and sort by id descending (assuming higher id is newer)
        combined = [
            {
                "id": img.id,
                "latitude": getattr(img, 'latitude', None),
                "longitude": getattr(img, 'longitude', None),
                "image_url": img.image_url,
                "raw_rgb_url": getattr(img, 'raw_rgb_url', None)
            }
            for img in history
        ] + [
            {
                "id": img.id,
                "latitude": None,
                "longitude": None,
                "image_url": img.image_url,
                "raw_rgb_url": None
            }
            for img in uploads
        ]

        combined_sorted = sorted(combined, key=lambda x: x['id'], reverse=True)

        return jsonify(combined_sorted)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@history_bp.route('/delete_image/<int:image_id>', methods=['DELETE', 'OPTIONS'])
def delete_image(image_id):
    db = SessionLocal()
    try:
        print(f"Attempting to delete image with ID: {image_id}")  # Debug log
        image = db.query(ImageHistory).filter(ImageHistory.id == image_id).first()
        if image:
            # For GEE URLs, just delete the DB record without file deletion
            if image.image_url.startswith('http'):
                db.delete(image)
                db.commit()
                return jsonify({"message": "Image URL deleted successfully"})
            else:
                # Delete image file from disk if exists
                image_path = os.path.join('static', image.image_url)
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                        print(f"Deleted image file at {image_path}")
                    except Exception as file_err:
                        print(f"Failed to delete image file: {file_err}")

                db.delete(image)
                db.commit()
                return jsonify({"message": "Image deleted successfully"})

        # If not found in ImageHistory, check UploadedImage
        upload_image = db.query(UploadedImage).filter(UploadedImage.id == image_id).first()
        if upload_image:
            image_path = os.path.join('static', upload_image.image_url)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    print(f"Deleted uploaded image file at {image_path}")
                except Exception as file_err:
                    print(f"Failed to delete uploaded image file: {file_err}")

            db.delete(upload_image)
            db.commit()
            return jsonify({"message": "Uploaded image deleted successfully"})

        print(f"Image with ID {image_id} not found in any table")  # Debug log
        return jsonify({"error": "Image not found", "id": image_id}), 404

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
