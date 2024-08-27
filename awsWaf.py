from flask import Flask, request, jsonify
from collections import defaultdict
from datetime import datetime, timedelta
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Regular expression patterns for SQL injection and XSS
patterns = [
    r"('.+--)|(--)|(%27)|(\*|;|--|\+\s)|(\s+OR\s+)|(\s+AND\s+)",
    r"(<|>|\"|\'|%3C|%3E|%22|%27|%3c|%3e|%22|%27|%3C|%3E|%27|%22)"
]

# Rate limiting: Max requests per IP per minute
RATE_LIMIT = 3
rate_limit = defaultdict(lambda: [0, datetime.now()])

def is_malicious(input_string):
    """Check if the input string matches any malicious patterns."""
    for pattern in patterns:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True
    return False

def rate_limit_exceeded(ip):
    """Check if the rate limit for the given IP address is exceeded."""
    requests, timestamp = rate_limit[ip]
    now = datetime.now()
    if (now - timestamp) > timedelta(minutes=1):
        rate_limit[ip] = [1, now]
        return False
    rate_limit[ip][0] += 1
    return rate_limit[ip][0] > RATE_LIMIT

@app.route('/filter', methods=['GET'])
def filter_input():
    """Filter user input for malicious patterns and apply rate limiting."""
    user_input = request.args.get('input', '')
    user_ip = request.remote_addr

    if rate_limit_exceeded(user_ip):
        return jsonify({"error": "Rate limit exceeded"}), 429

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    if is_malicious(user_input):
        return jsonify({"error": "Blocked: Malicious input detected"}), 400

    return jsonify({"message": "Input is safe"}), 200

if __name__ == '__main__':
    # Run the app on port 80
    app.run(host='0.0.0.0', port=80)
