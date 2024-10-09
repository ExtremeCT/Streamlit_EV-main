import streamlit as st
from pymongo import MongoClient
import bcrypt

# Connect to MongoDB (you might want to use environment variables for these credentials)
client = MongoClient("mongodb+srv://Extremenop:Nop24681036@cardb.ynz57.mongodb.net/?retryWrites=true&w=majority&appName=Cardb")
db = client['cardb']
users_collection = db['users']

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

def change_password(username, current_password, new_password):
    user = users_collection.find_one({"username": username})
    if user and verify_password(user['password'], current_password):
        hashed_new_password = hash_password(new_password)
        users_collection.update_one(
            {"username": username},
            {"$set": {"password": hashed_new_password}}
        )
        return True
    return False

def profile_page():
    st.title("User Profile")
    st.header("Change Password")

    if not st.session_state.get('logged_in', False):
        st.error("You must be logged in to access this page.")
        return

    username = st.session_state.get('username')
    st.write(f"Logged in as: {username}")

    current_password = st.text_input("Current Password", type="password")
    new_password = st.text_input("New Password", type="password")
    confirm_new_password = st.text_input("Confirm New Password", type="password")

    if st.button("Change Password"):
        if not current_password or not new_password or not confirm_new_password:
            st.error("Please fill out all fields.")
        elif new_password != confirm_new_password:
            st.error("New passwords do not match.")
        else:
            if change_password(username, current_password, new_password):
                st.success("Password changed successfully!")
            else:
                st.error("Failed to change password. Please check your current password.")

if __name__ == "__main__":
    profile_page()
