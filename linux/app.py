from flask import Flask, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, async_mode='gevent')

@app.route('/')
def serve_index():
    # Serve the index.html file from the current directory
    return send_from_directory(os.getcwd(), 'index.html')

@socketio.on('input')
def handle_input(data):
    command = data['command']
    
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        output = result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        output = e.output.decode('utf-8')
    
    socketio.emit('output', {'output': output})

if __name__ == '__main__':
    socketio.run(app, debug=True)
