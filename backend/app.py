from flask import Flask
from database import init_db
from routes.cubesat import cubesat_bp
from routes.image import image_bp
from routes.classify import classify_bp
from flask_cors import CORS  

app = Flask(__name__)

# Enable CORS
CORS(app)

# Initialize database
init_db()

# Register Routes
app.register_blueprint(cubesat_bp, url_prefix="/api")
app.register_blueprint(image_bp, url_prefix="/api")
app.register_blueprint(classify_bp, url_prefix="/api")

# Debugging: Print all registered routes
with app.test_request_context():
    print("\n Registered API Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.methods} -> {rule}")

# Run the Flask app
if __name__ == "__main__":
    print("\n Flask API is running at http://127.0.0.1:5001/")
    app.run(debug=True, port=5001)
