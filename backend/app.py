from flask import Flask
from database import init_db
from routes.cubesat import cubesat_bp
from routes.image import image_bp
from routes.classify import classify_bp
from flask_cors import CORS  

app = Flask(__name__)

CORS(app) 
# Initialize database
init_db()

# Register Routes
app.register_blueprint(cubesat_bp, url_prefix="/api")
app.register_blueprint(image_bp, url_prefix="/api")
app.register_blueprint(classify_bp, url_prefix="/api")

# Debug: Print all registered routes
with app.test_request_context():
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)

if __name__ == "__main__":
    app.run(debug=True)
