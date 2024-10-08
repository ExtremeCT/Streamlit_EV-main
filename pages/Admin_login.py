import streamlit as st
from pymongo import MongoClient
import bcrypt

# Set page config
st.set_page_config(page_title="EV Detection System Admin Login", layout="centered")

# Connect to MongoDB (adjust connection string as needed)
client = MongoClient("mongodb+srv://Extremenop:Nop24681036@cardb.ynz57.mongodb.net/?retryWrites=true&w=majority&appName=Cardb")
db = client['cardb']
users_collection = db['users']

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
        st.success("Admin login successful! Redirecting to admin dashboard...")
        st.rerun()
    else:
        st.error("Invalid admin credentials.")

# Main App
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if st.session_state.admin_logged_in:
    # Admin Dashboard logic
    st.title("EV Detection System Admin Dashboard")
    st.write(f"Welcome, Admin {st.session_state.admin_username}!")

    # Add admin-specific functionality here
    if st.button("Manage Users"):
        st.subheader("User Management")
        # Add user management functionality

    if st.button("System Settings"):
        st.subheader("System Settings")
        # Add system settings functionality

    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.session_state.admin_username = None
        st.rerun()

else:
    # Admin Login form
    st.title("EV Detection System Admin Login")

    username = st.text_input("Admin Username", placeholder="Enter your admin username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")

    if st.button("Login"):
        if username and password:
            admin_login(username, password)
        else:
            st.error("Please enter both username and password.")

st.markdown("---")
st.write("For support, please contact the system administrator.")