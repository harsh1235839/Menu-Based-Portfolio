import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Path where logs will be saved
LOG_FILE_PATH = 'cloudwatch_logs.txt'

@app.route('/get-credentials', methods=['POST'])
def get_credentials():
    """
    Endpoint to receive AWS credentials and log group/stream info from the user.
    """
    data = request.json
    aws_access_key_id = data.get('aws_access_key_id')
    aws_secret_access_key = data.get('aws_secret_access_key')
    log_group_name = data.get('log_group_name')
    log_stream_name = data.get('log_stream_name')

    if not all([aws_access_key_id, aws_secret_access_key, log_group_name, log_stream_name]):
        return jsonify({"error": "Missing required parameters"}), 400

    # Fetch logs using the provided credentials and log group/stream info
    logs = fetch_logs(aws_access_key_id, aws_secret_access_key, log_group_name, log_stream_name)

    if logs is None:
        return jsonify({"error": "Failed to fetch logs"}), 500

    # Save logs to a file
    with open(LOG_FILE_PATH, 'w') as file:
        file.write(logs)
    
    return jsonify({"message": "Logs fetched successfully"}), 200

@app.route('/logs', methods=['GET'])
def serve_logs():
    """
    Endpoint to serve the logs file.
    """
    if not os.path.exists(LOG_FILE_PATH):
        return jsonify({"error": "Logs file not found"}), 404

    return send_from_directory('.', LOG_FILE_PATH, as_attachment=True)

def fetch_logs(aws_access_key_id, aws_secret_access_key, log_group_name, log_stream_name):
    """
    Fetch logs from AWS CloudWatch using the provided credentials.
    """
    try:
        client = boto3.client(
            'logs',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name='us-east-1'  # Update to your region
        )

        response = client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            startFromHead=True
        )

        logs = response['events']
        log_messages = [log['message'] for log in logs]
        return '\n'.join(log_messages)

    except (NoCredentialsError, PartialCredentialsError) as e:
        print("Credentials error:", e)
        return None
    except Exception as e:
        print("Error fetching logs:", e)
        return None

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)  # Listen on port 80
