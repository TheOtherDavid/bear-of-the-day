import boto3
import datetime
import json
from dotenv import load_dotenv
import os
import random
import requests
import base64
import sys
import common.config as config
import common.dalle as dalle
import common.s3 as s3
import common.manifest as manifest

def bear_of_the_day():
    """
    This function generates an image using DALL-E based on a randomly selected style and scene.
    The generated image is then saved to an S3 bucket and emailed to the user.

    If the DEBUG_MODE environment variable is set to True, the function will generate a blank image instead.

    The function reads base prompt vocabulary from CSV files, plus monthly seasonal
    scenes and spirits from 'seasonal_content.json'.

    The AWS_BUCKET_NAME and RECIPIENTS environment variables must be set. RECIPIENTS is a comma-separated list of email addresses.

    If the image generation or email sending fails, the function will print an error message and exit with a status code of 1.
    """
    
    config.verify_environment()

    debug_mode = os.environ.get('DEBUG_MODE', 'False') == 'True'    

    sns = boto3.client('sns', region_name=os.environ['AWS_DEFAULT_REGION'])

    # load base prompt vocabulary and month-specific seasonal content
    script_dir = os.path.dirname(os.path.abspath(__file__))

    subjects_file = load_data_file(os.path.join(script_dir, 'subjects.csv'))
    scenes_file = load_data_file(os.path.join(script_dir, 'scenes.csv'))
    spirits_file = load_data_file(os.path.join(script_dir, 'spirits.csv'))
    seasonal_content = load_seasonal_content(
        os.path.join(script_dir, 'seasonal_content.json')
    )
    # EventBridge runs at 13:00 UTC, so this month also matches the German local date.
    month_key = datetime.datetime.now(datetime.timezone.utc).strftime('%m')
    month_content = seasonal_content['months'][month_key]

    # randomly select image elements
    subject = random.choice(subjects_file)
    # add a 25% chance to add an S to the end of the subject, to make it plural
    if random.random() < 0.25:
        subject = subject + "s"

    # Choose a general or seasonal scene with equal probability.
    if random.random() < 0.5:
        scene = random.choice(month_content['scenes'])
    else:
        scene = random.choice(scenes_file)

    # Every prompt gets one general spirit and one seasonal spirit.
    normal_spirit = random.choice(spirits_file)
    seasonal_spirit_options = [
        spirit for spirit in month_content['spirits']
        if spirit.casefold() != normal_spirit.casefold()
    ]
    seasonal_spirit = random.choice(seasonal_spirit_options)
    spirits = [normal_spirit, seasonal_spirit]

    spirits_string = ", ".join(spirits)

    prompt = f"{subject} {scene}, {spirits_string}"
    print(prompt)
    model = "gpt-image-2"
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

    # Record the new image in the manifest so the gallery can filter on it.
    # A manifest hiccup must never block image delivery; rebuild_manifest self-heals.
    try:
        entry = manifest.entry_from_metadata(image_path, {
            'subject': subject,
            'scene': scene,
            'spirits': spirits_string,
            'model': model,
            'prompt': prompt,
        })
        manifest.append_entry(bucket_name, entry)
        print("Manifest updated.")
    except Exception as e:
        print(f"Warning: failed to update manifest (will self-heal on rebuild): {e}")

    # Publish a message to the SNS topic to trigger downstream functions
    if debug_mode == False:
        sns.publish(
            TopicArn=os.environ['SNS_TOPIC_ARN'],
            Message='BearOfTheDayFunction completed'
        )

def load_data_file(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read().splitlines()


def load_seasonal_content(filename):
    with open(filename, encoding='utf-8') as f:
        content = json.load(f)

    if not isinstance(content, dict) or not isinstance(content.get('months'), dict):
        raise ValueError("Seasonal content must contain a 'months' object.")

    months = content['months']
    expected_months = {f'{month:02d}' for month in range(1, 13)}
    if set(months) != expected_months:
        raise ValueError("Seasonal content must define month keys '01' through '12'.")

    for month_key, month_content in months.items():
        if not isinstance(month_content, dict):
            raise ValueError(f"Seasonal content for month {month_key} must be an object.")

        scenes = month_content.get('scenes')
        spirits = month_content.get('spirits')
        if (
            not isinstance(scenes, list)
            or not scenes
            or any(not isinstance(scene, str) or not scene.strip() for scene in scenes)
        ):
            raise ValueError(f"Month {month_key} must have at least one scene and no blank entries.")
        if (
            not isinstance(spirits, list)
            or len(spirits) != 8
            or any(not isinstance(spirit, str) or not spirit.isalpha() for spirit in spirits)
            or len({spirit.casefold() for spirit in spirits}) != 8
        ):
            raise ValueError(
                f"Month {month_key} must have exactly 8 distinct single-word seasonal spirits."
            )

    return content


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
