from boto3 import client
from datetime import datetime
import pytz
import os
import uuid
from transcribe_handler import TranscribeHandler
from extractor import Extractor



transcribe = client('transcribe', region_name='us-east-1')
transcribe_handler = TranscribeHandler(transcribe)
extractor = Extractor()
ddb = client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    for record in event['Records']:
        s3_event = record['s3']
        print(s3_event)

        bucket_name = s3_event['bucket']['name']
        key = s3_event['object']['key'].replace('%40', '@')
        texts = transcribe_handler.record_to_texts(bucket_name, key)
        topic = extractor.extract_topic(texts)
        print(f'Topic: {topic}')

        topic_id = uuid.uuid4().hex
        event_datetime = convert_event_timezone(record['eventTime'])
        event_date, event_time = event_datetime.split(' ')
        response = ddb.put_item(
            TableName=os.environ['TABLE_NAME'],
            Item={
                'topic_id': {'S': topic_id},
                'date': {'S': event_date},
                'time': {'S': event_time},
                'topic': {'S': topic}
            }
        )

    return

def convert_event_timezone(dt_str):
    orig_dt = datetime.strptime(
        dt_str[:-5],
        '%Y-%m-%dT%H:%M:%S'
    ).replace(tzinfo=pytz.UTC)
    taipei_dt = orig_dt.astimezone(pytz.timezone('Asia/Taipei'))
    taipei_dt_str = taipei_dt.strftime('%Y-%m-%d %H:%M:%S')
    return taipei_dt_str
