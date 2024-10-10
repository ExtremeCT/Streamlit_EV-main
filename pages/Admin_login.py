import streamlit as st
from pymongo import MongoClient
import bcrypt
import secrets
import logging
import gridfs
from bson import ObjectId
from PIL import Image
from io import BytesIO
import re
import smtplib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(page_title="EV Detection System Admin", layout="wide", page_icon="🚗")

# Connect to MongoDB (adjust connection string as needed)
client = MongoClient("mongodb+srv://Extremenop:Nop24681036@cardb.ynz57.mongodb.net/?retryWrites=true&w=majority&appName=Cardb")
db = client['cardb']
users_collection = db['users']
nonev_collection = db['nonev']
fs = gridfs.GridFS(db)

# Log debug information
logger.info(f"Connected to database: {db.name}")
logger.info(f"Collections in database: {db.list_collection_names()}")

# Regex patterns
USERNAME_PATTERN = r'^[a-zA-Z0-9]{1,15}$'
PASSWORD_PATTERN = r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};:\'",.<>?]{1,20}$'

# Custom CSS for styling
st.markdown("""
<style>
    /* Main page style */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    body {
        color: #2a4858;
        background-color: #f7e8d3;
    }

    h1, h2, h3 {
        color: #4c8c71;
    }

    /* Sidebar styles */
    [data-testid="stSidebar"] {
        background-color: #68c3a3;
        padding-top: 2rem;
    }
    [data-testid="stSidebar"] .sidebar-content {
        background-color: #68c3a3;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #f7e8d3;
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
        background-color: rgba(247, 232, 211, 0.1) !important;
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
        color: #f7e8d3;
        background-color: #4c8c71;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
        text-align: left;
        display: flex;
        align-items: center;
        margin-top: 23px;
    }
    .stButton > button:hover {
        background-color: #68c3a3;
        color: #f7e8d3;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stTextInput > div > div > input {
        height: 48px;
    }
    .stButton > button > svg {
        margin-right: 0.5rem;
    }

    /* New styles for the sidebar menu */
    .sidebar-content {
        padding-top: 1rem;
    }
    .sidebar-content h1 {
        color: #f7e8d3;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sidebar-content .stButton > button {
        background-color: transparent;
        color: #f7e8d3;
        font-size: 1rem;
        font-weight: normal;
        text-align: left;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 0;
        transition: background-color 0.3s;
    }
    .sidebar-content .stButton > button:hover {
        background-color: rgba(247, 232, 211, 0.2);
    }
    .sidebar-content .stButton > button:focus {
        box-shadow: none;
    }
    /* Styles for option_menu */
    .css-1p0m6zy {
        padding-top: 1rem;
    }
    .css-1544g2n {
        padding: 0;
    }
    .css-uc76bn {
        font-size: 0.9rem;
    }
 </style>
""", unsafe_allow_html=True)

# Validation function
def validate_input(input_value, pattern):
    return re.match(pattern, input_value) is not None

def show_error(error_message):
    st.markdown(f'<p style="color: red; font-size: 14px;">{error_message}</p>', unsafe_allow_html=True)

# Hashing password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Verifying password
def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

# Admin login function
def admin_login(username, password):
    user = users_collection.find_one({"username": username, "user_type": "admin"})
    if user and verify_password(user['password'], password):
        st.session_state.admin_logged_in = True
        st.session_state.admin_username = username
        st.success("Admin login successful!")
        st.rerun()
    else:
        st.error("Invalid admin credentials.")

# Admin registration function
def admin_register(username, password, registration_key):
    if registration_key != st.secrets["admin_registration_key"]:
        st.error("Invalid registration key.")
        return False

    existing_user = users_collection.find_one({"$or": [{"username": username}]})
    if existing_user:
        st.error("Username already exists. Please choose different ones.")
        return False

    hashed_password = hash_password(password)
    new_admin = {
        "username": username,
        "password": hashed_password,
        "user_type": "admin"
    }
    result = users_collection.insert_one(new_admin)
    if result.inserted_id:
        st.success("Admin account created successfully. You can now log in.")
        return True
    else:
        st.error("Failed to create admin account. Please try again.")
        return False

# Function to get all users
def get_all_users():
    try:
        all_users = list(users_collection.find({"user_type": {"$ne": "admin"}}))
        logger.info(f"Found {len(all_users)} users")
        return all_users
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return []

# Function to delete user
def delete_user(username):
    try:
        result = users_collection.delete_one({"username": username, "user_type": {"$ne": "admin"}})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return False

# Function to get all image files
def get_all_images():
    try:
        all_images = list(nonev_collection.find())
        logger.info(f"Found {len(all_images)} images")
        return all_images
    except Exception as e:
        logger.error(f"Error fetching images: {str(e)}")
        return []

