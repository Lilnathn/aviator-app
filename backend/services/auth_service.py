"""
Authentication service for user management and JWT token handling.
"""

from datetime import datetime, timedelta
from functools import wraps
import jwt
from flask import current_app, request, jsonify
from models.database import db, User


class AuthService:
    """Service for handling user authentication."""

    @staticmethod
    def register_user(username, email, password):
        """Register a new user."""
        if not username or not email or not password:
            return {'success': False, 'message': 'Missing required fields'}, 400

        if len(password) < 6:
            return {'success': False, 'message': 'Password must be at least 6 characters'}, 400

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return {'success': False, 'message': 'Username already exists'}, 409

        if User.query.filter_by(email=email).first():
            return {'success': False, 'message': 'Email already registered'}, 409

        try:
            # Create new user
            user = User(username=username, email=email, balance=100.0)  # Demo starting balance
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            return {
                'success': True,
                'message': 'User registered successfully',
                'user': user.to_dict()
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500

    @staticmethod
    def login_user(username, password):
        """Login user and return JWT token."""
        if not username or not password:
            return {'success': False, 'message': 'Missing credentials'}, 400

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return {'success': False, 'message': 'Invalid credentials'}, 401

        # Generate JWT token
        token = AuthService.generate_token(user.id)

        return {
            'success': True,
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }, 200

    @staticmethod
    def generate_token(user_id, expires_in=24):
        """Generate JWT token for user."""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=expires_in),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return token

    @staticmethod
    def verify_token(token):
        """Verify JWT token and return user_id."""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def get_current_user(token):
        """Get current user from token."""
        user_id = AuthService.verify_token(token)
        if not user_id:
            return None
        return User.query.get(user_id)


def token_required(f):
    """Decorator to require valid JWT token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401

        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401

        user = AuthService.get_current_user(token)
        if not user:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

        # Pass current user to the route
        request.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user') or not request.current_user.is_admin:
            return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
        return f(*args, **kwargs)

    return decorated_function
