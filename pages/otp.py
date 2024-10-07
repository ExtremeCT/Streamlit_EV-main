import streamlit as st
import datetime as dt
from time import sleep
from utils.utils import send_email

def signin_complete_message():
    signin_time = dt.datetime.now()
    return f"""
    <html>
        <body>
            <p>You have successfully recovered your password</p>
            <p>Date: {signin_time.strftime("%d/%m/%y")}</p>
            <p>Time: {signin_time.strftime("%H:%M:%S")}</p>
            <p>This is an automated email. Please do not reply.</p>
        </body>
    </html>
    """    

def back_to_login():
    if st.session_state.new_page == 'signin':
        del st.session_state.signin_payload
    elif st.session_state.new_page == 'pswd_recover':
        del st.session_state.recover_mail

    del st.session_state.new_page
    del st.session_state.otp_code
    del st.session_state.ref_code
    del st.session_state.otp_time
    
    if 'otp_check' in st.session_state:
        del st.session_state.otp_check
    
    st.switch_page('streamlit_app.py')

def checkOTP():
    if len(otp) == 0:
        st.session_state.otp_check = 1
    else:
        if otp == st.session_state.otp_code:
            if dt.datetime.today() <= (st.session_state.otp_time + dt.timedelta(minutes=3)):                
                if st.session_state.new_page == 'signin':   
                    mail_payload = {
                        'subject': "noreply: Password Recovery Successful",
                        'body': signin_complete_message()
                    }
                    if send_email(st.session_state.signin_payload["user_mail"], mail_payload) == "success":
                        st.session_state.otp_check = 0
                    else:
                        st.session_state.otp_check = 4
                else:
                    st.session_state.otp_check = 0
            else:
                st.session_state.otp_check = 3
        else:
            st.session_state.otp_check = 2

st.title("EV Detection System OTP Verification")

with st.container():
    st.info(f'ℹ️ Reference Code: {st.session_state.ref_code}')   
    otp = st.text_input("Enter OTP", max_chars=6, type="password")
    
    if 'otp_check' in st.session_state:
        if st.session_state.otp_check == 1:
            st.error("❌ Please enter the OTP")
        elif st.session_state.otp_check == 2:
            st.error("❌ Invalid OTP")
        elif st.session_state.otp_check == 3:
            st.error("❌ OTP expired. Please request a new one")
        elif st.session_state.otp_check == 4:
            st.error("❌ Verification failed. Please try again")
        elif st.session_state.otp_check == 0:
            del st.session_state.otp_code
            del st.session_state.ref_code
            del st.session_state.otp_time
            del st.session_state.otp_check
                
            st.success("✔️ OTP verified successfully")
            if st.session_state.new_page == 'signin':
                st.session_state.client[st.secrets["mongo"]["user"]].insert_one(
                    st.session_state.signin_payload
                )
                del st.session_state.signin_payload
                
                st.toast("✔️ Registration successful")
                sleep(1)
                st.switch_page('streamlit_app.py')
            elif st.session_state.new_page == 'pswd_recover':
                st.switch_page('pages/pswd_new.py')

    submit_otp = st.button("Verify", use_container_width=True, 
        type="primary", on_click=checkOTP
    )

with st.expander("Back to Login"):
    st.markdown("Do you want to cancel?")
    login_button = st.button("Back to Login", use_container_width=True)
    
    if login_button:
        back_to_login()
