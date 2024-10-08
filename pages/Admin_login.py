import streamlit as st
from pymongo import MongoClient
import bcrypt
import secrets
import logging
import gridfs
from bson import ObjectId
from PIL import Image
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page config
st.set_page_config(page_title="EV Detection System Admin", layout="wide")

# Connect to MongoDB (adjust connection string as needed)
client = MongoClient("mongodb+srv://Extremenop:Nop24681036@cardb.ynz57.mongodb.net/?retryWrites=true&w=majority&appName=Cardb")
db = client['cardb']
users_collection = db['users']
nonev_collection = db['nonev']
fs = gridfs.GridFS(db)

# Log debug information
logger.info(f"Connected to database: {db.name}")
logger.info(f"Collections in database: {db.list_collection_names()}")

# Custom CSS for styling
st.markdown("""
<style>
    .stTextInput>div>div>input {
        border: 1px solid black;
    }
    .stTextInput>div>div>input::placeholder {
        color: rgba(0,0,0,0.6);
    }
    .login-link {
        color: blue;
        text-decoration: underline;
        cursor: pointer;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

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

    existing_user = users_collection.find_one({"username": username})
    if existing_user:
        st.error("Username already exists. Please choose a different one.")
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
    st.title("EV Detection System Admin Management")
    st.write(f"Welcome, Admin {st.session_state.admin_username}!")

    # User Management Section
    st.header("User Management")

    # Get all users
    users = get_all_users()

    # Display users in a table
    if users:
        user_data = [{"Username": user.get("username", "N/A"), 
                      "User Type": user.get("user_type", "N/A")} for user in users]
        st.table(user_data)

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

    # Image Management Section
    st.header("Image Management")

    # Get all images
    images = get_all_images()

    # Display images in a table
    if images:
        image_data = [{"File ID": image.get("file_id", "N/A"), 
                       "Timestamp": image.get("timestamp", "N/A"),
                       "Event": image.get("event", "N/A")} for image in images]
        st.table(image_data)

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

    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.session_state.admin_username = None
        st.rerun()

else:
    # Admin Login and Registration
    st.title("EV Detection System Admin Portal")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.header("Admin Login")
        username = st.text_input("Admin Username", placeholder="Enter your admin username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

        if st.button("Login"):
            if username and password:
                admin_login(username, password)
            else:
                st.error("Please enter both username and password.")

    with tab2:
        st.header("Admin Registration")
        new_username = st.text_input("New Admin Username", placeholder="Enter new admin username")
        new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm new password")
        registration_key = st.text_input("Registration Key", type="password", placeholder="Enter registration key")

        if st.button("Register"):
            if new_username and new_password and confirm_password and registration_key:
                if new_password == confirm_password:
                    admin_register(new_username, new_password, registration_key)
                else:
                    st.error("Passwords do not match. Please try again.")
            else:
                st.error("Please fill out all fields.")

st.markdown("---")
st.write("For support, please contact the system administrator.")