"""
Payment service for handling deposits through various African payment providers.
Includes simulated transactions and placeholders for real API integration.
"""

import random
import string
from datetime import datetime
from services.wallet_service import WalletService
from models.database import db


class PaymentService:
    """Service for handling payment operations through various providers."""

    # Simulated payment providers
    PROVIDERS = {
        'mpesa': {'name': 'M-Pesa (Kenya)', 'min': 1, 'max': 70000},
        'mtn': {'name': 'MTN Mobile Money', 'min': 1, 'max': 10000},
        'airtel': {'name': 'Airtel Money', 'min': 1, 'max': 10000},
        'tigo': {'name': 'Tigo Pesa (Tanzania)', 'min': 1, 'max': 5000},
        'rwmomo': {'name': 'MTN MoMo (Rwanda)', 'min': 1, 'max': 5000},
        'zambia': {'name': 'MTN/Airtel (Zambia)', 'min': 1, 'max': 5000},
    }

    @staticmethod
    def initiate_deposit(user_id, amount, provider, phone_number):
        """
        Initiate a payment deposit through specified provider.
        For demo: simulates success with configurable failure rate.
        """
        if provider not in PaymentService.PROVIDERS:
            return {'success': False, 'message': 'Invalid payment provider'}, 400

        provider_info = PaymentService.PROVIDERS[provider]

        if amount < provider_info['min'] or amount > provider_info['max']:
            return {
                'success': False,
                'message': f"Amount must be between {provider_info['min']} and {provider_info['max']}"
            }, 400

        try:
            # Log the payment attempt
            transaction_ref = WalletService.log_payment_attempt(
                user_id=user_id,
                provider=provider,
                amount=amount,
                status='pending',
                request_data={
                    'phone_number': phone_number,
                    'amount': amount,
                    'provider': provider
                }
            )

            if not transaction_ref:
                return {'success': False, 'message': 'Failed to log payment'}, 500

            # For DEMO: Simulate API response
            # In production: Call the actual provider API
            success = PaymentService._simulate_payment(provider, amount)

            if success:
                # Payment successful - credit user
                result, status_code = WalletService.deposit(
                    user_id=user_id,
                    amount=amount,
                    payment_method=provider
                )

                # Update payment log
                PaymentService._update_payment_log(
                    transaction_ref,
                    'success',
                    {'status': 'SUCCESS', 'message': 'Payment processed successfully'}
                )

                return {
                    'success': True,
                    'message': f'Payment received! {amount} added to balance',
                    'transaction_ref': transaction_ref,
                    'new_balance': result.get('new_balance'),
                    'provider': provider_info['name']
                }, 200
            else:
                # Payment failed
                PaymentService._update_payment_log(
                    transaction_ref,
                    'failed',
                    {'status': 'FAILED', 'message': 'Payment processing failed'}
                )

                return {
                    'success': False,
                    'message': 'Payment processing failed. Please try again.',
                    'transaction_ref': transaction_ref
                }, 400

        except Exception as e:
            return {'success': False, 'message': str(e)}, 500

    @staticmethod
    def _simulate_payment(provider, amount):
        """
        Simulate payment processing.
        For demo: 90% success rate to make demo realistic.
        """
        # 10% failure rate for realism
        failure_rate = 0.10
        return random.random() > failure_rate

    @staticmethod
    def _update_payment_log(transaction_ref, status, response_data):
        """Update payment log with response data."""
        from models.database import PaymentLog
        try:
            log = PaymentLog.query.filter_by(transaction_ref=transaction_ref).first()
            if log:
                log.status = status
                log.response_data = response_data
                log.updated_at = datetime.utcnow()
                db.session.commit()
        except Exception as e:
            db.session.rollback()

    @staticmethod
    def get_providers():
        """Get list of available payment providers."""
        return {
            'success': True,
            'providers': [
                {
                    'id': provider_id,
                    'name': info['name'],
                    'min_amount': info['min'],
                    'max_amount': info['max'],
                    'currency': PaymentService._get_currency(provider_id)
                }
                for provider_id, info in PaymentService.PROVIDERS.items()
            ]
        }, 200

    @staticmethod
    def _get_currency(provider_id):
        """Get currency for provider."""
        currencies = {
            'mpesa': 'KES',
            'mtn': 'Various',
            'airtel': 'Various',
            'tigo': 'TZS',
            'rwmomo': 'RWF',
            'zambia': 'ZMW'
        }
        return currencies.get(provider_id, 'Unknown')


# ============================================================================
# REAL API INTEGRATION PLACEHOLDERS
# ============================================================================
# These are templates for integrating with real payment providers.
# Uncomment and implement when deploying with real payments.
# ============================================================================


