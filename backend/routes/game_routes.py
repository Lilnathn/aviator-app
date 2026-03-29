"""
Game routes for Aviator game operations.
"""

from flask import Blueprint, request, jsonify
from services.auth_service import token_required
from services.game_service import GameService

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
