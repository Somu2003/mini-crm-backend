class VendorAPI:
    def send_message(self, recipient, message, log_id):
        print(f"📱 Sending: {message[:50]}... to {recipient}")
