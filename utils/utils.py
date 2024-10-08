import streamlit as st
import math, random, string
from email.mime.text import MIMEText
import smtplib

def send_email(recipient, payload):
    
    sender = st.secrets['mastermail']['email']
    body = payload['body']
    
    msg = MIMEText(body, 'html')
    msg['Subject'] = payload['subject']
    msg['From'] = sender
    msg['To'] = recipient
    
    try:        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, st.secrets['mastermail']['password'])
        server.sendmail(sender, recipient, msg.as_string())
        server.quit()
    except Exception as e:
        print(e)
        return "failed"
    else:
        return "success"
    

def getOTP() :
    digits = "0123456789"
    otp_payload = {}
    otp_payload['otp_code'] = ''.join([digits[math.floor(random.random() * 10)] for _ in range(6) ])
    otp_payload['ref_code'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return otp_payload    
