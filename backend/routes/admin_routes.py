"""
Admin routes for demo control panel and management operations.
"""

from flask import Blueprint, request, jsonify
from services.auth_service import token_required, admin_required
from services.wallet_service import WalletService
from models.database import db, User, Transaction, GameRound, Bet, PaymentLog

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/dashboard', methods=['GET'])
@token_required
@admin_required
def get_dashboard():
    """Get admin dashboard statistics."""
    try:
        total_users = User.query.count()
        total_balance = db.session.query(db.func.sum(User.balance)).scalar() or 0
        total_transactions = Transaction.query.count()
        total_games = GameRound.query.count()
        
        # Get active game info
        from services.game_service import GameService
        active_game = GameService.game_state

        return jsonify({
            'success': True,
            'statistics': {
                'total_users': total_users,
                'total_balance': round(total_balance, 2),
                'total_transactions': total_transactions,
                'total_games': total_games,
                'active_game': active_game
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def list_users():
    """List all users with pagination."""
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)

    if limit > 100:
        limit = 100

    try:
        users = User.query.order_by(User.created_at.desc()).limit(limit).offset(offset).all()
        total = User.query.count()

        return jsonify({
            'success': True,
            'users': [u.to_dict() for u in users],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
@admin_required
def get_user(user_id):
    """Get detailed user information."""
    try:
        user = User.query.get(user_id)

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        # Get user statistics
        total_bets = Bet.query.filter_by(user_id=user_id).count()
        won_bets = Bet.query.filter_by(user_id=user_id, result='won').count()
        lost_bets = Bet.query.filter_by(user_id=user_id, result='lost').count()
        total_transactions = Transaction.query.filter_by(user_id=user_id).count()

        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'statistics': {
                'total_bets': total_bets,
                'won_bets': won_bets,
                'lost_bets': lost_bets,
                'total_transactions': total_transactions
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/users/<int:user_id>/credit', methods=['POST'])
@token_required
@admin_required
def credit_user(user_id):
    """Manually credit a user (demo admin function)."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    amount = data.get('amount')
    reason = data.get('reason', 'Admin credit')

    if not amount:
        return jsonify({'success': False, 'message': 'Amount required'}), 400

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid amount'}), 400

    result, status_code = WalletService.admin_credit_user(user_id, amount, reason)
    return jsonify(result), status_code


@admin_bp.route('/users/<int:user_id>/debit', methods=['POST'])
@token_required
@admin_required
def debit_user(user_id):
    """Manually debit a user (demo admin function)."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    amount = data.get('amount')
    reason = data.get('reason', 'Admin debit')

    if not amount:
        return jsonify({'success': False, 'message': 'Amount required'}), 400

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid amount'}), 400

    result, status_code = WalletService.admin_debit_user(user_id, amount, reason)
    return jsonify(result), status_code


@admin_bp.route('/transactions', methods=['GET'])
@token_required
@admin_required
def list_transactions():
    """List all transactions with filtering."""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    transaction_type = request.args.get('type', None)

    if limit > 100:
        limit = 100

    try:
        query = Transaction.query

        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)

        transactions = query.order_by(Transaction.created_at.desc()).limit(limit).offset(offset).all()
        total = query.count()

        return jsonify({
            'success': True,
            'transactions': [t.to_dict() for t in transactions],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/games', methods=['GET'])
@token_required
@admin_required
def list_games():
    """List all game rounds."""
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)

    if limit > 100:
        limit = 100

    try:
        games = GameRound.query.order_by(GameRound.round_number.desc()).limit(limit).offset(offset).all()
        total = GameRound.query.count()

        return jsonify({
            'success': True,
            'games': [g.to_dict() for g in games],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/games/<int:game_id>', methods=['GET'])
@token_required
@admin_required
def get_game(game_id):
    """Get detailed game information with all bets."""
    try:
        game = GameRound.query.get(game_id)

        if not game:
            return jsonify({'success': False, 'message': 'Game not found'}), 404

        bets = Bet.query.filter_by(game_round_id=game_id).all()

        total_wagered = sum(b.bet_amount for b in bets)
        total_won = sum(b.winnings for b in bets if b.result == 'won')
        total_lost = len([b for b in bets if b.result == 'lost'])

        return jsonify({
            'success': True,
            'game': game.to_dict(),
            'bets': [b.to_dict() for b in bets],
            'statistics': {
                'total_bets': len(bets),
                'total_wagered': round(total_wagered, 2),
                'total_won': round(total_won, 2),
                'total_lost': total_lost
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/payments', methods=['GET'])
@token_required
@admin_required
def list_payments():
    """List payment logs."""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    status = request.args.get('status', None)

    if limit > 100:
        limit = 100

    try:
        query = PaymentLog.query

        if status:
            query = query.filter_by(status=status)

        payments = query.order_by(PaymentLog.created_at.desc()).limit(limit).offset(offset).all()
        total = query.count()

        return jsonify({
            'success': True,
            'payments': [p.to_dict() for p in payments],
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/export/users', methods=['GET'])
@token_required
@admin_required
def export_users():
    """Export all users as JSON."""
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [u.to_dict() for u in users]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/export/transactions', methods=['GET'])
@token_required
@admin_required
def export_transactions():
    """Export all transactions as JSON."""
    try:
        transactions = Transaction.query.all()
        return jsonify({
            'success': True,
            'data': [t.to_dict() for t in transactions]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
