"""
Game service for Aviator game logic and game round management.
"""

import random
import math
from datetime import datetime
from models.database import db, User, GameRound, Bet, Transaction


class GameService:
    """Service for managing Aviator game rounds and betting."""

    # Game state
    current_round = None
    game_state = {
        'round_id': None,
        'multiplier': 1.0,
        'crash_point': None,
        'is_active': False,
        'crashed': False
    }

    @staticmethod
    def generate_crash_point():
        """
        Generate a random crash point using exponential distribution.
        Most games crash early, fewer crash late (realistic Aviator behavior).
        """
        # Use exponential distribution skewed towards lower multipliers
        seed = random.random()
        # Exponential distribution: crash_point = ln(1/(1-seed))
        if seed >= 0.99:
            crash_point = random.uniform(100, 500)
        elif seed >= 0.95:
            crash_point = random.uniform(20, 100)
        elif seed >= 0.80:
            crash_point = random.uniform(5, 20)
        else:
            crash_point = random.uniform(1.0, 5.0)

        return round(crash_point, 2)

    @staticmethod
    def start_new_round():
        """Start a new game round."""
        try:
            # Get the latest round number
            last_round = GameRound.query.order_by(GameRound.round_number.desc()).first()
            next_round_number = (last_round.round_number + 1) if last_round else 1

            # Generate crash point
            crash_point = GameService.generate_crash_point()

            # Create new game round
            game_round = GameRound(
                round_number=next_round_number,
                crash_point=crash_point,
                status='active'
            )

            db.session.add(game_round)
            db.session.commit()

            # Update game state
            GameService.game_state = {
                'round_id': game_round.id,
                'round_number': next_round_number,
                'multiplier': 1.0,
                'crash_point': crash_point,
                'is_active': True,
                'crashed': False,
                'started_at': datetime.utcnow().isoformat()
            }

            return game_round
        except Exception as e:
            db.session.rollback()
            return None

    @staticmethod
    def place_bet(user_id, amount):
        """Place a bet on current round."""
        if not GameService.game_state['is_active']:
            return {'success': False, 'message': 'No active game round'}, 400

        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404

        if amount <= 0:
            return {'success': False, 'message': 'Bet amount must be positive'}, 400

        if amount > user.balance:
            return {'success': False, 'message': 'Insufficient balance'}, 400

        if amount > 10000:  # Safety limit
            return {'success': False, 'message': 'Bet exceeds maximum limit'}, 400

        try:
            # Deduct bet amount from balance
            balance_before = user.balance
            user.balance -= amount
            user.updated_at = datetime.utcnow()

            # Create bet record
            bet = Bet(
                user_id=user_id,
                game_round_id=GameService.game_state['round_id'],
                bet_amount=amount,
                result='pending'
            )

            # Log transaction
            transaction = Transaction(
                user_id=user_id,
                transaction_type='bet_placed',
                amount=amount,
                balance_before=balance_before,
                balance_after=user.balance,
                description=f'Bet placed on round {GameService.game_state["round_number"]}',
                payment_method='game'
            )

            db.session.add(bet)
            db.session.add(transaction)
            db.session.commit()

            return {
                'success': True,
                'message': 'Bet placed successfully',
                'bet': bet.to_dict(),
                'new_balance': round(user.balance, 2)
            }, 200

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500

    @staticmethod
    def cash_out(user_id, bet_id):
        """Cash out from a bet at current multiplier."""
        bet = Bet.query.get(bet_id)
        if not bet:
            return {'success': False, 'message': 'Bet not found'}, 404

        if bet.user_id != user_id:
            return {'success': False, 'message': 'Unauthorized'}, 403

        if bet.result != 'pending':
            return {'success': False, 'message': f'Bet already {bet.result}'}, 400

        if not GameService.game_state['is_active']:
            return {'success': False, 'message': 'Game round not active'}, 400

        try:
            current_multiplier = GameService.game_state['multiplier']
            
            # Check if already crashed
            if GameService.game_state['crashed']:
                return {'success': False, 'message': 'Game already crashed'}, 400

            # Calculate winnings
            winnings = bet.bet_amount * current_multiplier
            winnings = round(winnings, 2)

            # Update bet
            bet.result = 'won'
            bet.cash_out_multiplier = current_multiplier
            bet.winnings = winnings
            bet.cash_out_at = datetime.utcnow()

            # Update user balance
            user = User.query.get(user_id)
            balance_before = user.balance
            user.balance += winnings
            user.updated_at = datetime.utcnow()

            # Log transaction
            transaction = Transaction(
                user_id=user_id,
                transaction_type='bet_win',
                amount=winnings,
                balance_before=balance_before,
                balance_after=user.balance,
                description=f'Bet won at {current_multiplier}x multiplier on round {GameService.game_state["round_number"]}',
                payment_method='game'
            )

            db.session.add(transaction)
            db.session.commit()

            return {
                'success': True,
                'message': f'Successfully cashed out at {current_multiplier}x',
                'winnings': winnings,
                'new_balance': round(user.balance, 2),
                'bet': bet.to_dict()
            }, 200

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500

    @staticmethod
    def process_crash():
        """Process crash and close all pending bets."""
        if not GameService.game_state['is_active']:
            return {'success': False, 'message': 'No active game'}, 400

        try:
            # Get all pending bets for current round
            pending_bets = Bet.query.filter_by(
                game_round_id=GameService.game_state['round_id'],
                result='pending'
            ).all()

            # Mark all as lost
            for bet in pending_bets:
                bet.result = 'lost'
                bet.cash_out_at = datetime.utcnow()

            # Update game round
            game_round = GameRound.query.get(GameService.game_state['round_id'])
            game_round.status = 'crashed'
            game_round.ended_at = datetime.utcnow()

            # Update game state
            GameService.game_state['is_active'] = False
            GameService.game_state['crashed'] = True

            db.session.commit()

            return {
                'success': True,
                'message': 'Game crashed',
                'crash_point': GameService.game_state['crash_point'],
                'lost_bets': len(pending_bets)
            }, 200

        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}, 500

    @staticmethod
    def update_multiplier(elapsed_seconds):
        """Update current multiplier based on elapsed time."""
        if not GameService.game_state['is_active']:
            return None

        # Multiplier growth formula: 1 + (elapsed_time * growth_rate)^2
        growth_rate = 0.08  # Adjust to control speed
        multiplier = 1.0 + (elapsed_seconds * growth_rate) ** 1.5

        GameService.game_state['multiplier'] = round(multiplier, 2)

        # Check if crashed
        if multiplier >= GameService.game_state['crash_point']:
            GameService.process_crash()
            return GameService.game_state['crash_point']

        return multiplier

    @staticmethod
    def get_game_state():
        """Get current game state."""
        return GameService.game_state

    @staticmethod
    def get_game_history(limit=20):
        """Get recent game history."""
        try:
            rounds = GameRound.query.order_by(GameRound.round_number.desc()) \
                .limit(limit).all()
            return {
                'success': True,
                'rounds': [r.to_dict() for r in rounds]
            }, 200
        except Exception as e:
            return {'success': False, 'message': str(e)}, 500

    @staticmethod
    def get_user_round_info(user_id):
        """Get user's info about current round (bets, balance, etc.)."""
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'User not found'}, 404

        try:
            # Get user's bet in current round if exists
            current_bet = None
            if GameService.game_state['is_active']:
                current_bet = Bet.query.filter_by(
                    user_id=user_id,
                    game_round_id=GameService.game_state['round_id']
                ).first()

            return {
                'success': True,
                'balance': round(user.balance, 2),
                'current_bet': current_bet.to_dict() if current_bet else None,
                'game_state': GameService.game_state
            }, 200
        except Exception as e:
            return {'success': False, 'message': str(e)}, 500
