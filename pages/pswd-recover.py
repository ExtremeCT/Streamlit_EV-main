import streamlit as st
import math, random, string
from utils.utils import send_email, getOTP
import datetime as dt
from time import sleep

def otp_request_message(otp_payload):
    return f"""
    <html>
        <body>
            <p>You have requested a password reset</p>
            <p>OTP: {otp_payload['otp_code']}</p>
            <p>Reference Code: {otp_payload['ref_code']}</p>
            <p><h3>** This OTP is valid for 3 minutes **</h3></p>
            <p><h3>** Please do not share this OTP with anyone **</h3></p>
            <p>This is an automated email. Please do not reply.</p>
        </body>
    </html>
    """

def back_to_login():
    if 'recover' in st.session_state: del st.session_state.recover
    st.switch_page('streamlit_app.py')
    
def checkEmailInput():
    if len(search_mail) == 0:
        st.session_state.recover = 1
    else:
        user_dict = list(st.session_state.client[st.secrets["mongo"]["user"]].find({
            'user_mail': search_mail.lower()
        }))

        if len(user_dict) > 0:
            if user_dict[0]['inUse'] == True:
                st.session_state.recover = 3
            else:
                otp = getOTP()
                email_payload = {
                    'subject': "noreply: Password Reset",
                    'body': otp_request_message(otp)
                }
                
                if send_email(search_mail.lower(), email_payload) == "success":
                    st.session_state.otp_code = otp['otp_code']
                    st.session_state.ref_code = otp['ref_code']
                    st.session_state.otp_time = dt.datetime.today()
                    st.session_state.new_page = 'pswd_recover'
                    st.session_state.recover_mail = search_mail.lower()
        
                    st.session_state.recover = 0
                else:
                    st.session_state.recover = 4
        else:
            st.session_state.recover = 2

st.title("EV Detection System Password Recovery")

with st.container():
    search_mail = st.text_input("Enter your email")
    
    if 'recover' in st.session_state:
        if st.session_state.recover == 0:
            st.success("✔️ OTP sent successfully")
            del st.session_state.recover
            sleep(1)
            st.switch_page('pages/otp.py')
        elif st.session_state.recover == 1:
            st.error("❌ Please enter an email")
        elif st.session_state.recover == 2:
            st.error("❌ Email not found")
        elif st.session_state.recover == 3:
            st.error("❌ Cannot recover password. User is currently active")
        elif st.session_state.recover == 4:
            st.error("❌ Unable to send OTP. Please try again")

    recovery = st.button("Search Email", use_container_width=True, 
        type="primary", on_click=checkEmailInput
    )
    
login_ = st.button("Back to Login", use_container_width=True)

if login_:
    back_to_login()
