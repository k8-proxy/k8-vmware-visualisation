import json

from getVMs import *

def lambda_handler(event, context):
    GetVmware().machines()
    return {
        'body': json.dumps('JSON File created Successfully and uploaded to S3 bucket')
        }
