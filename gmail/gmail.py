from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from dotenv import password
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

def send_email(to, message):
    email_id = "priyamsanodiya340@gmail.com"  # Your email address
    password = # Your email password
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_id, password)
        server.sendmail(email_id, to, message)
        server.quit()
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)

@app.route('/send_email', methods=['POST'])
def send_email_endpoint():
    data = request.json
    to = data.get('to')
    message = data.get('message')

    if not to or not message:
        return jsonify({'error': 'Missing required fields'}), 400

    success, response_message = send_email(to, message)

    if success:
        return jsonify({'message': response_message}), 200
    else:
        return jsonify({'error': response_message}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
