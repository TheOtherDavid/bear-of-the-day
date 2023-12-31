from dotenv import load_dotenv
from PIL import Image
import io
import os
import common.s3 as s3
import common.send_email as send_email

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
        obj, metadata, image_path = s3.get_latest_file(bucketName)
        print("Object retrieved from S3")
        prompt = metadata['prompt']
        recipients = os.environ['RECIPIENTS'].split(',')

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
