import streamlit as st
def load_css():
    return """
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
        background-color: #4ade80;  /* Bright green color suitable for EV cars */
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] .sidebar-content {
        background-color: #4ade80;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: black;  /* Changed to black for better readability */
        font-size: 1.2rem;
        padding: 0.5rem 0;
        margin-left: 0.5rem;
    }
    [data-testid="stSidebar"] .stRadio > label {
        color: black;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        display: block;
    }
    [data-testid="stSidebar"] .stRadio > div {
        margin-left: 0;
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] {
        padding-top: 0.5rem;
    }
    [data-testid="stSidebar"] .stRadio [role="radio"] {
        align-items: center;
    }
    [data-testid="stSidebar"] .stRadio [role="radio"] > div:first-child {
        margin-right: 0.5rem;
    }
    [data-testid="stSidebar"] .stRadio [role="radio"] > div:last-child {
        font-size: 1.1rem;
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent;
        color: black;
        border: none;
        text-align: left;
        font-size: 1.2rem;
        padding: 0.5rem 1rem;
        width: 100%;
        transition: all 0.3s;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: rgba(0, 0, 0, 0.1);
    }

    /* Main Menu title style */
    .main-menu-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
        color: black;
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
    }
    .stButton > button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Input field styles */
    .stTextInput > div > div > input {
        border-radius: 5px;
        border: 1px solid #4CAF50;
    }

    /* Selectbox styles */
    .stSelectbox > div > div > select {
        border-radius: 5px;
        border: 1px solid #4CAF50;
    }

    /* Metric styles */
    .stMetric {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Chart styles */
    .stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* DataFrame styles */
    .dataframe {
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 0.9em;
        font-family: sans-serif;
        min-width: 400px;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
    }
    .dataframe thead tr {
        background-color: #4CAF50;
        color: #ffffff;
        text-align: left;
    }
    .dataframe th,
    .dataframe td {
        padding: 12px 15px;
    }
    .dataframe tbody tr {
        border-bottom: 1px solid #dddddd;
    }
    .dataframe tbody tr:nth-of-type(even) {
        background-color: #f3f3f3;
    }
    .dataframe tbody tr:last-of-type {
        border-bottom: 2px solid #4CAF50;
    }

    /* Custom div for decorative elements */
    .decoration-top {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 5px;
        background: linear-gradient(90deg, #4CAF50, #45a049);
        z-index: 1000;
    }
    .decoration-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 5px;
        background: linear-gradient(90deg, #45a049, #4CAF50);
        z-index: 1000;
    }

    /* Footer styles */
    .footer {
        position: fixed;
        left: 0;
        bottom: 5px;
        width: 100%;
        background-color: #f0f8ff;
        color: #4CAF50;
        text-align: center;
        padding: 10px 0;
        font-style: italic;
    }
    </style>

    <div class="decoration-top"></div>
    <div class="decoration-bottom"></div>
    """

def apply_styles():
    st.markdown(load_css(), unsafe_allow_html=True)