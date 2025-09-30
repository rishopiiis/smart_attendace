# import qrcode
# import os
# from datetime import datetime
# import uuid

# class QRGenerator:
#     def __init__(self, qr_code_dir='static/qr_codes'):
#         self.qr_code_dir = qr_code_dir
#         if not os.path.exists(qr_code_dir):
#             os.makedirs(qr_code_dir)
    
#     def generate_qr_code(self, data, filename):
#         """Generate QR code with participant data"""
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4,
#         )
#         qr.add_data(data)
#         qr.make(fit=True)
        
#         img = qr.make_image(fill_color="black", back_color="white")
#         filepath = os.path.join(self.qr_code_dir, filename)
#         img.save(filepath)
#         return filepath
    
#     def generate_entrance_id(self):
#         """Generate unique entrance ID"""
#         return str(uuid.uuid4())[:8].upper()

# class SMSHandler:
#     @staticmethod
#     def generate_feedback_link(entrance_id, base_url):
#         """Generate feedback link for SMS"""
#         return f"{base_url}/feedback/{entrance_id}"
    
#     @staticmethod
#     def send_sms(phone, message):
#         """Simulate SMS sending - integrate with actual SMS service"""
#         print(f"SMS to {phone}: {message}")
#         # Integrate with services like Twilio, AWS SNS, etc.
#         return True


import qrcode
import os
from datetime import datetime
import uuid

class QRGenerator:
    def __init__(self, qr_code_dir='static/qr_codes'):
        self.qr_code_dir = qr_code_dir
        if not os.path.exists(qr_code_dir):
            os.makedirs(qr_code_dir)
    
    def generate_qr_code(self, data, filename):
        """Generate QR code with participant data"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        filepath = os.path.join(self.qr_code_dir, filename)
        img.save(filepath)
        return filepath
    
    def generate_entrance_id(self):
        """Generate unique entrance ID"""
        return str(uuid.uuid4())[:8].upper()

class SMSHandler:
    @staticmethod
    def generate_feedback_link(entrance_id, base_url):
        """Generate feedback link for SMS"""
        return f"{base_url}/feedback/{entrance_id}"
    
    @staticmethod
    def send_sms(phone, message):
        """Simulate SMS sending - integrate with actual SMS service"""
        print(f"📱 SMS to {phone}: {message}")
        # Integrate with services like Twilio, AWS SNS, etc.
        # Example with Twilio:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=message,
        #     from_='+1234567890',
        #     to=phone
        # )
        return True