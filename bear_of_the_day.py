import datetime
from dotenv import load_dotenv
from PIL import Image
import io
import os
import random
import requests
import sys
import dalle
import s3
import send_email

# This is an app that will randomly select a style and a scene from files, construct a prompt, and then call DALL-E image generation.
# The image will then be saved to an S3 bucket and emailed to the user.
def bear_of_the_day():
    # Load Debug Mode Variable
    debug_mode = os.environ.get('DEBUG_MODE', 'False') == 'True'

    # load the style CSV file into an array
    subjects = load_data_file('subjects.csv')
    styles = load_data_file('styles.csv')
    scenes = load_data_file('scenes.csv')
    
    if debug_mode:
        image = generate_blank_image()
    else:
        # randomly select a style
        subject = random.choice(subjects)
        style = random.choice(styles)
        scene = random.choice(scenes)
        prompt = subject + " " + scene + " in the style of " + style 
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
