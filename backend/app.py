"""
Aviator Betting Application - Flask Backend

🎓 DEMO MODE: School project demonstration.
   Simulation only - no real gambling or real money.

Features:
  • User authentication (JWT-based)
  • Wallet management (deposit, withdraw, transactions)
  • Aviator game with real-time multiplier simulation
  • Admin dashboard and controls
  • Payment API integration structure
  • Single-Page Application (SPA) frontend serving

Deployment:
  • Local: python app.py
  • Render: gunicorn app:app
  • Environment variables handled via os.getenv()
  • Automatic database initialization
  • Demo accounts auto-created on startup
"""

import os
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models.database import db, User
from routes.auth_routes import auth_bp
from routes.wallet_routes import wallet_bp
from routes.game_routes import game_bp
from routes.admin_routes import admin_bp
from services.game_service import GameService


def create_app(config_name=None):
    """
    Application Factory - Creates and configures Flask app.
    
    Args:
        config_name: 'production', 'development', or None (auto-detect)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__, static_folder=None)
    
    # ====== Environment & Configuration ======
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    debug_mode = config_name != 'production'
    app.config['DEBUG'] = debug_mode
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Convert Render's postgresql:// to SQLAlchemy's postgresql+psycopg2://
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Local development: SQLite
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            'sqlite:///aviator_demo.db'
        )
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    # Security
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY',
        'dev-key' if debug_mode else 'change-this-key'
    )
    app.config['JWT_SECRET'] = os.environ.get('JWT_SECRET', app.config['SECRET_KEY'])
    
    # ====== Initialize Extensions ======
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # ====== Register API Blueprints ======
    app.register_blueprint(auth_bp)
    app.register_blueprint(wallet_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(admin_bp)
    
    # ====== Frontend Path ======
    backend_dir = Path(__file__).parent
    frontend_dir = backend_dir.parent / 'frontend'
    
    # ====== Routes: Health & Demo ======
    
    @app.route('/', methods=['GET'])
    def status():
        """Root endpoint - Backend health check."""
        return jsonify({
            'status': 'Aviator backend is running',
            'mode': 'DEMO - Educational simulation',
            'demo_credentials': {
                'admin': 'admin/admin123 ($10,000)',
                'demo_user': 'demo/demo123 ($500)',
                'test_user': 'testuser/testuser123 ($1,000)'
            }
        }), 200
    
    @app.route('/api/health', methods=['GET'])
    def api_health():
        """API health check - for monitoring."""
        return jsonify({
            'success': True,
            'message': 'API is running',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    @app.route('/demo-info', methods=['GET'])
    def demo_info():
        """Demo information endpoint."""
        return jsonify({
            'demo': 'This is a demonstration environment',
            'note': 'No real money - 100% simulation',
            'purpose': 'Educational demo'
        }), 200
    
    # ====== Routes: Frontend SPA ======
    
    @app.route('/app')
    def serve_spa():
        """Serve SPA root (index.html)."""
        if not frontend_dir.exists():
            return jsonify({'error': 'Frontend not found'}), 404
        return send_from_directory(str(frontend_dir), 'index.html')
    
    @app.route('/app/<path:filename>')
    def serve_app_files(filename):
        """Serve SPA files and handle client-side routing."""
        if not frontend_dir.exists():
            return jsonify({'error': 'Frontend not found'}), 404
        
        file_path = frontend_dir / filename
        
        # Serve actual file if it exists
        if file_path.exists() and file_path.is_file():
            return send_from_directory(str(frontend_dir), filename)
        
        # Check for index.html in directory
        if file_path.exists() and file_path.is_dir():
            index_path = file_path / 'index.html'
            if index_path.exists():
                return send_from_directory(str(file_path), 'index.html')
        
        # SPA routing: serve index.html for unknown routes
        return send_from_directory(str(frontend_dir), 'index.html')
    
    @app.route('/assets/<path:filename>')
    def serve_assets_dir(filename):
        """Serve assets from /assets/ directory."""
        if not frontend_dir.exists():
            return jsonify({'error': 'Frontend not found'}), 404
        
        assets_dir = frontend_dir / 'assets'
        if not assets_dir.exists():
            return jsonify({'error': 'Assets not found'}), 404
        
        file_path = assets_dir / filename
        if file_path.exists() and file_path.is_file():
            return send_from_directory(str(assets_dir), filename)
        
        return jsonify({'error': 'Asset not found'}), 404
    
    # ====== Error Handlers ======
    
    @app.errorhandler(404)
    def handle_404(error):
        """Handle 404 errors."""
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Not found'}), 404
        # SPA routing: serve index.html
        if frontend_dir.exists():
            return send_from_directory(str(frontend_dir), 'index.html'), 200
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def handle_500(error):
        """Handle 500 errors."""
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    # ====== Database Setup ======
    with app.app_context():
        db.create_all()
        _create_demo_users()
        try:
            if not GameService.game_state.get('round_id'):
                GameService.start_new_round()
        except Exception as e:
            print(f"Warning: Could not init game: {e}")
    
    return app


def _create_demo_users():
    """Create demo users for testing (admin, demo, testuser)."""
    try:
        # Check and create admin user
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@aviator-demo.local',
                balance=10000.0,
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Check and create demo user
        if not User.query.filter_by(username='demo').first():
            demo = User(
                username='demo',
                email='demo@aviator-demo.local',
                balance=500.0,
                is_admin=False
            )
            demo.set_password('demo123')
            db.session.add(demo)
        
        # Check and create test user
        if not User.query.filter_by(username='testuser').first():
            testuser = User(
                username='testuser',
                email='testuser@aviator-demo.local',
                balance=1000.0,
                is_admin=False
            )
            testuser.set_password('testuser123')
            db.session.add(testuser)
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Warning: Could not create demo users: {e}")


# ============================================================================
# Application Entry Point
# ============================================================================

# Create app instance - used by: gunicorn app:app
app = create_app(os.environ.get('FLASK_ENV', 'development'))


if __name__ == '__main__':
    """
    Local development entry point.
    
    Usage:
        python app.py                     # Run on localhost:5000
        FLASK_ENV=production python app.py  # Production mode
    
    For Render deployment:
        gunicorn app:app
    
    Environment variables:
        FLASK_ENV: 'development' or 'production'
        SECRET_KEY: Security key for sessions
        JWT_SECRET: JWT token signing key
        DATABASE_URL: Database connection (auto-provided by Render for PostgreSQL)
        PORT: Server port (default 5000)
    """
    app.run(
        host='0.0.0.0',  # Required for Render
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
