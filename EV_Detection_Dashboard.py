import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from pymongo import MongoClient
import bcrypt
from streamlit_cookies_manager import CookieManager
import time
import gridfs
from bson.objectid import ObjectId
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

# Set page config at the very beginning
st.set_page_config(page_title="EV Detection System", layout="wide", page_icon="🚗")

# Custom CSS for styling
st.markdown("""
<style>
    /* Main page styles */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    body {
        color: #333;
        background-color: #f0f8ff;
    }

    h1, h2, h3 {
        color: #2e7d32;
    }

    /* Sidebar styles */
    [data-testid="stSidebar"] {
        background-color: #4ade80;
        padding-top: 2rem;
    }
    [data-testid="stSidebar"] .sidebar-content {
        background-color: #4ade80;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: black;
        font-size: 1.2rem;
        font-weight: 600;
        padding: 0.5rem 0;
        margin-left: 0.5rem;
    }
    
    /* Main Menu styles */
    [data-testid="stSidebar"] .st-bk {
        background-color: transparent !important;
    }
    [data-testid="stSidebar"] .st-co {
        background-color: rgba(0, 0, 0, 0.1) !important;
    }
    [data-testid="stSidebar"] .st-cu {
        border-radius: 0 !important;
    }
    [data-testid="stSidebar"] .st-cx {
        padding: 0.5rem 0.25rem !important;
    }
    [data-testid="stSidebar"] .st-cy {
        padding-left: 0.5rem !important;
    }
    [data-testid="stSidebar"] .st-dk {
        font-weight: 600 !important;
    }

    /* Button styles */
    .stButton > button {
        color: #ffffff;
        background-color: #4CAF50;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
        text-align: left;
        display: flex;
        align-items: center;
    }
    .stButton > button:hover {
        background-color: #21feea;
        color: black;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton > button > svg {
        margin-right: 0.5rem;
    }

    .logout-button {
        background-color: #ff4b4b;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
        border: none;
        cursor: pointer;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }
    .logout-button:hover {
        background-color: #ff3333;
    }

</style>
<div class="decoration-top"></div>
<div class="decoration-bottom"></div>
""", unsafe_allow_html=True)

# Check the current theme
is_dark_theme = st.config.get_option("theme.base") == "dark"

# Apply conditional styling
if is_dark_theme:
    text_color = "white"
    font="serif"
else:
    text_color = "black"
    font="serif"


# Initialize cookie manager
cookies = CookieManager()

# Function to wait for cookies to be ready
def wait_for_cookies():
    timeout = 10  # Maximum wait time in seconds
    start_time = time.time()
    while not cookies.ready():
        if time.time() - start_time > timeout:
            st.error("Cookie manager timed out. Please refresh the page.")
            st.stop()
        time.sleep(0.1)

# Wait for cookies to be ready
wait_for_cookies()

# Connect to MongoDB
client = MongoClient("mongodb+srv://Extremenop:Nop24681036@cardb.ynz57.mongodb.net/?retryWrites=true&w=majority&appName=Cardb")
db = client['cardb']
users_collection = db['users']
nonev_collection = db['nonev']
fs = gridfs.GridFS(db)

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'evdetectionsystem@gmail.com'  # Replace with your email
EMAIL_HOST_PASSWORD = 'efhu ncmo rgga dksk'  # Replace with your app password

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None
if 'otp' not in st.session_state:
    st.session_state.otp = None
if 'otp_email' not in st.session_state:
    st.session_state.otp_email = None
if 'registration_step' not in st.session_state:
    st.session_state.registration_step = 'initial'
if 'forgot_password_step' not in st.session_state:
    st.session_state.forgot_password_step = 'initial'

# Hashing password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Verifying password
def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

# Generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Send email
def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# Login user function
def login_user(username, password):
    user = users_collection.find_one({"username": username})
    if user and verify_password(user['password'], password):
        st.session_state.logged_in = True
        st.session_state.username = username
        cookies['username'] = username
        cookies['logged_in'] = True
        cookies.save()
        st.success("Login successful! Redirecting to dashboard...")
        st.rerun()
    else:
        st.error("Invalid username or password.")

