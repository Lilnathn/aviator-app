"""
Main Flask application for Aviator betting demo.
School project demonstration - simulation only, no real gambling.
"""

import os
import json
from datetime import datetime
from flask import Flask, jsonify, serve_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from models.database import db, User
from routes.auth_routes import auth_bp
from routes.wallet_routes import wallet_bp
from routes.game_routes import game_bp
from routes.admin_routes import admin_bp
from services.game_service import GameService


def create_app(config_name='development'):
    """Application factory."""
    app = Flask(__name__)

    # Configuration
    if config_name == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aviator_prod.db'
        app.config['DEBUG'] = False
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aviator_demo.db'
        app.config['DEBUG'] = True

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'demo-secret-key-change-in-production')

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(wallet_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(admin_bp)

    # Create database tables
    with app.app_context():
        db.create_all()
        # Create demo admin user if not exists
        create_demo_admin()
        # Initialize game
        if not GameService.game_state['round_id']:
            GameService.start_new_round()

    # Health check route
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'message': 'Aviator API is running',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    # Serve frontend static files
    @app.route('/', methods=['GET'])
    @app.route('/<path:path>', methods=['GET'])
    def serve_frontend(path=None):
        """Serve frontend files."""
        if path is None:
            return serve_from_directory('../frontend', 'index.html')
        elif os.path.exists(f'../frontend/{path}'):
            return serve_from_directory('../frontend', path)
        else:
            return serve_from_directory('../frontend', 'index.html')

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

    return app


def create_demo_admin():
    """Create demo admin user for testing."""
    admin = User.query.filter_by(username='admin').first()

    if not admin:
        admin = User(
            username='admin',
            email='admin@aviator-demo.local',
            balance=10000.0,
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)

    # Create demo regular user
    user = User.query.filter_by(username='demo').first()

    if not user:
        user = User(
            username='demo',
            email='demo@aviator-demo.local',
            balance=500.0,
            is_admin=False
        )
        user.set_password('demo123')
        db.session.add(user)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()


if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=True
    )
