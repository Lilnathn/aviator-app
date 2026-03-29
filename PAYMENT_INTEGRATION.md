# API Integration Guide
## Integrating Real Payment Providers

This guide helps you integrate real payment providers for African markets.

---

## M-Pesa Daraja API (Kenya)

### 1. Get Credentials
- Visit https://developer.safaricom.co.ke/
- Create account and app
- Get Consumer Key and Secret
- Get your Business Shortcode
- Get Passkey
- Generate Access Token

### 2. Setup in Code

```python
# backend/services/payment_service.py

class MPesaPaymentProvider:
    def __init__(self):
        self.consumer_key = os.getenv('MPESA_API_KEY')
        self.consumer_secret = os.getenv('MPESA_API_SECRET')
        self.business_shortcode = os.getenv('MPESA_BUSINESS_SHORTCODE')
        self.pass_key = os.getenv('MPESA_PASS_KEY')
        self.base_url = "https://api.safaricom.co.ke"  # Production URL
        
    def get_access_token(self):
        """Get OAuth token"""
        auth = HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        response = requests.get(
            f"{self.base_url}/oauth/v1/generate",
            auth=auth
        )
        return response.json()['access_token']
    
    def stk_push(self, phone_number, amount):
        """Initiate STK Push"""
        token = self.get_access_token()
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Create password: shortcode + passkey + timestamp (Base64)
        password = base64.b64encode(
            f"{self.business_shortcode}{self.pass_key}{timestamp}".encode()
        ).decode()
        
        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://yourdomain.com/api/payment/callback/mpesa",
            "AccountReference": f"User{user_id}",
            "TransactionDesc": "Aviator Game Deposit"
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{self.base_url}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers
        )
        
        return response.json()
```

### 3. Test
```bash
# Use Safaricom test numbers during sandbox testing
# Phone: 254708374149
# Then check callback for payment status
```

---

## MTN Mobile Money (Multi-Country)

### Supported Countries
- Cameroon (CM)
- Côte d'Ivoire (CI)
- Ghana (GH)
- Guinea (GN)
- Guinea-Bissau (GW)
- Rwanda (RW)
- Uganda (UG)
- Zambia (ZM)

### 1. Setup

```python
class MTNMoneyProvider:
    def __init__(self, country_code='UG'):
        self.api_key = os.getenv('MTN_API_KEY')
        self.api_user = os.getenv('MTN_API_USER')
        
        # URL mapping by country
        urls = {
            'UG': 'https://api.sandbox.mtn.com',  # Uganda
            'RW': 'https://api.sandbox.mtn.com',  # Rwanda
            'ZM': 'https://api.sandbox.mtn.com',  # Zambia
        }
        
        self.base_url = urls.get(country_code, 'https://api.sandbox.mtn.com')
    
    def request_to_pay(self, phone_number, amount):
        """Request payment from user"""
        import uuid
        
        headers = {
            'Content-Type': 'application/json',
            'X-Reference-Id': str(uuid.uuid4()),
            'Authorization': f'Bearer {self.api_key}',
            'X-Target-Environment': 'sandbox'
        }
        
        payload = {
            "amount": str(amount),
            "currency": "UGX",  # Adjust per country
            "externalId": f"User{user_id}",
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone_number
            },
            "payerMessage": "Pay for Aviator Game",
            "payeeNote": "Aviator Deposit"
        }
        
        response = requests.post(
            f"{self.base_url}/collection/v1_0/requesttopay",
            json=payload,
            headers=headers
        )
        
        return response.headers.get('X-Reference-Id')
```

---

## Airtel Money (Tanzania, Uganda, Rwanda, Zambia)

### 1. Integration