# Register user function with OTP verification
def register_user(username, password, email):
    if users_collection.find_one({"username": username}):
        st.error("Username already exists. Please choose a different username.")
    elif users_collection.find_one({"email": email}):
        st.error("Email already registered. Please use a different email.")
    else:
        otp = generate_otp()
        st.session_state.otp = otp
        st.session_state.otp_email = email
        if send_email(email, "OTP for Registration", f"Your OTP is: {otp}"):
            st.success("OTP sent to your email. Please check and enter below.")
            return True
    return False

# Verify OTP and complete registration
def verify_otp_and_register(username, password, email, entered_otp):
    if entered_otp == st.session_state.otp and email == st.session_state.otp_email:
        hashed_password = hash_password(password)
        users_collection.insert_one({"username": username, "password": hashed_password, "email": email})

        st.session_state.otp = None
        st.session_state.otp_email = None
        st.session_state.registration_step = 'initial'
        return True
    else:
        st.error("Invalid OTP. Please try again.")
        return False

# Password recovery function
def recover_password(email):
    user = users_collection.find_one({"email": email})
    if user:
        otp = generate_otp()
        st.session_state.otp = otp
        st.session_state.otp_email = email
        if send_email(email, "OTP for Password Recovery", f"Your OTP is: {otp}"):
            st.success("OTP sent to your email. Please check and enter below.")
            st.session_state.forgot_password_step = 'verify_otp'
            return True
    else:
        st.error("Email not found. Please check and try again.")
    return False

# Verify OTP and reset password
def verify_otp_and_reset_password(email, entered_otp, new_password):
    if entered_otp == st.session_state.otp and email == st.session_state.otp_email:
        hashed_password = hash_password(new_password)
        users_collection.update_one({"email": email}, {"$set": {"password": hashed_password}})
        st.success("Password reset successful! Please log in with your new password.")
        st.session_state.otp = None
        st.session_state.otp_email = None
        st.session_state.forgot_password_step = 'initial'
        return True
    else:
        st.error("Invalid OTP. Please try again.")
        return False
    
# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.current_page = 'home'
    cookies['logged_in'] = False
    cookies['username'] = None
    cookies.save()
    st.rerun()

# Function to get NON-EV image counts
def get_nonev_counts(start_date, end_date):
    pipeline = [
        {
            "$match": {
                "timestamp": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }
        },
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": {"$toDate": "$timestamp"}}},
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]
    result = list(nonev_collection.aggregate(pipeline))
    df = pd.DataFrame(result)
    if not df.empty:
        df.columns = ['date', 'value']
        df['date'] = pd.to_datetime(df['date'])
    else:
        df = pd.DataFrame(columns=['date', 'value'])
    return df

# Check login status from cookies
if not st.session_state.logged_in:
    if cookies.get('logged_in', False) and cookies.get('username'):
        st.session_state.logged_in = True
        st.session_state.username = cookies.get('username')

