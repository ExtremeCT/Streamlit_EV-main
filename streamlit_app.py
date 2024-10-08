import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from pymongo import MongoClient
import bcrypt
import smtplib
from email.mime.text import MIMEText
import random
import string

# Set page config
st.set_page_config(page_title="EV Detection System", layout="wide")

# Connect to MongoDB
client = MongoClient("mongodb+srv://Extremenop:Nop24681036@cardb.ynz57.mongodb.net/?retryWrites=true&w=majority&appName=Cardb")
db = client['cardb']
users_collection = db['users']

# Custom CSS for styling (unchanged)
st.markdown("""<style>
    [data-testid="stSidebar"] {
        background-color: #4ade80;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, 
    [data-testid="stSidebar"] .css-1v3fvcr {
        color: #0072a4;
    }
    [data-testid="stSidebar"] .stButton>button {
        color: black;
        background-color: white;
        border: 2px solid black;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background-color: rgba(0,0,0,0.1);
        color: black;
        border: 2px solid black;
    }
    [data-testid="stSidebar"] .stTextInput>div>div>input {
        color: black;
        background-color: white;
        border-color: black;
    }
    [data-testid="stSidebar"] .stTextInput>div>div>input::placeholder {
        color: rgba(0,0,0,0.7);
    }
</style>""", unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'otp' not in st.session_state:
    st.session_state.otp = None
if 'email' not in st.session_state:
    st.session_state.email = None
if 'registration_step' not in st.session_state:
    st.session_state.registration_step = 'initial'

# Hashing password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Verifying password
def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

# Generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Send OTP via email
def send_otp(email, otp):
    sender_email = "your_email@gmail.com"  # Replace with your email
    sender_password = "your_email_password"  # Replace with your email password

    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = "OTP for EV Detection System Registration"
    msg['From'] = sender_email
    msg['To'] = email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send OTP: {str(e)}")
        return False

# Login user function
def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and verify_password(user['password'], password):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success("Login successful! Redirecting to dashboard...")
        st.rerun()
    else:
        st.error("Invalid username or password.")

# Register user function
def register_user(username, email, password):
    if users_collection.find_one({"$or": [{"username": username}, {"email": email}]}):
        st.error("Username or email already exists. Please choose different credentials.")
    else:
        otp = generate_otp()
        if send_otp(email, otp):
            st.session_state.otp = otp
            st.session_state.email = email
            st.session_state.registration_step = 'otp_verification'
            st.success("OTP sent to your email. Please verify.")
            return True
    return False

# Verify OTP and complete registration
def verify_otp_and_register(username, email, password, provided_otp):
    if provided_otp == st.session_state.otp:
        hashed_password = hash_password(password)
        users_collection.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password
        })
        st.success("Registration successful! Please log in.")
        st.session_state.otp = None
        st.session_state.email = None
        st.session_state.registration_step = 'initial'
        return True
    else:
        st.error("Invalid OTP. Please try again.")
        return False

# Main application logic
if st.session_state.logged_in:
    # Main content of the dashboard (unchanged)
    st.title("EV Detection Dashboard")
    # ... [Keep the existing dashboard code here] ...

else:
    # Login or registration forms
    st.title("Login to EV Detection System")

    menu = ["Login", "Register"]
    choice = st.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login to your account")

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        if st.button("Login"):
            if username and password:
                login_user(username, password)
            else:
                st.error("Please enter both username and password.")

    elif choice == "Register":
        st.subheader("Create a new account")

        if st.session_state.registration_step == 'initial':
            new_username = st.text_input("New Username", placeholder="Enter your username")
            new_email = st.text_input("Email", placeholder="Enter your email")
            new_password = st.text_input("New Password", type="password", placeholder="Enter your password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")

            if st.button("Register"):
                if new_username and new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        if register_user(new_username, new_email, new_password):
                            st.session_state.temp_username = new_username
                            st.session_state.temp_password = new_password
                    else:
                        st.error("Passwords do not match. Please try again.")
                else:
                    st.error("Please fill out all fields.")

        elif st.session_state.registration_step == 'otp_verification':
            st.info("Please check your email for OTP.")
            otp_input = st.text_input("Enter OTP", placeholder="Enter the OTP sent to your email")
            if st.button("Verify OTP"):
                if verify_otp_and_register(st.session_state.temp_username, st.session_state.email, st.session_state.temp_password, otp_input):
                    del st.session_state.temp_username
                    del st.session_state.temp_password

st.markdown("---")
st.write("For support, please contact the system administrator.")