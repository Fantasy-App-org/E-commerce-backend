"""
Razorpay Payment Gateway Integration
Install: pip install razorpay
"""

import razorpay
from django.conf import settings
from decimal import Decimal

class RazorpayGateway:
    def __init__(self):
        # Add these to your Django settings
        self.key_id = getattr(settings, 'RAZORPAY_KEY_ID', 'your_razorpay_key_id')
        self.key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', 'your_razorpay_key_secret')
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
    
    def create_order(self, amount, currency='INR', receipt=None):
        """Create a Razorpay order"""
        try:
            # Amount should be in paise (multiply by 100)
            amount_in_paise = int(float(amount) * 100)
            
            order_data = {
                'amount': amount_in_paise,
                'currency': currency,
                'receipt': receipt or f'order_{amount_in_paise}',
                'payment_capture': 1  # Auto capture payment
            }
            
            order = self.client.order.create(data=order_data)
            return {
                'success': True,
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'status': order['status']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_id, order_id, signature):
        """Verify Razorpay payment signature"""
        try:
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            # Verify signature
            self.client.utility.verify_payment_signature(params_dict)
            return {'success': True, 'verified': True}
        except Exception as e:
            return {'success': False, 'error': str(e), 'verified': False}
    
    def get_payment_details(self, payment_id):
        """Get payment details from Razorpay"""
        try:
            payment = self.client.payment.fetch(payment_id)
            return {
                'success': True,
                'payment': payment
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund_payment(self, payment_id, amount=None):
        """Refund a payment"""
        try:
            refund_data = {}
            if amount:
                refund_data['amount'] = int(float(amount) * 100)  # Convert to paise
            
            refund = self.client.payment.refund(payment_id, refund_data)
            return {
                'success': True,
                'refund_id': refund['id'],
                'status': refund['status']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Usage example:
"""
# In your Django settings.py, add:
RAZORPAY_KEY_ID = 'your_razorpay_key_id'
RAZORPAY_KEY_SECRET = 'your_razorpay_key_secret'

# In your views:
from payment_gateways.razorpay_integration import RazorpayGateway

gateway = RazorpayGateway()
order_result = gateway.create_order(amount=500.00, receipt='order_123')

if order_result['success']:
    # Send order_id to frontend for payment
    razorpay_order_id = order_result['order_id']
"""