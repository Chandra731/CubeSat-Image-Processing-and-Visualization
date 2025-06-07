import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, render_template, send_from_directory
from database import init_db
from routes.cubesat import cubesat_bp
from routes.history import history_bp
from routes.classify import classify_bp
from routes.imagery import imagery_bp
from routes.auth import auth_bp
from routes.tle_update import tle_update_bp
from flask_cors import CORS
from datetime import timedelta
import os
import logging
import sys
import ee

from flask_mail import Mail

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '../frontend/templates'))
# Set maximum content length for requests
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB

# Setup secret key and session lifetime
app.secret_key = 'a9d3f6c14b7e4e9580c72fae27db5b4f'
app.permanent_session_lifetime = timedelta(days=1)

# Add missing SECURITY_PASSWORD_SALT config for token generation
app.config['SECURITY_PASSWORD_SALT'] = '7f6b2931d4e942e589c0a1c3e7f84d8b'

# Session cookie settings for cross-origin cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = False  # Set True if using HTTPS

# Flask-Mail configuration for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'chandrabrucelee31@gmail.com'
app.config['MAIL_PASSWORD'] = 'eite srip ryut gyzh'
app.config['MAIL_DEFAULT_SENDER'] = 'chandrabrucelee31@gmail.com'

# Initialize Flask-Mail
mail = Mail(app)

# Enable CORS with credentials support
CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5000", "http://localhost:5000"])

def set_cors_headers(response):
    origin = request.headers.get('Origin')
    allowed_origins = ['http://127.0.0.1:5000', 'http://localhost:5000']
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = 'null'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Vary'] = 'Origin'
    print(f"CORS: Origin={origin}, Set Access-Control-Allow-Origin={response.headers['Access-Control-Allow-Origin']}")
    return response

# Global CORS handler for all responses
@app.after_request
def add_cors_headers(response):
    if request.path.startswith('/api/') or request.path.startswith('/auth/') or request.path.startswith('/static/'):
        response = set_cors_headers(response)
    return response

# Explicit OPTIONS handler for all API routes
@app.route('/api/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = app.make_default_options_response()
    response = set_cors_headers(response)
    return response

@app.route('/auth/<path:path>', methods=['OPTIONS'])
def auth_options_handler(path):
    response = app.make_default_options_response()
    response = set_cors_headers(response)
    return response

# Serve static files explicitly
from flask import make_response

@app.route('/static/<path:filename>')
def serve_static(filename):
    response = make_response(send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), filename))
    response.headers['Access-Control-Allow-Origin'] = 'http://127.0.0.1:5000'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# Initialize database
import logging

logging.basicConfig(level=logging.DEBUG)

logging.debug("Initializing database...")
init_db()
logging.debug("Database initialized.")

# Register Blueprints
app.register_blueprint(cubesat_bp, url_prefix="/api")
app.register_blueprint(history_bp, url_prefix="/api")
app.register_blueprint(classify_bp, url_prefix="/api")
app.register_blueprint(imagery_bp, url_prefix="/api")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(tle_update_bp, url_prefix="/api")
from routes.upload import upload_bp
app.register_blueprint(upload_bp, url_prefix="/api")
from routes.classification_history import classification_history_bp
app.register_blueprint(classification_history_bp, url_prefix="/api")

# Debugging: Print all routes
with app.test_request_context():
    print("\n Registered API Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.methods} -> {rule}")

# Initialize Google Earth Engine only once
if __name__ == "__main__":
    try:
        ee.Initialize()
        logging.info("Google Earth Engine initialized successfully!")
    except Exception as e:
        logging.error(f"Error initializing Google Earth Engine: {e}")

    print("\n Flask API is running at http://127.0.0.1:5001/")
    app.run(debug=True, port=5001, use_reloader=False)

# Add route to serve index.html at root
@app.route('/')
def index():
    return render_template('index.html')

# Add route to serve visualization.html at /dashboard to match frontend navigation
@app.route('/dashboard')
def dashboard():
    return render_template('visualization.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/forgot_password')
def forgot_password_page():
    return render_template('forgot_password.html')
