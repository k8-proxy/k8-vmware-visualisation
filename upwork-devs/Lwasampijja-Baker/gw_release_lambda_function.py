import json

from get_recent_releases import *

def lambda_handler(event, context):
    GetRelease().releases()
    return {
        'body': json.dumps('JSON File created Successfully and uploaded to S3 bucket')
        }
