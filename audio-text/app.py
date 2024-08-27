from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
import smtplib
import subprocess
import cv2
from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import boto3
import time
import google.generativeai as genai
import numpy as np
import geocoder
from googlesearch import search 
from instagrapi import Client
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import mediapipe as mp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes



@app.route('/list-audio-files', methods=['POST'])
def list_audio_files():
    data = request.json
    aws_access_key = data.get('aws_access_key')
    aws_secret_key = data.get('aws_secret_key')
    region_name = data.get('region_name')
    bucket_name = data.get('bucket_name')

    try:
        # Connect to S3
        s3_client = boto3.client('s3', region_name=region_name,
                                 aws_access_key_id=,
                                 aws_secret_access_key=)
        
        # List objects in the specified bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name)

        audio_files = [obj['Key'] for obj in response.get('Contents', [])
                       if obj['Key'].endswith(('mp3', 'wav', 'flac'))]  # Filter for audio files
        
        return jsonify({'success': True, 'files': audio_files})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    data = request.json
    aws_access_key = data.get('aws_access_key')
    aws_secret_key = data.get('aws_secret_key')
    region_name = data.get('region_name')
    bucket_name = data.get('bucket_name')
    file_key = data.get('file_key')

    try:
        # Connect to Transcribe and S3
        transcribe_client = boto3.client('transcribe', region_name=region_name,
                                         aws_access_key_id=aws_access_key,
                                         aws_secret_access_key=aws_secret_key)

        # Generate a unique job name
        job_name = f"transcription_job_{int(time.time())}"

        # S3 URI for the audio file
        s3_uri = f's3://{bucket_name}/{file_key}'

        # Start the transcription job
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat=file_key.split('.')[-1],  # Extract file format (e.g., mp3, wav)
            LanguageCode='en-US'
        )

        # Poll for job completion
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            time.sleep(5)

        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            transcript_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            transcript_response = boto3.client('s3').get_object(Bucket=bucket_name, Key=transcript_url)
            transcript_text = transcript_response['Body'].read().decode('utf-8')

            return jsonify({'success': True, 'transcript': transcript_text})
        else:
            return jsonify({'success': False, 'message': 'Transcription failed.'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
