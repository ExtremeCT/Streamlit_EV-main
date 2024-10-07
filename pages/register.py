import streamlit as st
import bcrypt
import datetime as dt
# from utils.utils import send_email, getOTP
from email_validator import validate_email, EmailNotValidError
from time import sleep

def signup_verify_message(otp):
    return f"""
    <html>
        <body>
            <p>You have registered for the EV Detection System with Computer Vision</p>
            <p>Please enter the OTP code to confirm</p>
            <p>OTP Code: {otp['otp_code']}</p>
            <p>Reference Code: {otp['ref_code']}</p>
            <p><h3>** This OTP code is valid for 3 minutes **</h3></p>
            <p><h3>** Please do not share this OTP code with anyone **</h3></p>
            <p>This is an automated email. Please do not reply.</p>
        </body>
    </html>
    """

def back_to_login():
    if 'email_valid' in st.session_state:
        del st.session_state.email_valid
    
    if 'pswd_valid' in st.session_state:
        del st.session_state.pswd_valid
        
    st.switch_page("streamlit_app.py")

def checkEmail(mail):
    user_dict = list(st.session_state.client[st.secrets["mongo"]["user"]].find({
        'user_mail': mail
    }))
    
    if len(mail) == 0:
        return 1  # Email not entered
    elif " " in mail:
        return 2  # Email contains spaces
    elif len(user_dict) > 0:
        return 3  # Email already in use
    else:
        try:                
            validate_email(mail, check_deliverability=True)
        except EmailNotValidError as e:
            return 4  # Invalid email format
        else:
            return 0  # Valid email

def checkPassword(pswd1, pswd2):
    if len(pswd1) == 0:
        return 1  # Password not entered
    elif " " in pswd1:
        return 2  # Password contains spaces
    elif len(pswd1) < 6:
        return 3  # Password shorter than 6 characters
    elif len(pswd2) == 0:
        return 4  # Confirmation password not entered
    elif pswd1 != pswd2:
        return 5  # Passwords don't match
    else:
        return 0  # Valid password

def signup_confirm():
    st.session_state.email_valid = checkEmail(new_mail.lower())
    st.session_state.pswd_valid = checkPassword(new_pswd, con_pswd)
    
    if st.session_state.email_valid == 0 and st.session_state.pswd_valid == 0:
        recipient = new_mail.lower()
        salt = bcrypt.gensalt()
        byte_pswd = bytes(new_pswd, 'utf-8')
        hash_password = bcrypt.hashpw(byte_pswd, salt)
        otp = getOTP()

        email_payload = {
            'subject': "noreply: Confirm your registration",
            'body': signup_verify_message(otp)
        }

        if send_email(recipient, email_payload) == "success":
            st.session_state.otp_code = otp['otp_code']
            st.session_state.ref_code = otp['ref_code']
            st.session_state.otp_time = dt.datetime.today()
            st.session_state.new_page = 'signin'
            
            st.session_state.signin_payload = {
                "user_mail": recipient,
                "password": hash_password,
                "salt": salt,
                "inUse": False
            }
        else:
            st.session_state.email_valid = 6
            st.session_state.pswd_valid = 6

# Custom CSS to match the theme
st.markdown("""
<style>
    body {
        color: black;
        background-color: white;
    }
    .stTextInput>div>div>input {
        color: black;
        border: 1px solid black;
    }
    .stButton>button {
        color: white;
        background-color: #4ade80;
        border: 1px solid #4ade80;
    }
    .stButton>button:hover {
        color: #4ade80;
        background-color: white;
        border: 1px solid #4ade80;
    }
</style>
""", unsafe_allow_html=True)

st.title("EV Detection System Sign Up")

with st.container():
    new_mail = st.text_input(label="Email", placeholder="Enter your email")
    
    if "email_valid" in st.session_state:
        if st.session_state.email_valid == 1: 
            st.error("❌ Please enter an email")
        elif st.session_state.email_valid == 2:
            st.error("❌ Email must not contain spaces")
        elif st.session_state.email_valid == 3:
            st.error("❌ This email is already in use")
        elif st.session_state.email_valid == 4:
            st.error("❌ Invalid email format")
        elif st.session_state.email_valid == 0:
            st.success("✔️ Valid email")
        
    new_pswd = st.text_input("Password", type="password", 
                help="Password must be at least 6 characters long", placeholder="Enter password")
    
    con_pswd = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
    
    if "pswd_valid" in st.session_state:
        if st.session_state.pswd_valid == 1:
            st.error("❌ Please enter a password")
        elif st.session_state.pswd_valid == 2:
            st.error("❌ Password must not contain spaces")
        elif st.session_state.pswd_valid == 3:
            st.error("❌ Password must be at least 6 characters long") 
        elif st.session_state.pswd_valid == 4:
            st.error("❌ Please confirm your password")
        elif st.session_state.pswd_valid == 5:
            st.error("❌ Passwords do not match")
        elif st.session_state.pswd_valid == 0:
            st.success("✔️ Valid password")
    
    if "pswd_valid" in st.session_state and "email_valid" in st.session_state:
        if st.session_state.email_valid == 0 and st.session_state.pswd_valid == 0:
            del st.session_state.email_valid
            del st.session_state.pswd_valid        
            sleep(1)
            st.switch_page('pages/otp.py')
        elif st.session_state.email_valid == 6 and st.session_state.pswd_valid == 6:
            st.error("❌ Unable to send OTP. Please try again.")            
                
    confirm = st.button("Sign Up", use_container_width=True, type="primary",
            on_click=signup_confirm
    )

backToLogin = st.button("Back to Login", use_container_width=True)

if backToLogin:
    back_to_login()