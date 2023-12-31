import boto3
from dotenv import load_dotenv
from PIL import Image
import io
import os
import common.s3 as s3
import common.send_email as send_email

s3 = boto3.client('s3')

def send_bear_image():
    debug_mode = os.environ.get('DEBUG_MODE', 'False') == 'True'    

    bucketName = os.environ['AWS_BUCKET_NAME']

    if debug_mode:
        print("DEBUG MODE")
        obj = generate_blank_image()
        prompt = "DEBUG MODE"
        metadata = {"prompt": prompt}
        image_path = "debug.jpg"
        recipients = [os.environ['DEBUG_RECIPIENTS']]
    else:
        # Get list of objects in bucket
        response = s3.list_objects_v2(Bucket=bucketName)

        # Find latest object based on LastModified
        latest_object = None 
        for obj in response['Contents']:
            obj_time = obj['LastModified']
            if latest_object is None or obj_time > latest_object['LastModified']:
                latest_object = obj

        image_path = obj['Key']

        obj = s3.get_object(Bucket=bucketName, Key=image_path)
        print("Object retrieved from S3")
        metadata = obj['Metadata']
        prompt = metadata['prompt']
        recipients = os.environ['RECIPIENTS'].split(',')


    print(metadata)

    print("Sending email to " + str(recipients) + "...")
    send_email.send_image_email(recipients, obj, image_path, prompt)
    print("Email sent!")

def generate_blank_image():
    # generate a blank image
    image = Image.new('RGB', (100, 100))
    byte_arr = io.BytesIO()
    image.save(byte_arr, format='JPEG')
    image = byte_arr.getvalue()
    return image

def lambda_handler(event, context):
    try:
        send_bear_image()
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == "__main__":
    load_dotenv()
    send_bear_image()
