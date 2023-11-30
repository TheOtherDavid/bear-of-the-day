import datetime
from dotenv import load_dotenv
from PIL import Image
import io
import os
import random
import requests
import sys
import common.config as config
import common.dalle as dalle
import common.s3 as s3
import common.send_email as send_email

def bear_of_the_day():
    """
    This function generates an image using DALL-E based on a randomly selected style and scene.
    The generated image is then saved to an S3 bucket and emailed to the user.

    If the DEBUG_MODE environment variable is set to True, the function will generate a blank image instead.

    The function reads the style and scene data from 'subjects.csv', 'spirits.csv', and 'scenes.csv' files.

    The AWS_BUCKET_NAME and RECIPIENTS environment variables must be set. RECIPIENTS is a comma-separated list of email addresses.

    If the image generation or email sending fails, the function will print an error message and exit with a status code of 1.
    """
    
    config.verify_environment()
    # Load Debug Mode Variable
    debug_mode = os.environ.get('DEBUG_MODE', 'False') == 'True'

    # load the style CSV file into an array
    subjects = load_data_file('backend/subjects.csv')
    scenes = load_data_file('backend/scenes.csv')
    spirits = load_data_file('backend/spirits.csv')
    
    if debug_mode:
        print("DEBUG MODE")
        image = generate_blank_image()
        prompt = "DEBUG MODE"
    else:
        # randomly select image elements
        subject = random.choice(subjects)
        scene = random.choice(scenes)

        spirits_copy = spirits[:]
        spirit1 = random.choice(spirits)
        spirits_copy.remove(spirit1)
        spirit2 = random.choice(spirits_copy)

        prompt = subject + " " + scene + ",  " + spirit1 + ", " + spirit2
        print(prompt)
        # generate the image
        image_url = dalle.generate_image(prompt)
        if image_url is None:
            print("Failed to generate image.")
            sys.exit(1)
        print(image_url)
        image = requests.get(image_url).content

    # save the image to a file with the timestamp
    image_path = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.jpg'
    print(image_path)

    bucket_name = os.environ['AWS_BUCKET_NAME']
    try:
        s3.save_image_to_s3(image, bucket_name, image_path, prompt)
    except Exception as e:
        print(f"Failed to save image to S3: {e}")
        sys.exit(1)

    # email the image to the user
    if debug_mode:
        recipients = [os.environ['DEBUG_RECIPIENTS']]
    else:
        recipients = os.environ['RECIPIENTS'].split(',')
    print("Sending email to " + str(recipients) + "...")
    send_email.send_image_email(recipients, image, image_path, prompt)
    print("Email sent!")

def load_data_file(filename):
    with open(filename) as f:
        data = f.read().splitlines() 
    return data

def download_image(url, file_path):
    response = requests.get(url)
    with open(file_path, 'wb') as f:
        f.write(response.content)

def generate_blank_image():
    # generate a blank image
    image = Image.new('RGB', (100, 100))
    byte_arr = io.BytesIO()
    image.save(byte_arr, format='JPEG')
    image = byte_arr.getvalue()
    return image

# AWS Lambda handler
def lambda_handler(event, context):
    try:
        bear_of_the_day()
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == "__main__":
    load_dotenv()
    bear_of_the_day()
