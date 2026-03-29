"""
Game routes for Aviator game operations.
Demo-friendly routes for school presentation.
"""

from flask import Blueprint, request, jsonify
from services.auth_service import token_required, admin_required
from services.game_service import GameService
from models.database import db, Bet

game_bp = Blueprint('game', __name__, url_prefix='/api/game')


@game_bp.route('/start', methods=['POST'])
def start_game():
    """Start a new game round (admin/system route)."""
    game_round = GameService.start_new_round()

    if not game_round:
        return jsonify({'success': False, 'message': 'Failed to start game'}), 500

    return jsonify({
        'success': True,
        'message': 'Game started',
        'game': GameService.game_state
    }), 200


@game_bp.route('/state', methods=['GET'])
def get_game_state():
    """Get current game state."""
    return jsonify({
        'success': True,
        'game': GameService.get_game_state()
    }), 200


@game_bp.route('/bet', methods=['POST'])
@token_required
def place_bet():
    """Place a bet on the current game."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    amount = data.get('amount')

    if not amount:
        return jsonify({'success': False, 'message': 'Bet amount required'}), 400

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid amount'}), 400

    result, status_code = GameService.place_bet(request.current_user.id, amount)
    return jsonify(result), status_code


@game_bp.route('/cashout', methods=['POST'])
@token_required
def cash_out():
    """Cash out from current bet."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    bet_id = data.get('bet_id')

    if not bet_id:
        return jsonify({'success': False, 'message': 'Bet ID required'}), 400

    result, status_code = GameService.cash_out(request.current_user.id, bet_id)
    return jsonify(result), status_code


@game_bp.route('/crash', methods=['POST'])
def trigger_crash():
    """Trigger game crash (system route, normally triggered automatically)."""
    result, status_code = GameService.process_crash()
    return jsonify(result), status_code


@game_bp.route('/history', methods=['GET'])
def get_history():
    """Get game history."""
    limit = request.args.get('limit', 20, type=int)

    if limit > 100:
        limit = 100

    result, status_code = GameService.get_game_history(limit)
    return jsonify(result), status_code


@game_bp.route('/info', methods=['GET'])
@token_required
def get_user_game_info():
    """Get user's info about current round."""
    result, status_code = GameService.get_user_round_info(request.current_user.id)
    return jsonify(result), status_code


@game_bp.route('/update-multiplier', methods=['POST'])
def update_multiplier():
    """Update game multiplier (called by frontend polling)."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    elapsed_seconds = data.get('elapsed_seconds', 0)

    try:
        elapsed_seconds = float(elapsed_seconds)
    except (ValueError, TypeError):
        elapsed_seconds = 0

    multiplier = GameService.update_multiplier(elapsed_seconds)

    if multiplier is None:
        return jsonify({
            'success': False,
            'message': 'No active game'
        }), 400

    return jsonify({
        'success': True,
        'multiplier': GameService.game_state['multiplier'],
        'crashed': GameService.game_state['crashed'],
        'crash_point': GameService.game_state['crash_point'] if GameService.game_state['crashed'] else None
    }), 200


# ============================================================================
# DEMO-ONLY ROUTES FOR SCHOOL PRESENTATION
# These routes make it easy to demonstrate the game during presentations
# ============================================================================

@game_bp.route('/demo/force-crash', methods=['POST'])
@token_required
@admin_required
def demo_force_crash():
    """
    Demo route: Force the current game to crash immediately.
    Admin only. Used for school demonstrations.
    """
    result, status_code = GameService.process_crash()
    return jsonify({
        'success': True,
        'message': 'Game crashed (DEMO)',
        'crash_point': GameService.game_state['crash_point']
    }), 200


@game_bp.route('/demo/force-win/<int:bet_id>', methods=['POST'])
@token_required
@admin_required
def demo_force_win(bet_id):
    """
    Demo route: Force a specific bet to win with a multiplier.
    Admin only. Used for school demonstrations to show winning scenarios.
    """
    try:
        bet = Bet.query.get(bet_id)
        if not bet:
            return jsonify({'success': False, 'message': 'Bet not found'}), 404

        # Get cash out multiplier from request
        data = request.get_json() or {}
        multiplier = float(data.get('multiplier', 1.5))

        # Calculate winnings
        winnings = bet.bet_amount * multiplier

        # Update bet with manual win
        bet.cash_out_multiplier = multiplier
        bet.result = 'won'
        bet.winnings = winnings

        # Credit user
        bet.user.balance += winnings

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Bet {bet_id} forced to win (DEMO)',
            'bet_id': bet_id,
            'multiplier': multiplier,
            'winnings': winnings
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@game_bp.route('/demo/force-lose/<int:bet_id>', methods=['POST'])
@token_required
@admin_required
def demo_force_lose(bet_id):
    """
    Demo route: Force a specific bet to lose.
    Admin only. Used for school demonstrations to show losing scenarios.
    """
    try:
        bet = Bet.query.get(bet_id)
        if not bet:
            return jsonify({'success': False, 'message': 'Bet not found'}), 404

        # Mark bet as lost
        bet.result = 'lost'
        bet.winnings = 0
        bet.cash_out_multiplier = None

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Bet {bet_id} forced to lose (DEMO)',
            'bet_id': bet_id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@game_bp.route('/demo/set-multiplier/<float:multiplier>', methods=['POST'])
@token_required
@admin_required
def demo_set_multiplier(multiplier):
    """
    Demo route: Manually set the current multiplier value.
    Admin only. Useful for testing or demonstration purposes.
    The game will crash if the multiplier reaches the crash point.
    """
    try:
        multiplier = float(multiplier)
        if multiplier < 1.0:
            multiplier = 1.0
        if multiplier > 10000:
            multiplier = 10000

        GameService.game_state['multiplier'] = multiplier

        return jsonify({
            'success': True,
            'message': f'Multiplier set to {multiplier}x (DEMO)',
            'multiplier': multiplier,
            'crash_point': GameService.game_state['crash_point']
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