# Function to delete image file
def delete_image(file_id):
    try:
        # Delete the file from GridFS
        fs.delete(ObjectId(file_id))
        # Delete the metadata from nonev collection
        result = nonev_collection.delete_one({"file_id": file_id})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting image: {str(e)}")
        return False

# Function to get image data
def get_image_data(file_id):
    try:
        return fs.get(ObjectId(file_id)).read()
    except Exception as e:
        logger.error(f"Error retrieving image data: {str(e)}")
        return None

# Main App
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if st.session_state.admin_logged_in:
    # Admin Dashboard
    st.title("🚗 EV Detection System Admin Dashboard")
    st.write(f"Welcome, Admin {st.session_state.admin_username}!")

    # Sidebar
    with st.sidebar:
        st.title("🚗 EV Detection Admin")
        selected = st.radio(
            "Main Menu",
            ["User Management", "Image Management"],
            format_func=lambda x: f"{'👥' if x == 'User Management' else '🖼️'} {x}"
        )

        st.sidebar.markdown("---")  # Add a separator line
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.session_state.admin_username = None

    if selected == "User Management":
        st.header("👥 User Management")

        # Get all users
        users = get_all_users()

        # Display users in a table
        if users:
            user_data = [{"Username": user.get("username", "N/A"), 
                          "User Type": user.get("user_type", "N/A"),
                          "Email": user.get("email", "N/A")} for user in users]
            st.dataframe(user_data)

            # User deletion
            st.subheader("Delete User")
            username_to_delete = st.selectbox("Select user to delete", 
                                              [user["username"] for user in users])
            if st.button("Delete Selected User"):
                if delete_user(username_to_delete):
                    st.success(f"User {username_to_delete} has been deleted.")
                    st.rerun()
                else:
                    st.error("Failed to delete user. Please try again.")
        else:
            st.info("No users found in the system.")

    elif selected == "Image Management":
        st.header("🖼️ Image Management")

        # Get all images
        images = get_all_images()

        # Display images in a table
        if images:
            image_data = [{"File ID": image.get("file_id", "N/A"), 
                           "Timestamp": image.get("timestamp", "N/A"),
                           "Event": image.get("event", "N/A")} for image in images]
            st.dataframe(image_data)

            # Image deletion
            st.subheader("Delete Image")
            file_id_to_delete = st.selectbox("Select image to delete", 
                                             [image["file_id"] for image in images])
            
            # Display selected image
            if st.button("Show Selected Image"):
                image_data = get_image_data(file_id_to_delete)
                if image_data:
                    st.image(Image.open(BytesIO(image_data)), caption=f"Image ID: {file_id_to_delete}", use_column_width=True)
                else:
                    st.error("Failed to load image. The file might be corrupted or missing.")

            if st.button("Delete Selected Image"):
                if delete_image(file_id_to_delete):
                    st.success(f"Image with File ID {file_id_to_delete} has been deleted.")
                    st.rerun()
                else:
                    st.error("Failed to delete image. Please try again.")
        else:
            st.info("No images found in the system.")

else:
    # Admin Login and Registration
    st.title("🚗 EV Detection System Admin Portal")

    tab1, tab2 = st.tabs(["🔐 Admin Login", "📝 Admin Registration"])

    with tab1:
        st.header("Admin Login")
        username = st.text_input("Admin Username", placeholder="Enter your admin username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

        if st.button("Login", key="login_button"):
            if username and password:
                admin_login(username, password)
            else:
                st.error("Please enter both username and password.")

    with tab2:
        st.header("Admin Registration")
        new_username = st.text_input("New Admin Username", placeholder="Enter new admin username")
        if new_username and not validate_input(new_username, USERNAME_PATTERN):
            show_error("Username must be 1-15 characters long and contain only letters and numbers.")

        new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
        if new_password and not validate_input(new_password, PASSWORD_PATTERN):
            show_error("Password must be 1-20 characters long and can contain letters, numbers, and special characters.")

        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")
        if confirm_password and new_password != confirm_password:
            show_error("Passwords do not match.")

        registration_key = st.text_input("Registration Key", type="password", placeholder="Enter registration key")

        if st.button("Register", key="register_button"):
            if new_username and new_password and confirm_password and registration_key:
                if validate_input(new_username, USERNAME_PATTERN) and validate_input(new_password, PASSWORD_PATTERN):
                    if new_password == confirm_password:
                        admin_register(new_username, new_password, registration_key)
                    else:
                        st.error("Passwords do not match. Please try again.")
                else:
                    st.error("Please make sure all fields are filled correctly.")
            else:
                st.error("Please fill out all fields.")

st.markdown("---")
st.write("For support, please contact the system administrator.")

# Add some decorative elements
st.markdown("""
<div style="text-align: center; margin-top: 50px;">
    <h3>🌿 Driving towards a greener future 🌿</h3>
    <p style="font-style: italic;">Empowering sustainable transportation through advanced EV detection.</p>
</div>
""", unsafe_allow_html=True)