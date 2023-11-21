import boto3
import os
import base64
import json
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

s3 = boto3.client('s3')

def get_latest_bear():
    print("Begin get_latest_bear function")
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
    print("Object retrieved from S3")

    metadata = obj['Metadata']

    print(metadata)

    # Generate a presigned URL for the object
    try:
        response = s3.generate_presigned_url('get_object',
                                              Params={'Bucket': bucketName,
                                                      'Key': latest_object['Key']},
                                              ExpiresIn=3600)
    except NoCredentialsError:
        print("Credentials not available")
        return None

    print("Presigned URL: %s" % response)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'url': response,
            'metadata': metadata
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
        },
    }

# AWS Lambda handler
def lambda_handler(event, context):
    try:
        return get_latest_bear()
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == "__main__":
    load_dotenv()
    get_latest_bear()
