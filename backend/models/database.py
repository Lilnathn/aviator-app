"""
Database initialization and models for Aviator betting application.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for storing user information."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, default=100.0, nullable=False)  # Demo money
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    bets = db.relationship('Bet', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'balance': round(self.balance, 2),
            'created_at': self.created_at.isoformat(),
            'is_admin': self.is_admin
        }


class Transaction(db.Model):
    """Transaction model for logging wallet operations."""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal, bet_loss, bet_win
    amount = db.Column(db.Float, nullable=False)
    balance_before = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    payment_method = db.Column(db.String(50))  # mpesa, mtn, airtel, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.transaction_type,
            'amount': round(self.amount, 2),
            'balance_before': round(self.balance_before, 2),
            'balance_after': round(self.balance_after, 2),
            'description': self.description,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat()
        }


class GameRound(db.Model):
    """Model for tracking each game round."""
    __tablename__ = 'game_rounds'

    id = db.Column(db.Integer, primary_key=True)
    round_number = db.Column(db.Integer, nullable=False, unique=True, index=True)
    crash_point = db.Column(db.Float, nullable=False)  # At what multiplier did it crash
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, crashed, completed

    # Relationships
    bets = db.relationship('Bet', backref='game_round', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        """Convert game round to dictionary."""
        return {
            'id': self.id,
            'round_number': self.round_number,
            'crash_point': round(self.crash_point, 2),
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'status': self.status
        }


class Bet(db.Model):
    """Model for tracking bets placed by users."""
    __tablename__ = 'bets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    game_round_id = db.Column(db.Integer, db.ForeignKey('game_rounds.id'), nullable=False, index=True)
    bet_amount = db.Column(db.Float, nullable=False)
    cash_out_multiplier = db.Column(db.Float, nullable=True)  # Multiplier at which user cashed out
    result = db.Column(db.String(20), default='pending')  # pending, won, lost
    winnings = db.Column(db.Float, default=0.0)  # Amount won (0 if lost)
    placed_at = db.Column(db.DateTime, default=datetime.utcnow)
    cash_out_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        """Convert bet to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'game_round_id': self.game_round_id,
            'bet_amount': round(self.bet_amount, 2),
            'cash_out_multiplier': round(self.cash_out_multiplier, 2) if self.cash_out_multiplier else None,
            'result': self.result,
            'winnings': round(self.winnings, 2),
            'placed_at': self.placed_at.isoformat(),
            'cash_out_at': self.cash_out_at.isoformat() if self.cash_out_at else None
        }


class PaymentLog(db.Model):
    """Model for logging payment API requests and responses (simulated)."""
    __tablename__ = 'payment_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    provider = db.Column(db.String(50), nullable=False)  # mpesa, mtn, airtel, etc.
    transaction_ref = db.Column(db.String(100), unique=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, success, failed
    request_data = db.Column(db.JSON)
    response_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert payment log to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'provider': self.provider,
            'transaction_ref': self.transaction_ref,
            'amount': round(self.amount, 2),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
