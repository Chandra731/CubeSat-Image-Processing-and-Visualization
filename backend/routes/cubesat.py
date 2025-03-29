from flask import Blueprint, jsonify
from sqlalchemy.orm import sessionmaker
from database import engine
from models import CubeSat

cubesat_bp = Blueprint('cubesat', __name__)

Session = sessionmaker(bind=engine)

@cubesat_bp.route('/cubesat_positions')
def get_cubesat_positions():
    session = Session()
    try:
        results = session.query(CubeSat).all()
        data = [row.to_dict() for row in results]
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()
