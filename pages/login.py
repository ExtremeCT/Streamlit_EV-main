import streamlit as st

# Set page config
st.set_page_config(page_title="EV Detection System Login", layout="centered")

# Custom CSS to style the page
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

# Login form
st.title("EV Detection System Dashboard Login")

username = st.text_input("Username", placeholder="Enter your username")
password = st.text_input("Password", type="password", placeholder="Enter your password")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Enter Dashboard"):
        if username and password:
            st.success("Login successful! Redirecting to dashboard...")
        else:
            st.error("Please enter both username and password.")

with col2:
    if st.button("Register"):
        st.info("Redirecting to registration page...")

with col3:
    st.markdown("[Forgot Password?](https://example.com)", unsafe_allow_html=True)

st.markdown("---")
st.write("For support, please contact the system administrator.")