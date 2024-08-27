from flask import Flask, request, jsonify
from twilio.rest import Client
import datetime
import threading
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Twilio credentials


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(phone_number, message):
    """Send a WhatsApp message using Twilio."""
    try:
        client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f'whatsapp:{phone_number}'
        )
    except Exception as e:
        raise e

@app.route('/whatsapp_message', methods=['POST'])
def handle_whatsapp_message():
    """Handle sending or scheduling a WhatsApp message."""
    data = request.json
    phone_number = data.get('phone_number')
    message = data.get('message')
    send_option = data.get('send_option').strip().lower()
    
    if not phone_number or not message or not send_option:
        return jsonify({'error': 'Missing required fields'}), 400

    if send_option == 'instant':
        try:
            send_whatsapp_message(phone_number, message)
            return jsonify({'message': f'Message sent instantly to {phone_number}'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif send_option == 'schedule':
        hour = data.get('hour')
        minute = data.get('minute')

        if hour is None or minute is None:
            return jsonify({'error': 'Hour and minute are required for scheduling'}), 400

        try:
            # Calculate time for sending message
            now = datetime.datetime.now()
            send_time = now.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
            if send_time < now:
                send_time += datetime.timedelta(days=1)
            
            # Schedule message
            delay = (send_time - now).total_seconds()
            threading.Timer(delay, send_whatsapp_message, args=[phone_number, message]).start()

            return jsonify({'message': f'Message scheduled to {phone_number} at {hour}:{minute}'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid option. Please enter "instant" or "schedule".'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
