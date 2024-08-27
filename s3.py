from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/create_and_upload', methods=['POST'])
def create_and_upload():
    try:
        # Extract data from the request JSON
        data = request.json
        aws_access_key = data['aws_access_key']
        aws_secret_key = data['aws_secret_key']
        bucket_name = data['bucket_name']
        file_name = data['file_name']
        file_content = data['file_content']
        region = data.get('region', 'us-east-1')

        # Initialize the S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )

        # Check if the bucket already exists
        try:
            s3.head_bucket(Bucket=bucket_name)
            bucket_exists = True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                bucket_exists = False
            else:
                raise e

        # Create the bucket if it doesn't exist
        if not bucket_exists:
            if region == 'us-east-1':
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )

        # Upload the file to the bucket
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)

        return jsonify({'message': 'Bucket created (if not existed) and file uploaded successfully'}), 200

    except NoCredentialsError:
        return jsonify({'error': 'Invalid AWS credentials'}), 400
    except PartialCredentialsError:
        return jsonify({'error': 'Incomplete AWS credentials'}), 400
    except ClientError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
