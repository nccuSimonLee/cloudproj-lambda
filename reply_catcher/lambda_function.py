from boto3 import client
import json
import os
from datetime import datetime
import pytz



sqs = client('sqs', region_name='us-east-1')
QUEUE_URL = sqs.get_queue_url(QueueName=os.environ['QUEUE_NAME'])['QueueUrl']


def lambda_handler(event, context):
    date, time = convert_event_timezone(
        event['requestContext']['requestTime']
    ).split(' ')
    for line_event in json.loads(event['body'])['events']:
        print(line_event)
        if need_to_process(line_event):
            response = sqs.send_message(
                QueueUrl=QUEUE_URL,
                MessageBody=json.dumps({
                    'userId': line_event['source']['userId'],
                    'date': date,
                    'time': time,
                    'text': line_event['message']['text']
                }),
                MessageGroupId='0'
            )
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
def need_to_process(line_event):
    source = line_event['source']
    return bool(line_event['type'] == 'message'
                and source['type'] == 'group'
                and source['groupId'] == os.environ['TOPIC_GROUP_ID'])

def convert_event_timezone(dt_str):
    orig_dt = datetime.strptime(
        dt_str.split(' ')[0],
        '%d/%b/%Y:%H:%M:%S'
    ).replace(tzinfo=pytz.UTC)
    taipei_dt = orig_dt.astimezone(pytz.timezone('Asia/Taipei'))
    taipei_dt_str = taipei_dt.strftime('%Y-%m-%d %H:%M:%S')
    return taipei_dt_str