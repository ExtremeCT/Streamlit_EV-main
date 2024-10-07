import streamlit as st
import datetime as dt
import bcrypt
from time import sleep
from utils.utils import send_email

def recover_complete_message():
    recover_time = dt.datetime.now()
    return f"""
    <html>
        <body>
            <p>You have successfully recovered your password</p>
            <p>Date: {recover_time.strftime("%d/%m/%y")}</p>
            <p>Time: {recover_time.strftime("%H:%M:%S")}</p>
            <p>This is an automated email. Please do not reply.</p>
        </body>
    </html>
    """

def to_login():
    if 'pswd_valid' in st.session_state:
        del st.session_state.pswd_valid
    
    del st.session_state.recover_mail
    
    st.switch_page('streamlit_app.py')

def pswd_recover_confirm():
    if (len(new_pswd) == 0):
        st.session_state.pswd_valid = 1
    elif " " in new_pswd:
        st.session_state.pswd_valid = 2
    elif (len(new_pswd) < 5):
        st.session_state.pswd_valid = 3
    elif (len(con_pswd) == 0):
        st.session_state.pswd_valid = 4
    elif (new_pswd != con_pswd):
        st.session_state.pswd_valid = 5
    else:
        mail_payload = {
            'subject': "noreply: Password Recovery Successful",
            'body': recover_complete_message()
        }
        
        if send_email(st.session_state.recover_mail, mail_payload) == "success":
            salt = bcrypt.gensalt()
            byte_pswd = bytes(new_pswd, 'utf-8')
            hash_password = bcrypt.hashpw(byte_pswd, salt)
            
            new_pswd_payload = {
                "password": hash_password,
                "salt": salt
            }
            
            st.session_state.client[st.secrets["mongo"]["user"]].update_one(
                { "user_mail": st.session_state.recover_mail }, 
                { "$set": new_pswd_payload } 
            )
            
            st.session_state.user_set = list(
                st.session_state.client[st.secrets["mongo"]["user"]].find()
            )
            
            st.session_state.pswd_valid = 0
        else:
            st.session_state.pswd_valid = 6

st.title("EV Detection System Password Reset")
        
with st.container():
    new_pswd = st.text_input("Enter new password", type="password", 
                help="Password should be longer than 6 characters")
    
    con_pswd = st.text_input("Confirm new password", type="password")
    
    if "pswd_valid" in st.session_state:
        if st.session_state.pswd_valid == 1:
            st.error("❌ Please enter a password")
        elif st.session_state.pswd_valid == 2:
            st.error("❌ New password must not contain spaces")
        elif st.session_state.pswd_valid == 3:
            st.error("❌ Password should be longer than 5 characters")
        elif st.session_state.pswd_valid == 4:
            st.error("❌ Please confirm your password")
        elif st.session_state.pswd_valid == 5:
            st.error("❌ Passwords do not match")
        elif st.session_state.pswd_valid == 6:
            st.error("❌ Confirmation failed. Please try again")
        elif st.session_state.pswd_valid == 0:
            st.success("✔️ Password recovery successful")
            sleep(1)
            to_login()
                
    st.button("Confirm", use_container_width=True, type="primary",
        on_click=pswd_recover_confirm          
    )
    
with st.expander("Cancel", use_container_width=True):
    st.markdown("Do you want to cancel password change?")
    back_to_login = st.button("Cancel", use_container_width=True)
    
    if back_to_login:
        to_login()
