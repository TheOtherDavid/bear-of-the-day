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
        image_data = generate_blank_image()
        prompt = "DEBUG MODE"
        metadata = {"prompt": prompt}
        image_path = "debug.jpg"
        recipients = [os.environ['DEBUG_RECIPIENTS']]
    else:
        obj, metadata, image_path = s3.get_latest_file(bucketName)
        print("Object retrieved from S3")
        image_data = obj['Body'].read()
        prompt = metadata['prompt']
        recipients = os.environ['RECIPIENTS'].split(',')

    # The stored image is a ~2MB PNG (great for the S3 gallery, heavy for email).
    # Re-encode to JPEG for the attachment only; the S3 original is untouched.
    image_data = compress_for_email(image_data)

    print("Sending email to " + str(recipients) + "...")
    send_email.send_image_email(recipients, image_data, image_path, prompt)
    print("Email sent!")

def compress_for_email(image_bytes, quality=85):
    """Re-encode image bytes (PNG or otherwise) to a JPEG suitable for email.

    Converts to RGB (flattening any alpha, which JPEG can't store) and saves at
    the given quality. At 1024x1024 this takes a ~2.4MB PNG down to ~350KB.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=quality, optimize=True)
    return out.getvalue()

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
