import boto3

def save_image_to_s3(image, bucket_name, s3_file_name, prompt):
    """
    Saves an image to an S3 bucket.

    Parameters:
    image (bytes): The image to upload.
    bucket_name (str): The name of the S3 bucket to upload to.
    s3_file_name (str): The file name to use for the uploaded image.
    prompt (str): The prompt to save as metadata with the image.

    Returns:
    None
    """
    s3 = boto3.client('s3')

    metadata = {'prompt': prompt}

    s3.put_object(Bucket=bucket_name, Key=s3_file_name, Body=image, Metadata=metadata)
    print(f"Image saved to S3 bucket {bucket_name} with key {s3_file_name}")