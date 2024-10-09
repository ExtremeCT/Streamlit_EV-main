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

# Set page config at the very beginning
st.set_page_config(page_title="EV Detection System", layout="wide")

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

# Custom CSS for styling
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
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'selected_image' not in st.session_state:
    st.session_state.selected_image = None

# Hashing password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Verifying password
def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

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

# Register user function
def register_user(username, password):
    if users_collection.find_one({"username": username}):
        st.error("Username already exists. Please choose a different username.")
    else:
        hashed_password = hash_password(password)
        users_collection.insert_one({"username": username, "password": hashed_password})
        st.success("Registration successful! Please log in.")

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
    # Sidebar
    st.sidebar.title("Navigation")
    if st.sidebar.button("Home"):
        st.session_state.current_page = 'home'
    if st.sidebar.button("Messages"):
        st.session_state.current_page = 'messages'
    if st.sidebar.button("NON-EV Detected"):
        st.session_state.current_page = 'latest_non_ev'
    if st.sidebar.button("Settings"):
        st.session_state.current_page = 'settings'

    # Logout button
    if st.sidebar.button("Logout"):
        logout()

    st.sidebar.text_input("Search...", "")

    # Page content
    if st.session_state.current_page == 'latest_non_ev':
        st.title("NON-EV Images Detected")
        
        # Fetch all NON-EV image metadata from the database
        all_images = list(nonev_collection.find().sort('timestamp', -1))
        
        # Create a DataFrame for the table
        df = pd.DataFrame(all_images)
        df['_id'] = df['_id'].astype(str)
        df['file_id'] = df['file_id'].astype(str)
        
        # Display the table
        st.dataframe(df)
        
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

    else:  # Default to home/dashboard
        st.title("EV Detection Dashboard")
        
        # Date range selector in main content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Select Date Range")
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
            st.subheader("Notifications")
            st.info("New EV model detected")
            st.info("Detection rate increased")
            st.info("Weekly report available")

        # Get NON-EV image count data
        df = get_nonev_counts(start_date, end_date)

        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total NON-EV Detections", f"{df['value'].sum():,}")
        with col2:
            st.metric("Average Daily NON-EV Detections", f"{df['value'].mean():.2f}")

        # NON-EV Detections Trend
        st.subheader("NON-EV Detections Trend")
        fig_trend = px.line(df, x='date', y='value', title='NON-EV Detections Over Time')
        fig_trend.update_traces(line_color="#4ade80")
        st.plotly_chart(fig_trend, use_container_width=True)

        # Monthly Comparison (if applicable)
        if (end_date - start_date).days >= 30:
            st.subheader("Monthly Comparison")
            df_monthly = df.set_index('date').resample('M').sum().reset_index()
            fig_bar = px.bar(df_monthly, x='date', y='value', title='Monthly NON-EV Detections')
            fig_bar.update_traces(marker_color="#4ade80")
            st.plotly_chart(fig_bar, use_container_width=True)

        # Top NON-EV Events (using actual data)
        st.subheader("Top NON-EV Events")
        top_events = nonev_collection.aggregate([
            {"$group": {"_id": "$event", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ])
        top_events_df = pd.DataFrame(list(top_events))
        if not top_events_df.empty:
            fig_pie = px.pie(top_events_df, values='count', names='_id', title='Top NON-EV Events Detected')
            st.plotly_chart(fig_pie, use_column_width=True)
        else:
            st.write("No NON-EV events data available.")

else:
    # Login or registration forms
    st.title("EV Detection System")

    menu = ["Login", "Register"]
    choice = st.selectbox("Login or Register", menu)

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

        new_username = st.text_input("New Username", placeholder="Enter your username")
        new_password = st.text_input("New Password", type="password", placeholder="Enter your password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")

        if st.button("Register"):
            if new_username and new_password and confirm_password:
                if new_password == confirm_password:
                    register_user(new_username, new_password)
                else:
                    st.error("Passwords do not match. Please try again.")
            else:
                st.error("Please fill out all fields.")

st.markdown("---")
st.write("For support, please contact the system administrator.")