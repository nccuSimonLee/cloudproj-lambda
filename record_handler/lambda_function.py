from boto3 import client
from datetime import datetime
import pytz
import os
import json
from transcribe_handler import TranscribeHandler



transcribe = client('transcribe', region_name='us-east-1')
transcribe_handler = TranscribeHandler(transcribe)
sqs = client('sqs', region_name='us-east-1')
QUEUE_URL = sqs.get_queue_url(QueueName=os.environ['QUEUE_NAME'])['QueueUrl']

def lambda_handler(event, context):
    for record in event['Records']:
        s3_event = record['s3']
        print(s3_event)

        bucket_name = s3_event['bucket']['name']
        key = s3_event['object']['key'].replace('%40', '@')
        texts = transcribe_handler.record_to_texts(bucket_name, key)
        print(f'Texts: {texts}')

        event_datetime = convert_event_timezone(record['eventTime'])
        event_date, event_time = event_datetime.split(' ')
        username, _ = key.split('/')

        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({
                'username': username,
                'date': event_date,
                'time': event_time,
                'texts': texts
            })
        )
        print('Response:', response)

    return

def convert_event_timezone(dt_str):
    orig_dt = datetime.strptime(
        dt_str[:-5],
        '%Y-%m-%dT%H:%M:%S'
    ).replace(tzinfo=pytz.UTC)
    taipei_dt = orig_dt.astimezone(pytz.timezone('Asia/Taipei'))
    taipei_dt_str = taipei_dt.strftime('%Y-%m-%d %H:%M:%S')
    return taipei_dt_str