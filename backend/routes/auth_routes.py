"""
Authentication routes for user registration and login.
"""

from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    return jsonify(*AuthService.register_user(username, email, password))


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT token."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    return jsonify(*AuthService.login_user(username, password))


@auth_bp.route('/verify', methods=['GET'])
def verify():
    """Verify JWT token is valid."""
    token = None

    if 'Authorization' in request.headers:
        try:
            token = request.headers['Authorization'].split(" ")[1]
        except IndexError:
            return jsonify({'success': False, 'message': 'Invalid token format'}), 401

    if not token:
        return jsonify({'success': False, 'message': 'Token missing'}), 401

    user = AuthService.get_current_user(token)

    if not user:
        return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401

    return jsonify({
        'success': True,
        'message': 'Token is valid',
        'user': user.to_dict()
    }), 200
