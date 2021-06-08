from boto3 import client
import uuid
import os
import json
from linebot import LineBotApi
from linebot.models import TextSendMessage
from extractor import Extractor



extractor = Extractor()
ddb = client('dynamodb', region_name='us-east-1')
line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])


def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])

        topic = extractor.extract_topic(body['texts'])
        print(f'Topic: {topic}')

        username = body['username']

        response = write_to_ddb(username, topic, body)
        print(response)

        publish_to_line_group(username, topic)

    return

def write_to_ddb(username, topic, body):
    topic_id = uuid.uuid4().hex
    response = ddb.put_item(
        TableName=os.environ['TABLE_NAME'],
        Item={
            'topic_id': {'S': topic_id},
            'username': {'S': username},
            'date': {'S': body['date']},
            'time': {'S': body['time']},
            'topic': {'S': topic}
        }
    )
    return response

def publish_to_line_group(username, topic):
    line_bot_api.push_message(
        os.environ['GROUP_ID'],
        TextSendMessage(text=f'@{username} 剛剛發佈了新問題，快來看看吧！\n{topic}')
    )
    return
