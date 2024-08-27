from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import subprocess

app = Flask(__name__)
CORS(app)

def get_translation_code(text, target_lang, aws_access_key, aws_secret_key, aws_region):
    # Configure the Gemini model
    genai.configure(api_key="YOUR_API_KEY_HERE")  # Replace with your Gemini API key

    # Choose the Gemini model you want to use
    model = genai.GenerativeModel("gemini-pro")  # Replace with desired model

    # Your prompt
    prompt = f"""
    Write a complete Python code to use AWS Translate service where:
    - Text to be translated is: {text}
    - Target language is: {target_lang}
    - AWS credentials are:
      Access Key: {aws_access_key}
      Secret Access Key: {aws_secret_key}
      Region: {aws_region}
    - Source language code is 'en' (English)
    - Do not print anything other than the code
    """

    # Generate code
    response = model.generate_content(prompt)
    code = response.text.strip("```python\n").strip("```")

    return code

@app.route('/generate_translation_script', methods=['POST'])
def generate_translation_script():
    data = request.json
    text = data.get('text')
    target_lang = data.get('target_lang')

    aws_access_key = data.get('aws_access_key')
    aws_secret_key = data.get('aws_secret_key')
    aws_region = data.get('aws_region')

    if not text or not target_lang or not aws_access_key or not aws_secret_key or not aws_region:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Generate Python code using Gemini
        code = get_translation_code(text, target_lang, aws_access_key, aws_secret_key, aws_region)

        # Save the generated script
        with open('generated_script.py', 'w') as file:
            file.write(code)

        # Execute the generated script
        subprocess.run(['python', 'generated_script.py'], check=True)

        return jsonify({'message': 'Script executed successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6000)
