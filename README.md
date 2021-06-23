# Introduction
![](architecture.png)
The repo consists of four aws lambdas, and the architecture graph above shows how they interact with each other.

The lambdas compose the heart of the system. They mainly contribute to two features:
  - judge the users' status by their photos and screenshots
  - extract discussion topics and incorporate them with replies

The deployments are a bit tricky, please refer to the following sections to find how to deploy each lambda and what they exactly did.

Note: Most of the lambda layers are from [Klayers](https://github.com/keithrozario/Klayers/blob/a415f8fce3ea0fbfe1d012ec72498da0eada8f3c/deployments/python3.8/arns/us-east-1.csv).

# focus_judger
focus_judger is triggered by an API gateway, and the POST request sent to the API gateway needs to contain a json body with the following parameters
```json
{
    'username': string,
    'photo': {
        'bucket': string,
        'key': string
    },
    'screenshot': {
        'bucket': string,
        'key': string
    }
}
```
Once focus_judger receives the request, it would use [aws rekognition](https://aws.amazon.com/tw/transcribe/) to judge the user's status is working or lazy. Then it would publish the status data to the database of the frontend.

If the condition is staisfied, focus_judger would publish a canned message the line group and publish a message to the MQTT to trigger the IoT device.

## Setup
### Runtime
 - Python 3.8

### Permissions
 - cloudwatch
 - rekognition
 - dynamoDB

### Trigger
 - API Gateway

### Layers
| name | Version ARN |
|-------|-------------|
| Klayers-python38-requests|arn:aws:lambda:us-east-1:770693421928:layer:Klayers-python38-requests:17
|Klayers-python38-numpy | arn:aws:lambda:us-east-1:770693421928:layer:Klayers-python38-numpy:17
|Klayers-python38-pytz | arn:aws:lambda:us-east-1:770693421928:layer:Klayers-python38-pytz:5 |
| [linebot-sdk](https://github.com/line/line-bot-sdk-python) | create by yourself |

# record_handler
record_handler is triggered by an S3 object create event, and the object must be a wav file.

Once record_handler receives the event, it would use [aws transcribe](https://aws.amazon.com/tw/transcribe/) to transcribe the wav file into texts, and generate some relevant data:
 - username
 - date: the date of the event creation in the Asia/Taipei time zone (e.g., 2021-06-23)
 - time: the time (24-hour clock) of the event creation in the Asia/Taipei time zone (e.g., 08:30:00)
 - texts: transcription of the wav file

 The relevant data would be published to the SQS queue to trigger topic_extractor.

## Setup
### Runtime
 - Python 3.8

### Permissions
 - cloudwatch
 - transcribe
 - sqs

### Trigger
 - S3 object create event

### Layers
| name | Version ARN |
|-------|-------------|
|Klayers-python38-pytz | arn:aws:lambda:us-east-1:770693421928:layer:Klayers-python38-pytz:5 |
| [python-opencc](https://github.com/yichen0831/opencc-python) | create by yourself |

# topic_extractor

# reply_catcher