import boto3
import datetime
from dotenv import load_dotenv
import os
import random
import requests
import base64
import sys
import common.config as config
import common.dalle as dalle
import common.s3 as s3

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

    debug_mode = os.environ.get('DEBUG_MODE', 'False') == 'True'    

    sns = boto3.client('sns', region_name=os.environ['AWS_DEFAULT_REGION'])

    # load the CSV files into arrays
    script_dir = os.path.dirname(os.path.abspath(__file__))

    subjects_file = load_data_file(os.path.join(script_dir, 'subjects.csv'))
    scenes_file = load_data_file(os.path.join(script_dir, 'scenes.csv'))
    spirits_file = load_data_file(os.path.join(script_dir, 'spirits.csv'))
    
    # randomly select image elements
    subject = random.choice(subjects_file)
    # add a 25% chance to add an S to the end of the subject, to make it plural
    if random.random() < 0.25:
        subject = subject + "s"

    scene = random.choice(scenes_file)

    spirits_copy = spirits_file[:]
    spirit1 = random.choice(spirits_file)
    spirits_copy.remove(spirit1)
    spirit2 = random.choice(spirits_copy)

    #Here is where you can hardcode another spirit, like "Christmassy"
    spirit_special = ""

    if spirit_special == "":
        spirits = [spirit1, spirit2]
    else:
        spirits = [spirit1, spirit2, spirit_special]

    spirits_string = ", ".join(spirits)

    prompt = subject + " " + scene + ",  " + spirits_string
    print(prompt)
    model = "gpt-image-1"
    image_base64 = dalle.get_gpt_base64_image(model, prompt)
    if image_base64 is None:
        print("Failed to generate image.")
        sys.exit(1)
    image = decode_base64_image(image_base64)

    # save the image to a file with the timestamp
    image_path = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.jpg'
    print(image_path)

    bucket_name = os.environ['AWS_BUCKET_NAME']
    try:
        s3.save_image_to_s3(image, bucket_name, image_path, prompt, subject, scene, spirits, model)
    except Exception as e:
        print(f"Failed to save image to S3: {e}")
        sys.exit(1)
    # Publish a message to the SNS topic to trigger downstream functions
    if debug_mode == False:
        sns.publish(
            TopicArn=os.environ['SNS_TOPIC_ARN'],
            Message='BearOfTheDayFunction completed'
        )

def load_data_file(filename):
    with open(filename) as f:
        data = f.read().splitlines() 
    return data

def download_image(url, file_path):
    response = requests.get(url)
    with open(file_path, 'wb') as f:
        f.write(response.content)

def lambda_handler(event, context):
    try:
        bear_of_the_day()
    except Exception as e:
        print(f"Error: {e}")
        raise e

def decode_base64_image(base64_image):
    image = base64.b64decode(base64_image)
    return image

if __name__ == "__main__":
    load_dotenv()
    bear_of_the_day()
