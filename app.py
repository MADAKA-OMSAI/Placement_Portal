import streamlit as st
from student_page import register_student, student_login, student_dashboard, forgot_password
from admin_page import admin_login, admin_dashboard
from PIL import Image

# Set page config
# st.set_page_config(page_title="Placement Cell", layout="wide")
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
import os
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import hashlib
import json
from datetime import datetime, date

# Set page configuration as the first command
st.set_page_config(page_title="Placement Cell", page_icon=":guardsman:", layout="wide")

# Load environment variables from .env file
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Admin credentials
ADMIN_CREDENTIALS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest()
}

# Function to load external CSS


# Your other Streamlit code continues here

st.markdown("""
    <style>
       
        }
        .stApp {
            background: linear-gradient(to bottom right, #f2f9ff, #e6f0ff);
            font-family: 'Segoe UI', 'Roboto', sans-serif;
            color: #002b5c;
            padding: 20px;
        }

        /* Custom Title */
        h1 {
            font-size: 2.5rem !important;
            text-align: center;
            color: #002b5c;
            font-weight: 700;
            margin-bottom: 1.5rem;
            text-shadow: 2px 2px 4px #cfe0f5;
        }

        /* Title Animation */
        @keyframes expandTitle {
            0% {
                width: 0;
            }
            50% {
                width: 50%;
            }
            100% {
                width: 100%;
            }
        }
        

        /* Animated Title */
        .animated-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #003366;
            text-align: center;
            overflow: hidden;
            display: inline-block;
            white-space: nowrap;
            animation: expandTitle 4s ease-in-out forwards;
            width: 0;
            border-right: 3px solid #002b5c;
            padding-right: 5px;
            display: inline-block;
        }

        /* Subheading */
        .stMarkdown h2 {
            text-align: center;
            font-size: 1.5rem;
            color: #003366;
            margin-bottom: 2rem;
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(to right, #0066cc, #0099ff);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            font-size: 1.1rem;
            font-weight: 600;
            box-shadow: 2px 4px 12px rgba(0,0,0,0.2);
            transition: all 0.3s ease-in-out;
        }

        .stButton>button:hover {
            background: linear-gradient(to right, #3399ff, #66ccff);
            transform: scale(1.03);
            box-shadow: 4px 6px 16px rgba(0,0,0,0.25);
        }

        /* Text input fields */
        .stTextInput>div>div>input {
            border: 1px solid #3399ff;
            padding: 0.6rem;
            border-radius: 8px;
        }

        /* Radio button styling */
        .stRadio>div>label {
            font-size: 1.3rem;
            font-weight: 600;
            color: #003366;
        }

        .stRadio>div>div>div>label {
            font-size: 1.2rem;
            font-weight: 500;
            color: #003366;
        }

        /* Padding */
        .stContainer {
            padding: 1.5rem;
        }

        /* Adjustments to the overall layout */
        .stRadio {
            margin-bottom: 20px;
        }

        /* Logo image styling */
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            padding: 10px 0;
            margin-bottom: 20px;
        }

        .logo-container img {
            border-radius: 50%;
            width: 80px; /* Reduced size of the logo */
            height: 80px;
            transition: transform 0.3s ease-in-out;
        }

        .logo-container img:hover {
            transform: scale(1.1); /* Animation on hover */
        }

        .logo-text {
            font-size: 1.3rem;
            font-weight: 700;
            color: #003366;
            margin-left: 10px;
            letter-spacing: 2px;
            text-transform: uppercase;
            display: inline-block;
        }

        /* Hide the title on non-home pages */
        .home-title {
            display: block;
        }

        .non-home-title {
            display: none;
        }

    </style>
""", unsafe_allow_html=True)

# Function to display the logo and title on all pages
def show_logo_and_title(is_home_page=False):
    # Load image locally using PIL
    image = Image.open(r"C:\Users\rgukt\Desktop\Placement Cell\logo_rgukt.png")
    # Display logo with RGUKT ONGOLE text
    st.image(image, width=80, use_column_width=False)  # Reduced size of logo
    st.markdown("""<div class="logo-text">RGUKT ONGOLE</div>""", unsafe_allow_html=True)

# Home function with title
def show_home():
    show_logo_and_title(is_home_page=True)  # Show logo and title on home page

    # Animated titles for both RGUKT ONGOLE and Placement Portal
    st.markdown('<div class="animated-title">RGUKT ONGOLE</div>', unsafe_allow_html=True)
    st.markdown('<div class="animated-title">Placement Portal</div>', unsafe_allow_html=True)

    st.markdown("## Choose your role")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧑‍🎓 Student", use_container_width=True):
            st.session_state.role = "student"
            st.session_state.view = "student_menu"
            st.session_state.student_view = "login"  # default student view
            st.rerun()

    with col2:
        if st.button("🧑‍💼 Admin", use_container_width=True):
            st.session_state.role = "admin"
            st.session_state.view = "admin_login"
            st.rerun()

# Main routing logic
def main():
    if "view" not in st.session_state:
        st.session_state.view = "home"

    if st.session_state.view == "home":
        show_home()

    elif st.session_state.view == "student_menu":
        if "student" in st.session_state:
            show_logo_and_title()  # Show logo and title on student menu page
            student_dashboard(st.session_state["student"])
        else:
            if "student_view" not in st.session_state:
                st.session_state.student_view = "login"

            # Student sub-pages
            if st.session_state.student_view == "register":
                show_logo_and_title()  # Show logo and title on registration page
                register_student()

            elif st.session_state.student_view == "forgot_password":
                show_logo_and_title()  # Show logo and title on forgot password page
                forgot_password()

            elif st.session_state.student_view == "login":
                # show_logo_and_title()  # Show logo and title on login page
                student_login()

                # Forgot Password Button
                if st.button("🔑 Forgot Password?"):
                    st.session_state.student_view = "forgot_password"
                    st.experimental_rerun()

                # New User Registration Button
                if st.button("🔑 New User? Register here"):
                    st.session_state.student_view = "register"  # Switch to the register view
                    st.experimental_rerun()

    elif st.session_state.view == "admin_login":
        show_logo_and_title()  # Show logo and title on admin login page
        admin_login()
        if st.session_state.get("admin_logged_in"):
            st.session_state.view = "admin_dashboard"
            st.rerun()

    elif st.session_state.view == "admin_dashboard":
        show_logo_and_title()  # Show logo and title on admin dashboard page
        admin_dashboard()


if __name__ == "__main__":
    main()
