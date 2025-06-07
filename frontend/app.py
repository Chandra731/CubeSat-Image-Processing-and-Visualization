from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Route to serve the main frontend page
@app.route('/')
def index():
    return render_template('index.html')

# Route to serve the image history page    
@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/visualization')
def visualization():
    return render_template('visualization.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

# New routes to serve login, register, and forgot_password pages
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

# Route to serve static JS files
@app.route('/static/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)

# Route to serve static CSS files
@app.route('/static/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(app.static_folder, 'css'), filename)

# Route to serve static images
@app.route('/static/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(os.path.join(app.static_folder, 'images'), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
