import boto3
import requests
from botocore.exceptions import NoCredentialsError

def save_image_to_s3(image_url, bucket_name, s3_file_name):
    s3 = boto3.client('s3')

    try:
        # Fetch image
        image = requests.get(image_url).content

        # Upload image to S3
        s3.put_object(Bucket=bucket_name, Key=s3_file_name, Body=image)
        print(f"Image saved to S3 bucket {bucket_name} with key {s3_file_name}")
    except NoCredentialsError:
        print("No AWS credentials found")
    except Exception as e:
        print(f"An error occurred: {e}")