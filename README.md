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
Once focus_judger receives the request, it would use aws rekognition to judge the user's status is working or lazy. Then it would publish the status data to the database of the frontend.

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
| linebot-sdk | create by yourself |

# record_handler

# topic_extractor

# reply_catcher