```python
class AirtelMoneyProvider:
    def __init__(self):
        self.merchant_code = os.getenv('AIRTEL_MERCHANT_CODE')
        self.consumer_key = os.getenv('AIRTEL_CONSUMER_KEY')
        self.consumer_secret = os.getenv('AIRTEL_CONSUMER_SECRET')
        self.base_url = "https://api.airtel.ug"  # Adjust per country
    
    def initiate_payment(self, phone_number, amount, user_id):
        """Initiate Airtel payment"""
        # Airtel uses OAuth2
        auth_result = self._get_oauth_token()
        token = auth_result['access_token']
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        payload = {
            "reference": f"User{user_id}",
            "subscriber": {
                "country": "TZ",  # or UG, RW, ZM
                "currency": "TZS",  # Adjust per country
                "msisdn": phone_number
            },
            "transaction": {
                "amount": amount,
                "country": "TZ",
                "currency": "TZS",
                "id": f"AV{user_id}{int(time.time())}",
                "type": "MerchantPayment"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/merchant/v2/payments/",
            json=payload,
            headers=headers
        )
        
        return response.json()
```

---

## Setting Up Webhooks

### Webhook Handler Example

```python
# In backend/routes/payment_routes.py

@app.route('/api/payment/callback/mpesa', methods=['POST'])
def mpesa_callback():
    """Handle M-Pesa callback"""
    data = request.get_json()
    
    # Verify callback signature if provided
    transaction_ref = data['MerchantRequestID']
    result_code = data['ResultCode']
    
    if result_code == 0:  # Success
        # Extract amount and phone
        amount = data['CallbackMetadata']['Item'][0]['Value']
        phone = data['CallbackMetadata']['Item'][1]['Value']
        
        # Credit user
        user = User.query.filter_by(phone=phone).first()
        if user:
            WalletService.deposit(user.id, amount, 'mpesa')
    
    # Always return 200 to acknowledge receipt
    return jsonify({'ResultCode': 0}), 200

@app.route('/api/payment/callback/mtn', methods=['POST'])
def mtn_callback():
    """Handle MTN callback"""
    data = request.get_json()
    
    if data['status'] == 'SUCCESSFUL':
        # Process payment
        pass
    
    return jsonify({'status': 'received'}), 200
```

---

## Testing Payment Integration

### 1. Sandbox Testing
- Always use sandbox URLs for testing
- Use test phone numbers provided by provider
- Don't use real money

### 2. Test Cases

```python
# Test cases to verify
1. User deposits $100
   - Check balance increases
   - Check transaction logged
   - Check payment logs recorded

2. User deposits with invalid phone
   - Check error message
   - Check balance unchanged

3. Payment timeout
   - Check retry logic
   - Check user informed

4. Currency conversion (if applicable)
   - Check correct amount after conversion
   - Check rates updated
```

---

## Switching to Production

### Checklist
- [ ] Change all sandbox URLs to production URLs
- [ ] Update credentials in environment variables
- [ ] Enable webhook signature verification
- [ ] Setup monitoring and alerts
- [ ] Test with small transfers first
- [ ] Setup payment reconciliation
- [ ] Enable audit logging
- [ ] Setup backup payment provider
- [ ] Test failure scenarios
- [ ] Verify callback endpoints are accessible

---

## Common Issues

### SSL Certificate Errors
```python
# Temporary fix (not for production)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
response = requests.post(url, verify=False)
```

### Timeout Issues
```python
response = requests.post(
    url,
    json=payload,
    headers=headers,
    timeout=30  # Set timeout
)
```

### Phone Number Formatting
Different providers require different formats:
```python
# M-Pesa: 254708374149 (with country code)
# MTN: +256700000000 or 256700000000
# Airtel: 255657123456

def normalize_phone(phone, country_code):
    """Normalize phone for specific provider"""
    # Remove common prefixes
    phone = phone.lstrip('+').lstrip('0')
    
    # Add country code if missing
    if not phone.startswith(country_code):
        phone = country_code + phone
    
    return phone
```

---

## Documentation Links

- M-Pesa: https://developer.safaricom.co.ke/
- MTN: https://mtn-api-documentation.stoplight.io/
- Airtel: Check with local Airtel business team
- Tigo: Check with Tigo Tanzania business team

---

**Remember**: This is for educational demo. Always verify provider requirements for production use.
