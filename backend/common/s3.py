import boto3

def save_image_to_s3(image, bucket_name, s3_file_name, prompt, subject, scene, spirits, model):
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

    metadata = {
            'prompt': prompt,
            'subject': subject,
            'scene': scene,
            'spirits': ', '.join(spirits),
            'model': model
        }

    s3.put_object(Bucket=bucket_name, Key=s3_file_name, Body=image, Metadata=metadata)
    print(f"Image saved to S3 bucket {bucket_name} with key {s3_file_name}")

def list_items_v2(bucket_name):
    """
    Lists the objects in an S3 bucket.

    Parameters:
    bucket_name (str): The name of the S3 bucket to list objects from.

    Returns:
    list: A list of objects in the bucket.
    """
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name)

    return response['Contents'] if 'Contents' in response else []

def get_object_with_metadata(bucket_name, key):
    """
    Gets an object from an S3 bucket.

    Parameters:
    bucket_name (str): The name of the S3 bucket to get the object from.
    key (str): The key of the object to get.

    Returns:
    dict: The object data.
    """
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=key)

    return response

def get_latest_file(bucketName):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucketName)

    latest_object = None 
    for obj in response['Contents']:
        obj_time = obj['LastModified']
        if latest_object is None or obj_time > latest_object['LastModified']:
            latest_object = obj

    image_path = latest_object['Key']

    obj = s3.get_object(Bucket=bucketName, Key=image_path)
    metadata = obj['Metadata']

    return obj, metadata, image_path