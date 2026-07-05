from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from models import db, User
import bcrypt
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)


def hash_password(password):
    """
    Hash password using bcrypt
    Never store plain text passwords!
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def check_password(password, hashed):
    """Check if password matches hash"""
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )


@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    """
    Register new user
    Role can be 'doctor' or 'patient'
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        role = data.get('role', 'patient').strip()
        age = data.get('age', None)
        phone = data.get('phone', '').strip()

        if not name:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400

        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400

        if not password:
            return jsonify({
                'success': False,
                'error': 'Password is required'
            }), 400

        if len(password) < 6:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 6 characters'
            }), 400

        if role not in ['doctor', 'patient']:
            return jsonify({
                'success': False,
                'error': 'Role must be doctor or patient'
            }), 400

        # Check if email already exists
        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 400

        # Hash password before saving
        hashed_password = hash_password(password)

        # Create user
        user = User(
            name=name,
            email=email,
            password_hash=hashed_password,
            role=role,
            age=age,
            phone=phone
        )

        db.session.add(user)
        db.session.commit()

        # Create JWT token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'role': user.role,
                'name': user.name,
                'email': user.email
            },
            expires_delta=timedelta(hours=24)
        )

        return jsonify({
            'success': True,
            'message': f'Welcome {name}! Account created successfully.',
            'token': access_token,
            'user': user.to_dict()
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login with email and password
    Returns JWT token on success
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password required'
            }), 400

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401

        # Check password
        if not check_password(password, user.password_hash):
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401

        # Check if account is active
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'Account is disabled'
            }), 401

        # Create JWT token
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'role': user.role,
                'name': user.name,
                'email': user.email
            },
            expires_delta=timedelta(hours=24)
        )

        return jsonify({
            'success': True,
            'message': f'Welcome back {user.name}!',
            'token': access_token,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current logged in user info
    Requires valid JWT token
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user"""
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200