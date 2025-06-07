from flask import Blueprint, request, jsonify, session, current_app, url_for
from database import SessionLocal
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask_mail import Message, Mail
from functools import wraps
from flask import g

auth_bp = Blueprint('auth', __name__)
mail = Mail()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        session_db = SessionLocal()
        g.user = session_db.query(get_user_model()).filter(get_user_model().id == user_id).first()
        session_db.close()

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except (SignatureExpired, BadSignature):
        return False
    return email

def get_user_model():
    from backend.models import User
    return User

def get_db_session():
    return SessionLocal()

import re

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"Register request data: {data}")  # Debug log
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirmPassword')

        # Validation
        if not username or not email or not password or not confirm_password:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        if len(username) < 3 or len(username) > 30:
            return jsonify({'success': False, 'message': 'Username must be between 3 and 30 characters'}), 400

        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            return jsonify({'success': False, 'message': 'Username can only contain letters, numbers, underscores, dots, and hyphens'}), 400

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({'success': False, 'message': 'Invalid email address'}), 400

        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match'}), 400

        User = get_user_model()
        db_session = get_db_session()

        if db_session.query(User).filter((User.username == username) | (User.email == email)).first():
            return jsonify({'success': False, 'message': 'User with this username or email already exists'}), 400

        user = User(username=username, email=email)
        user.set_password(password)
        db_session.add(user)
        db_session.commit()

        print("User registered successfully")  # Debug log
        return jsonify({'success': True, 'message': 'User registered successfully'}), 201
    except Exception as e:
        print(f"Exception during registration: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@auth_bp.route('/status', methods=['GET'])
def status():
    if 'user_id' in session:
        return jsonify({'success': True, 'user': {'id': session['user_id'], 'username': session.get('username')}})
    else:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username_or_email = data.get('username')
    password = data.get('password')

    if not username_or_email or not password:
        return jsonify({'success': False, 'message': 'Missing username/email or password'}), 400

    User = get_user_model()
    db_session = get_db_session()

    user = db_session.query(User).filter((User.username == username_or_email) | (User.email == username_or_email)).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'success': True, 'message': 'Logged in successfully'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_bp.route('/password_reset_request', methods=['POST'])
def password_reset_request():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400

    User = get_user_model()
    db_session = get_db_session()

    user = db_session.query(User).filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'message': 'Email not found'}), 404

    token = generate_confirmation_token(email)
    # Change reset_url to point to frontend password reset page
    reset_url = url_for('auth.password_reset', token=token, _external=True)

    msg = Message(subject="Password Reset Request For cubesat Visualization Platform",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email])
    msg.body = f"To reset your password, visit the following link:\n{reset_url}\nIf you did not request this, please ignore this email."
    mail.send(msg)

    return jsonify({'success': True, 'message': 'Password reset email sent'})

@auth_bp.route('/password_reset/<token>', methods=['POST'])
def password_reset(token):
    data = request.get_json()
    new_password = data.get('password')
    confirm_password = data.get('confirmPassword')

    if not new_password or not confirm_password:
        return jsonify({'success': False, 'message': 'Missing password fields'}), 400

    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match'}), 400

    User = get_user_model()
    db_session = get_db_session()

    email = confirm_token(token)
    if not email:
        return jsonify({'success': False, 'message': 'Invalid or expired token'}), 400

    user = db_session.query(User).filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    user.set_password(new_password)
    db_session.commit()

    return jsonify({'success': True, 'message': 'Password has been reset successfully'})
