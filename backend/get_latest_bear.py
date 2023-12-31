import boto3
import os
import json
import common.s3 as s3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

boto_s3 = boto3.client('s3')

def get_latest_bear():
    print("Begin get_latest_bear function")
    bucketName = os.environ['AWS_BUCKET_NAME']
    
    obj, metadata, image_path = s3.get_latest_file(bucketName)
    print("Object retrieved from S3")

    # Generate a presigned URL for the object
    try:
        response = boto_s3.generate_presigned_url('get_object',
                                              Params={'Bucket': bucketName,
                                                      'Key': image_path},
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
