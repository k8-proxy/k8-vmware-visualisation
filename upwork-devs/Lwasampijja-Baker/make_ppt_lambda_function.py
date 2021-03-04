import json
import boto3

from make_ppt import *

def lambda_handler(event, context):

    uploads = make_presentation(output_to='/tmp/gw_releases.pptx', single=True, dm = True)

    s3      = boto3.client('s3')

    s3.upload_file("/tmp/gw_releases.pptx", "gw-data-vis", "gw_releases.pptx")

    return {
        'body': json.dumps('Presentation created Successfully and uploaded to S3 bucket')
           }
