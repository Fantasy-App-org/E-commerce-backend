"""
PayU Payment Gateway Integration
"""

import hashlib
import hmac
from django.conf import settings
from urllib.parse import urlencode

class PayUGateway:
    def __init__(self):
        # Add these to your Django settings
        self.merchant_key = getattr(settings, 'PAYU_MERCHANT_KEY', 'your_payu_merchant_key')
        self.merchant_salt = getattr(settings, 'PAYU_MERCHANT_SALT', 'your_payu_merchant_salt')
        self.base_url = getattr(settings, 'PAYU_BASE_URL', 'https://test.payu.in')  # Use https://secure.payu.in for production
    
    def generate_hash(self, data):
        """Generate PayU hash for payment verification"""
        hash_string = f"{self.merchant_key}|{data['txnid']}|{data['amount']}|{data['productinfo']}|{data['firstname']}|{data['email']}|||||||||||{self.merchant_salt}"
        return hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
    
    def create_payment_form_data(self, order_data):
        """Create payment form data for PayU"""
        try:
            payment_data = {
                'key': self.merchant_key,
                'txnid': order_data['transaction_id'],
                'amount': str(order_data['amount']),
                'productinfo': order_data.get('description', 'Product'),
                'firstname': order_data['customer']['name'],
                'email': order_data['customer']['email'],
                'phone': order_data['customer']['phone'],
                'surl': order_data.get('success_url', '/payment/success/'),
                'furl': order_data.get('failure_url', '/payment/failure/'),
                'service_provider': 'payu_paisa',
            }
            
            # Generate hash
            payment_data['hash'] = self.generate_hash(payment_data)
            
            return {
                'success': True,
                'form_data': payment_data,
                'action_url': f"{self.base_url}/_payment"
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment_response(self, response_data):
        """Verify PayU payment response"""
        try:
            # Extract response data
            status = response_data.get('status')
            txnid = response_data.get('txnid')
            amount = response_data.get('amount')
            productinfo = response_data.get('productinfo')
            firstname = response_data.get('firstname')
            email = response_data.get('email')
            hash_received = response_data.get('hash')
            
            # Generate hash for verification
            hash_string = f"{self.merchant_salt}|{status}|||||||||||{email}|{firstname}|{productinfo}|{amount}|{txnid}|{self.merchant_key}"
            calculated_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
            
            is_valid = hash_received == calculated_hash
            is_success = status == 'success'
            
            return {
                'success': True,
                'is_valid': is_valid,
                'is_payment_success': is_success,
                'transaction_id': txnid,
                'amount': amount,
                'status': status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_transaction_details(self, transaction_id):
        """Get transaction details from PayU"""
        # PayU doesn't provide a direct API for transaction details
        # You would need to implement webhook handling or use their verify API
        return {
            'success': False,
            'error': 'Transaction details API not implemented for PayU'
        }

# Usage example:
"""
# In your Django settings.py, add:
PAYU_MERCHANT_KEY = 'your_payu_merchant_key'
PAYU_MERCHANT_SALT = 'your_payu_merchant_salt'
PAYU_BASE_URL = 'https://test.payu.in'  # Use https://secure.payu.in for production

# In your views:
from payment_gateways.payu_integration import PayUGateway

gateway = PayUGateway()
form_data = gateway.create_payment_form_data({
    'transaction_id': 'TXN123',
    'amount': 500.00,
    'description': 'Order #123',
    'customer': {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '9876543210'
    },
    'success_url': '/payment/success/',
    'failure_url': '/payment/failure/'
})
"""