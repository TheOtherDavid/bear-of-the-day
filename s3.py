import boto3
import requests
from botocore.exceptions import NoCredentialsError

def save_image_to_s3(image_url, bucket_name, s3_file_name, prompt):
    """
    Saves an image to an S3 bucket.

    Parameters:
    image_url (str): The URL of the image to download.
    bucket_name (str): The name of the S3 bucket to upload to.
    s3_file_name (str): The file name to use for the uploaded image.
    prompt (str): The prompt to save as metadata with the image.

    Returns:
    None
    """
    s3 = boto3.client('s3')

    try:
        image = requests.get(image_url).content
        metadata = {'prompt': prompt}

        s3.put_object(Bucket=bucket_name, Key=s3_file_name, Body=image, Metadata=metadata)
        print(f"Image saved to S3 bucket {bucket_name} with key {s3_file_name}")
    except NoCredentialsError:
        print("No AWS credentials found")
    except Exception as e:
        print(f"An error occurred: {e}")