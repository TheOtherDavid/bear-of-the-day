import datetime
import os
import smtplib
import requests
from email.message import EmailMessage

def send_image_email(recipients, image_url, image_path, message_body):
  sender_email = os.environ['SENDER_EMAIL']
  sender_pass = os.environ['SENDER_PASS']
  
  msg = EmailMessage()
  #Include timestamp as Day Month Year, with the month spelled out
  msg['Subject'] = "Bear of the Day for " + datetime.datetime.now().strftime("%d %B %Y") 
  msg['From'] = sender_email
  msg['To'] = ", ".join(recipients)

  msg.set_content(message_body)
  
  image = requests.get(image_url).content
  image_path = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + '.jpg'

  msg.add_attachment(image, maintype='image', subtype='jpeg', filename=image_path)

  with smtplib.SMTP('smtp.gmail.com', 587) as smtp: 
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    
    smtp.login(sender_email, sender_pass)
    smtp.send_message(msg)