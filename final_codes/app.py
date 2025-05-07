import streamlit as st
from student_page import register_student, student_login, student_dashboard, forgot_password
from admin_page import admin_login, admin_dashboard
from PIL import Image

# Set page config
st.set_page_config(page_title="Placement Cell", layout="wide")

# Inject CSS Styling
st.markdown("""
    <style>
        /* Add your CSS styling here */
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
                show_logo_and_title()  # Show logo and title on login page
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
