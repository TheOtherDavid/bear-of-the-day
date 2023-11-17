import boto3
import os
from dotenv import load_dotenv
from datetime import datetime

s3 = boto3.client('s3')

def get_latest_bear():
    bucketName = os.environ['AWS_BUCKET_NAME']
    # Get list of objects in bucket
    response = s3.list_objects_v2(Bucket=bucketName)

    # Find latest object based on LastModified
    latest_object = None 
    for obj in response['Contents']:
        obj_time = obj['LastModified']
        if latest_object is None or obj_time > latest_object['LastModified']:
            latest_object = obj

    obj = s3.get_object(Bucket=bucketName, Key=latest_object['Key'])

    metadata = obj['Metadata']

    return {
        'statusCode': 200,
        'body': obj['Body'].read(),
        'headers': {
            'Content-Type': 'image/*' 
        },
        'metadata': metadata
    }

# AWS Lambda handler
def lambda_handler(event, context):
    try:
        get_latest_bear()
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == "__main__":
    load_dotenv()
    get_latest_bear()
