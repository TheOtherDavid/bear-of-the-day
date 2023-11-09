import csv
import datetime
from dotenv import load_dotenv
import os
import random
import requests
import dalle
import s3
import send_email

load_dotenv()
# This is an app that will randomly select a style and a scene from files, construct a prompt, and then call DALL-E image generation.
# The image will then be saved to an S3 bucket and emailed to the user.
def bear_of_the_day():
    # load the style CSV file into an array
    #These are all wrong, they're all coming in as dicts and not arrays
    subjects = load_data_file('subjects.csv')
    styles = load_data_file('styles.csv')
    scenes = load_data_file('scenes.csv')

    #randomly select a style
    subject = random.choice(subjects)
    style = random.choice(styles)
    scene = random.choice(scenes)
    prompt = subject + " " + scene + " in the style of " + style 
    print(prompt)
    #generate the image
    image_url = dalle.generate_image(prompt)
    print(image_url)

    #save the image to a file with the timestamp
    image_path = 'static/images/' + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.jpg'
    download_image(image_url, image_path)

    #save the image to S3
    #s3.save_image_to_s3(image_url)
    #email the image to the user
    recipients = os.environ['RECIPIENTS'].split(',')
    print("Sending email to " + str(recipients) + "...")
    send_email.send_image_email(recipients, image_path)
    print("Email sent!")

def load_data_file(filename):
    with open(filename) as f:
        data = f.read().splitlines() 
    return data

def download_image(url, file_path):
    response = requests.get(url)
    with open(file_path, 'wb') as f:
        f.write(response.content)

if __name__ == "__main__":
    bear_of_the_day()
