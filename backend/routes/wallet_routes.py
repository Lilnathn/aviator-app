"""
Wallet routes for balance operations and transaction history.
"""

from flask import Blueprint, request, jsonify
from services.auth_service import token_required
from services.wallet_service import WalletService
from services.payment_service import PaymentService

wallet_bp = Blueprint('wallet', __name__, url_prefix='/api/wallet')


@wallet_bp.route('/balance', methods=['GET'])
@token_required
def get_balance():
    """Get current user balance."""
    balance = WalletService.get_balance(request.current_user.id)
    return jsonify({
        'success': True,
        'balance': balance,
        'user_id': request.current_user.id
    }), 200


@wallet_bp.route('/deposit', methods=['POST'])
@token_required
def deposit():
    """Deposit demo money using simulated payment."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    amount = data.get('amount')
    provider = data.get('provider', 'manual')
    phone_number = data.get('phone_number', '')

    if not amount:
        return jsonify({'success': False, 'message': 'Amount required'}), 400

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid amount'}), 400

    # For demo: accept all providers, use PaymentService to simulate
    result, status_code = PaymentService.initiate_deposit(
        user_id=request.current_user.id,
        amount=amount,
        provider=provider,
        phone_number=phone_number
    )

    return jsonify(result), status_code


@wallet_bp.route('/withdraw', methods=['POST'])
@token_required
def withdraw():
    """Request withdrawal of demo money."""
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    amount = data.get('amount')
    method = data.get('method', 'manual')

    if not amount:
        return jsonify({'success': False, 'message': 'Amount required'}), 400

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid amount'}), 400

    result, status_code = WalletService.withdraw(
        user_id=request.current_user.id,
        amount=amount,
        payment_method=method
    )

    return jsonify(result), status_code


@wallet_bp.route('/transactions', methods=['GET'])
@token_required
def get_transactions():
    """Get user transaction history."""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Validate limits
    if limit > 100:
        limit = 100
    if offset < 0:
        offset = 0

    result, status_code = WalletService.get_transactions(
        user_id=request.current_user.id,
        limit=limit,
        offset=offset
    )

    return jsonify(result), status_code


@wallet_bp.route('/providers', methods=['GET'])
def get_payment_providers():
    """Get list of available payment providers."""
    result, status_code = PaymentService.get_providers()
    return jsonify(result), status_code
