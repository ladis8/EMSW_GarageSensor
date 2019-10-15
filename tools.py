"""
\file       tools.py
\author     Jake Hunt 
\brief      A variety of functions used for different purposes - sending email,...  
\copyright  none

"""

import smtplib, ssl
import logging

PORT = 587  # For SSL
SENDER_ADDRESS = "ense810Project@gmail.com"
PASSWORD = "Raspberrygmail"
RECEIVER_ADDRESS = ["stefka885@gmail.com"]


# Create a secure SSL context
def send_notification_email(date):

    context = ssl.create_default_context()

    with smtplib.SMTP("smtp.gmail.com", PORT) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(SENDER_ADDRESS, PASSWORD)

        subject = "Garage sensor notification"
        message = "MESSAGE {}: HUMAN DETECTED".format(date)
        email_text = 'Subject: {}\n\n{}'.format(subject, message)

        server.sendmail(SENDER_ADDRESS, RECEIVER_ADDRESS, email_text )
        logging.info("Email has been sent...")
        server.quit()

