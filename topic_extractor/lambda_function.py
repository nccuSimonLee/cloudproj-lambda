from boto3 import client
from .transcribe_handler import TranscribeHandler
from .extractor import Extractor



transcribe = client('transcribe', region_name='us-east-1')
transcribe_handler = TranscribeHandler(transcribe)
extractor = Extractor()

def lambda_handler(event, context):
    for record in event['Records']:
        s3_event = record['s3']
        print(s3_event)

        bucket_name = s3_event['bucket']['name']
        key = s3_event['object']['key'].replace('%40', '@')

        texts = transcribe_handler.record_to_texts(bucket_name, key)
        topic = extractor.extract_topic(texts)
        print(f'Topic: {topic}')
    return
