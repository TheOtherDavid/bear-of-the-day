import boto3
import os
import base64
import json
import logging
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

s3 = boto3.client('s3')

def get_bears_batch(batch_size, offset):
    print("Begin get_bears_batch function")
    bucketName = os.environ['AWS_BUCKET_NAME']
    # Get list of objects in bucket
    response = s3.list_objects_v2(Bucket=bucketName)
    # Sort objects by LastModified and get the latest 'batch_size' objects
    sorted_objects = sorted(response['Contents'], key=lambda obj: obj['LastModified'], reverse=True)
    batch_objects = sorted_objects[offset:offset + batch_size]
    # Generate presigned URLs for the objects
    urls = []
    for obj in batch_objects:
        try:
            response = s3.generate_presigned_url('get_object',
                                                  Params={'Bucket': bucketName,
                                                          'Key': obj['Key']},
                                                  ExpiresIn=3600)
            urls.append(response)
        except NoCredentialsError:
            print("Credentials not available")
            return None
    print("Presigned URLs: %s" % urls)
    return {
        'statusCode': 200,
        'body': json.dumps({
            'urls': urls
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
    }

# AWS Lambda handler
def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        if 'batch_size' in body:
            batch_size = body['batch_size']
        else:
            logging.warning("batch_size not provided in event, defaulting to 1")
            batch_size = 1

        if 'offset' in body:
            offset = body['offset']
        else:
            logging.warning("offset not provided in event, defaulting to 0")
            offset = 0

        return get_bears_batch(batch_size, offset)
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == "__main__":
    load_dotenv()
    get_bears_batch(5, 0)