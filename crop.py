from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/detect_faces', methods=['POST'])
def detect_faces():
    try:
        # Read the image file from the request
        file = request.files.get('image')
        if not file:
            return jsonify({'error': 'No image file provided'}), 400
        
        # Convert the file to a numpy array
        npimg = np.frombuffer(file.read(), np.uint8)
        
        # Decode the image using OpenCV
        img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Load the Haar Cascade for face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if face_cascade.empty():
            return jsonify({'error': 'Error loading Haar Cascade XML file'}), 500
        
        # Detect faces in the image
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        # Initialize a list to hold the cropped face images in base64 format
        cropped_faces = []
        for (x, y, w, h) in faces:
            face = img[y:y+h, x:x+w]  # Crop the face from the image
            
            # Encode the face image as JPEG
            _, buffer = cv2.imencode('.jpg', face)
            
            # Convert the JPEG buffer to base64 string
            face_base64 = base64.b64encode(buffer).decode('utf-8')
            cropped_faces.append(face_base64)
        
        # Return the list of detected faces in JSON format
        return jsonify({'faces': cropped_faces})
    
    except Exception as e:
        # Handle exceptions and return an error message
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
