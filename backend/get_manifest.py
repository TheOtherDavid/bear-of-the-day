"""GET /manifest - returns the image metadata manifest JSON for the frontend."""
import os
import boto3
import common.manifest as manifest
from dotenv import load_dotenv

s3 = boto3.client("s3")

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
}


def get_manifest():
    bucket = os.environ["AWS_BUCKET_NAME"]
    obj = s3.get_object(Bucket=bucket, Key=manifest.MANIFEST_KEY)
    body = obj["Body"].read().decode("utf-8")
    return {"statusCode": 200, "body": body, "headers": CORS_HEADERS}


def lambda_handler(event, context):
    try:
        return get_manifest()
    except Exception as e:
        print(f"Error: {e}")
        raise e


if __name__ == "__main__":
    load_dotenv()
    print(get_manifest())
