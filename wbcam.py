from flask import Flask, request, jsonify
from PIL import Image
import io
import base64
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        # Get JSON data from request
        data = request.get_json()
        image_data = data.get('image')

        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        # Remove the data URL part and keep only the base64-encoded string
        image_data = re.sub('^data:image/.+;base64,', '', image_data)

        # Decode the base64 string
        image = Image.open(io.BytesIO(base64.b64decode(image_data)))

        # Save the image
        image_path = 'uploaded_image.jpg'
        image.save(image_path)

        return jsonify({'message': 'Image uploaded successfully', 'image_path': image_path}), 200
    
    except Exception as e:
        return jsonify({'error': f'Error uploading image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
