import json

from get_recent_releases import *

def lambda_handler(event, context):
    obj = Get_GW_Releases()
    obj.create_json()
    return {
        'body': json.dumps('JSON File created Successfully and uploaded to S3 bucket')
        }
