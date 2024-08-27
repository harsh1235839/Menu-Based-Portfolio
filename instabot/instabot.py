from flask import Flask, request, jsonify
from flask_cors import CORS
from instagrapi import Client

app = Flask(__name__)
CORS(app)

def post_on_instagram(username, password, photo_path, caption):
    try:
        client = Client()
        client.login(username, password)
        media = client.photo_upload(photo_path, caption=caption)
        media_id = media.pk
        return True, f"Photo uploaded successfully! Media ID: {media_id}"
    except Exception as e:
        return False, str(e)

@app.route('/post_on_instagram', methods=['POST'])
def post_on_instagram_endpoint():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    photo = request.files.get('photo')
    caption = data.get('caption')

    if not username or not password or not photo or not caption:
        return jsonify({'error': 'Missing required fields'}), 400

    photo_path = f"temp_{photo.filename}"
    photo.save(photo_path)

    success, response_message = post_on_instagram(username, password, photo_path, caption)
    
    # Cleanup the temporary photo file
    import os
    os.remove(photo_path)

    if success:
        return jsonify({'message': response_message}), 200
    else:
        return jsonify({'error': response_message}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=81)
