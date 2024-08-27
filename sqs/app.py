import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from flask_cors import CORS
from flask import Flask

app = Flask(__name__)

cors = CORS(app)

@app.route("/sqs")
def message_queue():
    # Initialize a session using Amazon SQS
    try:
        sqs = boto3.client(
            service_name='sqs',
             region_name='ap-south-1'  # Specify your region
        )
    except (NoCredentialsError, PartialCredentialsError):
        print("Credentials not available")
        return "Credentials not available", 500

    # Create a new SQS queue
    try:
        response = sqs.create_queue(
            QueueName='TestQueue',
            Attributes={
                'DelaySeconds': '5',
                'MessageRetentionPeriod': '86400'
            }
        )
        print(f"Queue created. URL: {response['QueueUrl']}")
        queue_url = response['QueueUrl']
    except sqs.exceptions.QueueNameExists:
        print("Queue already exists")
        queue_url = sqs.get_queue_url(QueueName='TestQueue')['QueueUrl']

    # Send a message to the queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody='Hello World!',
        DelaySeconds=10
    )
    print(f"Message sent. Message ID: {response['MessageId']}")

    # Receive a message from the queue
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    if 'Messages' in response:
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']

        # Print out the message body
        print(f"Received message: {message['Body']}")

        # Delete the message from the queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print("Message deleted")
    else:
        print("No messages available")

    return "Message processed", 200

app.run(host="0.0.0.0", port=80)