# Main application logic
if st.session_state.logged_in:
    # Sidebar navigation
    with st.sidebar:
        st.title("🚗 EV Detection")
        selected = st.radio(
            "Main Menu",
            ["Dashboard", "NON-EV Detected", "Messages", "Settings"],
            format_func=lambda x: f"{'🏠' if x == 'Dashboard' else '📷' if x == 'NON-EV Detected' else '✉️' if x == 'Messages' else '⚙️'} {x}"
        )
        st.session_state.current_page = selected.lower()

        # Use a container to apply the custom class to the logout button
        if st.sidebar.button("Logout", key="logout_button", on_click=logout, help="Click to log out"):
            st.markdown('<button class="logout-button">Logout</button>', unsafe_allow_html=True)

    # Page content
    if st.session_state.current_page == "non-ev detected":
        st.title("📸 NON-EV Images Detected")
        
        # Fetch all NON-EV image metadata from the database
        all_images = list(nonev_collection.find().sort('timestamp', -1))
        
        # Create a DataFrame for the table
        df = pd.DataFrame(all_images)
        df['_id'] = df['_id'].astype(str)
        df['file_id'] = df['file_id'].astype(str)
        
        # Display the table
        st.dataframe(df.style.set_properties(**{'background-color': 'white', 'color': 'black'}))
        
        # Display total number of images
        st.write(f"Total number of images: {len(all_images)}")
        
        # Allow user to select an image to view
        selected_image_id = st.selectbox("Select an image to view", df['_id'].tolist())
        
        if selected_image_id:
            try:
                # Find the corresponding document in the collection using _id
                image_doc = nonev_collection.find_one({'_id': ObjectId(selected_image_id)})
                if image_doc:
                    # Use the file_id from the document to retrieve the image
                    file_id = image_doc['file_id']
                    image_data = fs.get(ObjectId(file_id)).read()
                    image = Image.open(BytesIO(image_data))
                    
                    # Display the selected image
                    st.image(image, caption=f"Image ID: {selected_image_id}", use_column_width=True)
                    
                    # Display additional information
                    st.write(f"Timestamp: {image_doc['timestamp']}")
                    st.write(f"Event: {image_doc['event']}")
                else:
                    st.error(f"No metadata found for image with ID: {selected_image_id}")
            except gridfs.errors.NoFile as e:
                st.error(f"No file found with ID: {selected_image_id}. Please check the ID and try again.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    elif st.session_state.current_page == "dashboard":
        st.title("📊 EV Detection Dashboard")
        
        # Date range selector in main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📅 Select Date Range")
            date_option = st.selectbox(
                "Choose a date range",
                ("Custom", "Last 24 Hours", "Last 7 Days", "Last 14 Days", "Last 30 Days", "Last 6 Months")
            )

            end_date = datetime.now()

            if date_option == "Custom":
                start_date = st.date_input("Start date", end_date - timedelta(days=30))
                end_date = st.date_input("End date", end_date)
                if start_date > end_date:
                    st.error("Error: End date must be after start date.")
            else:
                if date_option == "Last 24 Hours":
                    start_date = end_date - timedelta(hours=24)
                elif date_option == "Last 7 Days":
                    start_date = end_date - timedelta(days=7)
                elif date_option == "Last 14 Days":
                    start_date = end_date - timedelta(days=14)
                elif date_option == "Last 30 Days":
                    start_date = end_date - timedelta(days=30)
                else:  # Last 6 Months
                    start_date = end_date - timedelta(days=180)

        with col2:
            st.subheader("📢 Notifications")
            st.info("🆕 New EV model detected")
            st.info("📈 Detection rate increased")
            st.info("📊 Weekly report available")

        # Get NON-EV image count data
        df = get_nonev_counts(start_date, end_date)

        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total NON-EV Detections", f"{df['value'].sum():,}", delta="5%")
        with col2:
            st.metric("Average Daily NON-EV Detections", f"{df['value'].mean():.2f}", delta="-2%")

        # NON-EV Detections Trend
        st.subheader("📉 NON-EV Detections Trend")
        fig_trend = px.line(df, x='date', y='value', title='NON-EV Detections Over Time')
        fig_trend.update_traces(line_color="#4ade80")
        fig_trend.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#1e3a8a'
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # Monthly Comparison (if applicable)
        if (end_date - start_date).days >= 30:
            st.subheader("📊 Monthly Comparison")
            df_monthly = df.set_index('date').resample('M').sum().reset_index()
            fig_bar = px.bar(df_monthly, x='date', y='value', title='Monthly NON-EV Detections')
            fig_bar.update_traces(marker_color="#4ade80")
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#1e3a8a'
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Top NON-EV Events (using actual data)
        st.subheader("🏆 Top NON-EV Events")
        top_events = nonev_collection.aggregate([
            {"$group": {"_id": "$event", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ])
        top_events_df = pd.DataFrame(list(top_events))
        if not top_events_df.empty:
            fig_pie = px.pie(top_events_df, values='count', names='_id', title='Top NON-EV Events Detected')
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#1e3a8a'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.write("No NON-EV events data available.")

    elif st.session_state.current_page == "messages":
        st.title("📫 Messages")
        st.write("This feature is coming soon. Stay tuned for updates!")
        
        # Placeholder for future message functionality
        st.info("Here you'll be able to view and manage system notifications and user messages.")

    elif st.session_state.current_page == "settings":
        st.title("⚙️ Settings")
        st.subheader("User Profile")
        st.write(f"Username: {st.session_state.username}")
        
        # Change password form
        st.subheader("Change Password")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        
        if st.button("Change Password"):
            user = users_collection.find_one({"username": st.session_state.username})
            if user and verify_password(user['password'], current_password):
                if new_password == confirm_new_password:
                    hashed_password = hash_password(new_password)
                    users_collection.update_one(
                        {"username": st.session_state.username},
                        {"$set": {"password": hashed_password}}
                    )
                    st.success("Password changed successfully!")
                else:
                    st.error("New passwords do not match.")
            else:
                st.error("Current password is incorrect.")

        # Notification settings
        st.subheader("Notification Settings")
        email_notifications = st.checkbox("Receive email notifications", value=True)
        push_notifications = st.checkbox("Receive push notifications", value=True)
        
        if st.button("Save Notification Settings"):
            # Here you would typically save these settings to the user's profile in the database
            st.success("Notification settings saved!")

else:
    # Login and registration forms
    st.title("🚗 EV Detection System")

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        st.subheader("Login to your account")

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Login", key="login_button"):
                if username and password:
                    login_user(username, password)
                else:
                    st.error("Please enter both username and password.")
        with col2:
            if st.button("Forgot Password", key="forgot_password_button"):
                st.session_state.forgot_password_step = 'enter_email'

        if st.session_state.get('forgot_password_step') == 'enter_email':
            email = st.text_input("Enter your email", key="forgot_password_email")
            if st.button("Send OTP", key="send_otp_forgot_password"):
                if email:
                    if recover_password(email):
                        st.session_state.forgot_password_step = 'enter_otp'
                else:
                    st.error("Please enter your email.")

        if st.session_state.get('forgot_password_step') == 'enter_otp':
            otp = st.text_input("Enter OTP received in email", key="forgot_password_otp")
            new_password = st.text_input("Enter new password", type="password", key="new_password")
            if st.button("Reset Password", key="reset_password_button"):
                if otp and new_password:
                    if verify_otp_and_reset_password(st.session_state.otp_email, otp, new_password):
                        st.session_state.forgot_password_step = None
                else:
                    st.error("Please enter both OTP and new password.")

    with tab2:
        st.subheader("Create a new account")

        new_username = st.text_input("New Username", key="reg_username")
        new_password = st.text_input("New Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
        
        # Use columns to place the email input and Send OTP button side by side
        col1, col2 = st.columns([3, 1])
        with col1:
            email = st.text_input("Email", key="reg_email")
        with col2:
            send_otp = st.button("Send OTP", key="send_otp_button")

        # Use columns to place the OTP input and Resend OTP button side by side
        col3, col4 = st.columns([3, 1])
        with col3:
            otp_input = st.text_input("Enter OTP", key="reg_otp")
        with col4:
            resend_otp = st.button("Resend OTP", key="resend_otp_button")

        if send_otp or resend_otp:
            if email:
                if register_user(new_username, new_password, email):
                    st.session_state.temp_username = new_username
                    st.session_state.temp_password = new_password
            else:
                st.error("Please enter your email to send/resend OTP.")

        if st.button("Register", key="register_button"):
            if new_username and new_password and confirm_password and email and otp_input:
                if new_password == confirm_password:
                    if otp_input == st.session_state.otp and email == st.session_state.otp_email:
                        if verify_otp_and_register(new_username, new_password, email, otp_input):
                            st.success("Registration successful! You can now log in.")
                            # Clear temporary storage
                            st.session_state.temp_username = None
                            st.session_state.temp_password = None
                            st.session_state.otp = None
                            st.session_state.otp_email = None
                    else:
                        st.error("Invalid OTP. Please try again or request a new OTP.")
                else:
                    st.error("Passwords do not match. Please try again.")
            else:
                st.error("Please fill out all fields, including the OTP.")

    st.markdown("---")
    st.write("For support, please contact the system administrator.")

# Add some decorative elements
st.markdown("""
<div style="text-align: center; margin-top: 50px;">
    <h3>🌿 Driving towards a greener future 🌿</h3>
    <p style="font-style: italic;">Empowering sustainable transportation through advanced EV detection.</p>
</div>
""", unsafe_allow_html=True)
                    