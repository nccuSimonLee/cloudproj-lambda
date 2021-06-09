from boto3 import client
from datetime import datetime
import pytz
import os



rekog = client('rekognition', region_name='us-east-1')
ddb = client('dynamodb', region_name='us-east-1')

def lambda_handler(event, context):
    """
    Args:
        event: an S3 put object event
    """
    for record in event['Records']:
        print(record['s3'])
        # determine if there are any faces in the photo
        has_face = check_s3_event_has_face(record['s3'])
        
        # create the attributes of the table item
        username = record['s3']['object']['key'].split('/')[0].replace('%40', '@')
        event_datetime = convert_event_timezone(record['eventTime'])
        event_date, event_time = event_datetime.split(' ')
        print(f'{username} - {event_date} {event_time} - focus: {has_face}')

        response = write_to_ddb(username, event_date, event_time, has_face)
    return

def check_s3_event_has_face(s3_event):
    bucket_name = s3_event['bucket']['name']
    key = s3_event['object']['key'].replace('%40', '@')
    response = rekog.detect_faces(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': key,
            }
        }
    )
    # there is at least one face in the photo
    # if and only if response['FaceDetails] is not empty
    return bool(response['FaceDetails'])

def convert_event_timezone(dt_str):
    orig_dt = datetime.strptime(
        dt_str[:-5],
        '%Y-%m-%dT%H:%M:%S'
    ).replace(tzinfo=pytz.UTC)
    taipei_dt = orig_dt.astimezone(pytz.timezone('Asia/Taipei'))
    taipei_dt_str = taipei_dt.strftime('%Y-%m-%d %H:%M:%S')
    return taipei_dt_str

def write_to_ddb(username, event_date, event_time, has_face):
    response = ddb.put_item(
        TableName=os.environ['TABLE_NAME'],
        Item={
            'username': {'S': username},
            'date': {'S': event_date},
            'time': {'S': event_time},
            'focus': {'N': str(int(has_face))}
        }
    )
    return response
