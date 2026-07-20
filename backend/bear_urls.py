"""POST /bearurls - mint presigned URLs for a page of image keys.

Body: {"keys": ["20260720-130144.jpg", ...]}
Returns: {"urls": {"<key>": "<presigned-url>", ...}}

Presigned URLs expire, so they can't live in the static manifest; the frontend
requests them lazily for just the images currently visible.
"""
import os
import json
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

s3 = boto3.client("s3")

MAX_KEYS = 200

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
}


def presign_keys(keys):
    bucket = os.environ["AWS_BUCKET_NAME"]
    urls = {}
    for key in keys[:MAX_KEYS]:
        try:
            urls[key] = s3.generate_presigned_url(
                "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=3600
            )
        except NoCredentialsError:
            print("Credentials not available")
            return None
    return urls


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        keys = body.get("keys", [])
        if not isinstance(keys, list):
            return {"statusCode": 400, "headers": CORS_HEADERS,
                    "body": json.dumps({"error": "'keys' must be a list"})}
        urls = presign_keys(keys)
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": json.dumps({"urls": urls})}
    except Exception as e:
        print(f"Error: {e}")
        raise e


if __name__ == "__main__":
    load_dotenv()
    print(presign_keys(["example.jpg"]))
