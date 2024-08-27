from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3

app = Flask(__name__)
CORS(app)

def instance_launch(aws_access_key_id, aws_secret_access_key, region_name, instance_type, image_id):
    try:
        myec2 = boto3.resource(
            service_name="ec2",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )

        ec2 = myec2.create_instances(
            InstanceType=instance_type,
            ImageId=image_id,
            MaxCount=1,
            MinCount=1
        )
        instance_id = ec2[0].id
        return True, f"Instance launched successfully! Instance ID: {instance_id}"
    except Exception as e:
        return False, str(e)

@app.route('/instance_launch', methods=['POST'])
def instance_launch_endpoint():
    data = request.json
    aws_access_key_id = data.get('aws_access_key_id')
    aws_secret_access_key = data.get('aws_secret_access_key')
    region_name = data.get('region_name')
    instance_type = data.get('instance_type', 't2.micro')
    image_id = data.get('image_id')

    if not aws_access_key_id or not aws_secret_access_key or not region_name or not image_id:
        return jsonify({'error': 'Missing required fields'}), 400

    success, message = instance_launch(aws_access_key_id, aws_secret_access_key, region_name, instance_type, image_id)

    if success:
        return jsonify({'message': message}), 200
    else:
        return jsonify({'error': message}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
