"""
Wallet service for managing user balance and transactions.
"""

from datetime import datetime
from models.database import db, User, Transaction, PaymentLog


class WalletService:
    """Service for handling wallet operations and transactions."""

    @staticmethod
    def get_balance(user_id):
        """Get current user balance."""
        user = User.query.get(user_id)
        if not user:
            return None
        return round(user.balance, 2)

    @staticmethod
    def deposit(user_id, amount, payment_method='manual'):
        """Deposit demo money into user wallet."""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404

        if amount <= 0:
            return {'success': False, 'message': 'Deposit amount must be positive'}, 400

        if amount > 100000:  # Safety limit for demo
            return {'success': False, 'message': 'Deposit exceeds maximum limit'}, 400

        try:
            balance_before = user.balance

            # Update balance
            user.balance += amount
            user.updated_at = datetime.utcnow()

            # Log transaction
            transaction = Transaction(
                user_id=user_id,
                transaction_type='deposit',
                amount=amount,
                balance_before=balance_before,
                balance_after=user.balance,
                description=f'Deposit via {payment_method}',
                payment_method=payment_method
            )

            db.session.add(transaction)
            db.session.commit()

            return {
                'success': True,
                'message': f'Successfully deposited {amount}',
                'new_balance': round(user.balance, 2),
                'transaction': transaction.to_dict()
            }, 200

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500

    @staticmethod
    def withdraw(user_id, amount, payment_method='manual'):
        """Withdraw demo money from user wallet."""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404

        if amount <= 0:
            return {'success': False, 'message': 'Withdrawal amount must be positive'}, 400

        if amount > user.balance:
            return {'success': False, 'message': 'Insufficient funds'}, 400

        try:
            balance_before = user.balance

            # Update balance
            user.balance -= amount
            user.updated_at = datetime.utcnow()

            # Log transaction
            transaction = Transaction(
                user_id=user_id,
                transaction_type='withdrawal',
                amount=amount,
                balance_before=balance_before,
                balance_after=user.balance,
                description=f'Withdrawal via {payment_method}',
                payment_method=payment_method
            )

            db.session.add(transaction)
            db.session.commit()

            return {
                'success': True,
                'message': f'Successfully withdrew {amount}',
                'new_balance': round(user.balance, 2),
                'transaction': transaction.to_dict()
            }, 200

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500

    @staticmethod
    def get_transactions(user_id, limit=50, offset=0):
        """Get user transaction history."""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404

        try:
            transactions = Transaction.query.filter_by(user_id=user_id) \
                .order_by(Transaction.created_at.desc()) \
                .limit(limit) \
                .offset(offset) \
                .all()

            total = Transaction.query.filter_by(user_id=user_id).count()

            return {
                'success': True,
                'transactions': [t.to_dict() for t in transactions],
                'total': total,
                'limit': limit,
                'offset': offset
            }, 200

        except Exception as e:
            return {'success': False, 'message': str(e)}, 500

    @staticmethod
    def log_payment_attempt(user_id, provider, amount, status, request_data=None, response_data=None):
        """Log payment API attempt for audit trail."""
        try:
            import uuid
            transaction_ref = f"{provider}_{datetime.utcnow().timestamp()}_{uuid.uuid4().hex[:8]}"

            payment_log = PaymentLog(
                user_id=user_id,
                provider=provider,
                transaction_ref=transaction_ref,
                amount=amount,
                status=status,
                request_data=request_data,
                response_data=response_data
            )

            db.session.add(payment_log)
            db.session.commit()

            return transaction_ref
        except Exception as e:
            db.session.rollback()
            return None

    @staticmethod
    def admin_credit_user(user_id, amount, reason='Manual credit'):
        """Admin function to manually credit a user (for demo purposes)."""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404

        if amount <= 0:
            return {'success': False, 'message': 'Credit amount must be positive'}, 400

        try:
            balance_before = user.balance
            user.balance += amount
            user.updated_at = datetime.utcnow()

            transaction = Transaction(
                user_id=user_id,
                transaction_type='admin_credit',
                amount=amount,
                balance_before=balance_before,
                balance_after=user.balance,
                description=reason,
                payment_method='admin'
            )

            db.session.add(transaction)
            db.session.commit()

            return {
                'success': True,
                'message': f'Successfully credited user {amount}',
                'new_balance': round(user.balance, 2)
            }, 200

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500

    @staticmethod
    def admin_debit_user(user_id, amount, reason='Manual debit'):
        """Admin function to manually debit a user balance."""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404

        if amount <= 0:
            return {'success': False, 'message': 'Debit amount must be positive'}, 400

        if amount > user.balance:
            return {'success': False, 'message': 'Cannot debit more than balance'}, 400

        try:
            balance_before = user.balance
            user.balance -= amount
            user.updated_at = datetime.utcnow()

            transaction = Transaction(
                user_id=user_id,
                transaction_type='admin_debit',
                amount=amount,
                balance_before=balance_before,
                balance_after=user.balance,
                description=reason,
                payment_method='admin'
            )

            db.session.add(transaction)
            db.session.commit()

            return {
                'success': True,
                'message': f'Successfully debited user {amount}',
                'new_balance': round(user.balance, 2)
            }, 200

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500
