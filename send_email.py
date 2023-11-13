import datetime
import os
import smtplib
from email.message import EmailMessage

def send_image_email(recipients, image_path, message_body):
  sender_email = os.environ['SENDER_EMAIL']
  sender_pass = os.environ['SENDER_PASS']
  
  msg = EmailMessage()
  #Include timestamp as Day Month Year, with the month spelled out
  msg['Subject'] = "Bear of the Day for " + datetime.datetime.now().strftime("%d %B %Y") 
  msg['From'] = sender_email
  msg['To'] = ", ".join(recipients)

  msg.set_content(message_body)
  
  with open(image_path, 'rb') as f:
    image_data = f.read()
    image_name = image_path.split('/')[-1]

  msg.add_attachment(image_data, maintype='image', subtype='jpeg', filename=image_name)

  with smtplib.SMTP('smtp.gmail.com', 587) as smtp: 
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    
    smtp.login(sender_email, sender_pass)
    smtp.send_message(msg)