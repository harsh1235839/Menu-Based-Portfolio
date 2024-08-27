from flask import Flask, request, jsonify
import cv2
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

def capture_image(filename):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False, "Could not open webcam"
    
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(filename, frame)
        cap.release()
        cv2.destroyAllWindows()
        return True, f"Image saved as {filename}"
    else:
        cap.release()
        cv2.destroyAllWindows()
        return False, "Failed to capture image"

def send_email_with_attachment(sender_email, receiver_email, password, subject, body, attachment_path):
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    with open(attachment_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
        message.attach(part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True, "Email sent successfully."
    except Exception as e:
        return False, f"Error sending email: {e}"

@app.route('/capture_image', methods=['POST'])
def capture_image_endpoint():
    data = request.json
    image_filename = data.get('filename', 'captured_image.jpg')

    success, message = capture_image(image_filename)

    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'error': message}), 500

@app.route('/send_email', methods=['POST'])
def send_email_endpoint():
    data = request.json
    sender_email = "priyamsanodiya340@gmail.com"
    receiver_email = data.get('receiver_email')
    password = "dhgy zwex fjan nrgu"
    subject = data.get('subject')
    body = data.get('body')
    attachment_path = data.get('attachment_path', 'captured_image.jpg')

    if not receiver_email or not subject or not body:
        return jsonify({'error': 'Missing required fields'}), 400

    success, message = send_email_with_attachment(sender_email, receiver_email, password, subject, body, attachment_path)

    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'error': message}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
