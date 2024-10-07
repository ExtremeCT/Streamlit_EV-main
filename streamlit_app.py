import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Set page config
st.set_page_config(page_title="EV Detection Dashboard", layout="wide")

# Custom CSS to change sidebar color and text color to black
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #4ade80;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: black;
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
</style>
""", unsafe_allow_html=True)

# Function to generate random data
def generate_data(start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date)
    return pd.DataFrame({
        'date': date_range,
        'value': np.random.randint(50, 150, size=len(date_range))
    })

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.button("Home")
st.sidebar.button("Messages")
st.sidebar.button("Favorites")
st.sidebar.button("Settings")
st.sidebar.button("Logout")
st.sidebar.text_input("Search...", "")

# Main content
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

# Generate data based on selected date range
df = generate_data(start_date, end_date)

# Display metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Detections", f"{df['value'].sum():,}")
with col2:
    st.metric("Average Daily Detections", f"{df['value'].mean():.2f}")

# EV Detections Trend
st.subheader("EV Detections Trend")
fig_trend = px.line(df, x='date', y='value', title='EV Detections Over Time')
fig_trend.update_traces(line_color="#4ade80")
st.plotly_chart(fig_trend, use_container_width=True)

# Monthly Comparison (if applicable)
if (end_date - start_date).days >= 30:
    st.subheader("Monthly Comparison")
    df_monthly = df.set_index('date').resample('M').sum().reset_index()
    fig_bar = px.bar(df_monthly, x='date', y='value', title='Monthly EV Detections')
    fig_bar.update_traces(marker_color="#4ade80")
    st.plotly_chart(fig_bar, use_container_width=True)

# Top EV Models (placeholder data)
st.subheader("Top EV Models")
top_models = pd.DataFrame({
    'model': ['Tesla Model 3', 'Nissan Leaf', 'Chevrolet Bolt', 'BMW i3'],
    'detections': np.random.randint(100, 1000, size=4)
})
fig_pie = px.pie(top_models, values='detections', names='model', title='Top EV Models Detected')
st.plotly_chart(fig_pie, use_container_width=True)

# ... (keep the existing custom CSS)