class MPesaPaymentProvider:
    """
    M-Pesa Daraja API Integration (Kenya)
    
    Documentation: https://developer.safaricom.co.ke/
    """

    def __init__(self, api_key=None, api_secret=None, business_shortcode=None):
        """Initialize M-Pesa provider with credentials."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.business_shortcode = business_shortcode
        self.base_url = "https://sandbox.safaricom.co.ke"  # Use prod URL in production
        self.oauth_token = None

    def get_access_token(self):
        """
        Get OAuth token from M-Pesa.
        
        Implementation needed:
        - Use basic auth with API key and secret
        - Call /oauth/v1/generate endpoint
        - Cache token (valid for 1 hour)
        """
        pass

    def stk_push(self, phone_number, amount, account_reference):
        """
        Initiate STK Push for payment.
        
        Implementation needed:
        - Call /mpesa/stkpush/v1/processrequest endpoint
        - Handle callback from M-Pesa webhook
        - Update payment log with response
        """
        pass

    def query_transaction_status(self, checkout_request_id):
        """
        Query transaction status.
        
        Implementation needed:
        - Call /mpesa/stkpushquery/v1/query endpoint
        - Return transaction status
        """
        pass


class MTNMoneyProvider:
    """
    MTN Mobile Money API Integration (Multiple African countries)
    
    Documentation: https://mtn-api-documentation.stoplight.io/
    """

    def __init__(self, api_key=None, api_user=None, target_environment=None):
        """Initialize MTN provider with credentials."""
        self.api_key = api_key
        self.api_user = api_user
        self.target_environment = target_environment or 'sandbox'
        self.base_url = f"https://api.sandbox.mtn.com" if target_environment == 'sandbox' else "https://api.mtn.com"

    def request_to_pay(self, phone_number, amount, external_id, payer_message):
        """
        Request payment from user.
        
        Implementation needed:
        - POST to /collection/v1_0/requesttopay endpoint
        - Include transaction ID in response
        - Setup webhook for payment confirmation
        """
        pass

    def get_transaction_status(self, transaction_id):
        """
        Check payment transaction status.
        
        Implementation needed:
        - GET /collection/v1_0/requesttopay/{transaction_id}
        - Return payment status (PENDING, SUCCESSFUL, FAILED)
        """
        pass


class AirtelMoneyProvider:
    """
    Airtel Money API Integration (Tanzania, Uganda, Rwanda, Zambia)
    
    Documentation: https://www.airtel.com/about-us/partners/api
    """

    def __init__(self, merchant_code=None, consumer_key=None, consumer_secret=None):
        """Initialize Airtel provider with credentials."""
        self.merchant_code = merchant_code
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_url = "https://api.airtel.ug"  # Adjust for country

    def initiate_payment(self, phone_number, amount, order_id):
        """
        Initiate payment request.
        
        Implementation needed:
        - POST to /merchant/v2/payments/ endpoint
        - Include transaction ID
        - Setup polling or webhook for confirmation
        """
        pass

    def get_payment_status(self, transaction_id):
        """
        Get payment status.
        
        Implementation needed:
        - Query transaction by ID
        - Return status and details
        """
        pass


class TigoMoneyProvider:
    """
    Tigo Pesa API Integration (Tanzania)
    
    Documentation: Available through Tigo Money business portal
    """

    def __init__(self, api_credentials=None):
        """Initialize Tigo provider."""
        self.api_credentials = api_credentials
        self.base_url = "https://api.tigo.tz"

    def initiate_checkout(self, phone_number, amount, order_id):
        """
        Initiate Tigo payment.
        
        Implementation needed:
        - Create checkout session
        - Return redirect URL to payment page
        - Handle callback after payment
        """
        pass


class GenericPaymentProvider:
    """
    Generic template for adding new payment providers.
    Copy and modify for additional providers.
    """

    def __init__(self, api_key=None, api_secret=None):
        """Initialize generic provider."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = None

    def initiate_payment(self, phone_number, amount, order_id):
        """
        Initiate payment.
        
        Steps:
        1. Validate input
        2. Generate transaction ID
        3. Call provider API
        4. Log request and response
        5. Return transaction reference or error
        """
        pass

    def verify_payment(self, transaction_id):
        """
        Verify payment status.
        
        Steps:
        1. Query provider API
        2. Get transaction status
        3. Update local database if needed
        4. Return confirmed or failed
        """
        pass

    def handle_webhook(self, webhook_data):
        """
        Handle payment confirmation webhook.
        
        Steps:
        1. Verify webhook signature
        2. Validate data
        3. Update transaction status
        4. Credit user balance if successful
        5. Return confirmation
        """
        pass
