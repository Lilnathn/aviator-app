"""
Main Flask application for Aviator betting demo.
School project demonstration - simulation only, no real gambling.

This application is designed to run on Render or locally.
All configuration comes from environment variables (.env file).
"""

import os
import json
from datetime import datetime
from flask import Flask, jsonify, serve_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models.database import db, User
from routes.auth_routes import auth_bp
from routes.wallet_routes import wallet_bp
from routes.game_routes import game_bp
from routes.admin_routes import admin_bp
from services.game_service import GameService


def create_app(config_name=None):
    """
    Application factory.
    
    Args:
        config_name: 'production', 'development', or None (auto-detect from env)
    """
    app = Flask(__name__)

    # Auto-detect environment
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    # Configuration from environment variables
    debug_mode = config_name != 'production'
    app.config['DEBUG'] = debug_mode
    
    # Database URL - prioritize PostgreSQL URL for Render, fallback to SQLite
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Render uses postgresql://, but SQLAlchemy expects postgresql+psycopg2://
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to SQLite for local development
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            'sqlite:///aviator_demo.db'
        )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    # Security
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY',
        'dev-secret-key' if debug_mode else 'change-this-in-production'
    )
    app.config['JWT_SECRET'] = os.environ.get(
        'JWT_SECRET',
        app.config['SECRET_KEY']
    )

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(wallet_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(admin_bp)

    # Application routes
    @app.route('/', methods=['GET'])
    def home():
        """Root route - health check for Render deployment."""
        return jsonify({
            'status': 'success',
            'message': 'Aviator Backend is Running',
            'mode': '🎓 DEMO MODE - School Project, Simulation Only',
            'demo_credentials': {
                'admin_user': 'admin',
                'admin_pass': 'admin123',
                'demo_user': 'demo',
                'demo_pass': 'demo123'
            },
            'environment': config_name,
            'timestamp': datetime.utcnow().isoformat(),
            'endpoints': {
                'api_health': '/api/health',
                'auth': '/api/auth/*',
                'wallet': '/api/wallet/*',
                'game': '/api/game/*',
                'admin': '/api/admin/*'
            }
        }), 200

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            'success': True,
            'message': 'Aviator API is running',
            'mode': 'DEMO',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    # Serve frontend static files
    @app.route('/app', methods=['GET'])
    @app.route('/app/<path:path>', methods=['GET'])
    def serve_frontend(path=None):
        """Serve frontend files."""
        try:
            if path is None or path == '':
                return serve_from_directory('../frontend', 'index.html')
            elif os.path.exists(os.path.join('../frontend', path)):
                return serve_from_directory('../frontend', path)
            else:
                return serve_from_directory('../frontend', 'index.html')
        except Exception as e:
            # Fallback to index.html for SPA routing
            return serve_from_directory('../frontend', 'index.html')

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

    # Initialize database
    with app.app_context():
        db.create_all()
        create_demo_users()
        # Initialize game
        if not GameService.game_state['round_id']:
            GameService.start_new_round()

    return app


def create_demo_users():
    """
    Create demo users for testing.
    Adds an admin user and two test users with initial starting balances.
    """
    try:
        # Admin user
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

        # Demo regular user
        demo_user = User.query.filter_by(username='demo').first()
        if not demo_user:
            demo_user = User(
                username='demo',
                email='demo@aviator-demo.local',
                balance=500.0,
                is_admin=False
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)

        # Test user
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='testuser@aviator-demo.local',
                balance=1000.0,
                is_admin=False
            )
            test_user.set_password('testuser123')
            db.session.add(test_user)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Warning: Could not create demo users: {e}")


if __name__ == '__main__':
    """
    Main entry point for running the Flask app.
    Supports both local development and Render deployment.
    """
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
